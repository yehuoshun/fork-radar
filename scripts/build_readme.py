#!/usr/bin/env python3
"""fork-radar · 把 data/forks.json 与 curation.json 渲染成 README.md。

    python scripts/build_readme.py            # 生成 README.md
    python scripts/build_readme.py --check    # 只校验 README.md 是否与数据一致（CI 用）
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "forks.json"
CURATION_FILE = REPO_ROOT / "curation.json"
TEMPLATE_FILE = REPO_ROOT / "README.template.md"
README_FILE = REPO_ROOT / "README.md"

CST = timezone(timedelta(hours=8))
SLEEPY_DAYS = 365
NOTE_LIMIT = 78
DESC_LIMIT = 68


def fmt_stars(value):
    if not value:
        return "0"
    if value >= 1000:
        text = f"{value / 1000:.1f}"
        return text[:-2] + "k" if text.endswith(".0") else text + "k"
    return str(value)


def one_line(text, limit=None):
    text = " ".join(str(text).split()).replace("|", "／")
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def localize(value):
    moment = parse_time(value)
    if not moment:
        return "未知"
    return moment.astimezone(CST).strftime("%Y-%m-%d %H:%M") + " (UTC+8)"


def all_groups(curation):
    groups = [dict(item) for item in (curation.get("groups") or [])]
    if not any(item.get("id") == "other" for item in groups):
        groups.append({"id": "other", "title": "📦 待归类", "desc": ""})
    return groups


def config_of(fork, curation):
    return (curation.get("repos") or {}).get(fork["name"]) or {}


def group_of(fork, curation):
    explicit = config_of(fork, curation).get("group")
    if explicit:
        return explicit
    upstream = fork.get("upstream") or {}
    haystack = " ".join(
        [
            fork.get("name") or "",
            fork.get("description") or "",
            upstream.get("full_name") or "",
            " ".join(fork.get("topics") or []),
        ]
    ).lower()
    for rule in curation.get("rules") or []:
        group = rule.get("group")
        keywords = [str(word).lower() for word in (rule.get("keywords") or [])]
        if group and any(word in haystack for word in keywords):
            return group
    return "other"


def sort_key(fork, curation):
    upstream = fork.get("upstream") or {}
    sync = fork.get("sync") or {}
    pinned = 1 if config_of(fork, curation).get("pinned") else 0
    changed = 1 if (sync.get("ahead_by") or 0) > 0 else 0
    return (-pinned, -changed, -(upstream.get("stars") or 0), fork["name"].lower())


def status_cell(fork):
    upstream = fork.get("upstream")
    sync = fork.get("sync") or {}
    state = sync.get("state") or "unknown"
    if state == "blocked":
        badge = "🚫 仓库已屏蔽"
    elif not upstream or state == "upstream-missing":
        badge = "⛔ 上游已删"
    elif upstream.get("archived"):
        badge = "🗄️ 上游已归档"
    elif state == "synced":
        badge = "✅ 同步"
    elif state == "behind":
        badge = f"⬇️ 落后 {sync.get('behind_by') or 0}"
    elif state == "ahead":
        badge = f"✏️ 领先 {sync.get('ahead_by') or 0}"
    elif state == "diverged":
        badge = f"✂️ +{sync.get('ahead_by') or 0} / −{sync.get('behind_by') or 0}"
    else:
        badge = "❔ 未知"
    if fork.get("archived"):
        badge = badge + " · 📦 我已归档"
    return badge


def note_of(fork, curation):
    note = config_of(fork, curation).get("note")
    if note:
        return one_line(note, NOTE_LIMIT)
    upstream = fork.get("upstream") or {}
    for candidate in (upstream.get("description"), fork.get("description")):
        if candidate:
            return one_line(candidate, DESC_LIMIT)
    return "—"


def table_row(fork, curation):
    upstream = fork.get("upstream") or {}
    if upstream.get("full_name"):
        upstream_cell = (
            "[" + str(upstream["full_name"]) + "](" + str(upstream.get("html_url")) + ") ⭐"
            + fmt_stars(upstream.get("stars"))
        )
    else:
        upstream_cell = "—"
    ahead = (fork.get("sync") or {}).get("ahead_by") or 0
    pin = "📌 " if config_of(fork, curation).get("pinned") else ""
    cells = [
        pin + "[" + fork["name"] + "](" + fork["html_url"] + ")",
        upstream_cell,
        fork.get("language") or upstream.get("language") or "—",
        f"+{ahead}" if ahead > 0 else "—",
        status_cell(fork),
        note_of(fork, curation),
    ]
    return "| " + " | ".join(cells) + " |"


def buckets_of(forks, curation):
    buckets = {}
    for fork in forks:
        buckets.setdefault(group_of(fork, curation), []).append(fork)
    return buckets


def ordered_groups(curation, buckets):
    groups = all_groups(curation)
    declared = {item["id"] for item in groups}
    for key in buckets:
        if key not in declared:
            groups.append({"id": key, "title": key, "desc": ""})
    return groups


def render_overview(forks, curation):
    buckets = buckets_of(forks, curation)
    lines = ["| 分组 | 数量 | 其中我改过 |", "| --- | --- | --- |"]
    for group in ordered_groups(curation, buckets):
        members = buckets.get(group["id"]) or []
        if not members:
            continue
        changed = sum(1 for item in members if ((item.get("sync") or {}).get("ahead_by") or 0) > 0)
        lines.append("| " + str(group.get("title") or group["id"]) + f" | {len(members)} | " + (str(changed) if changed else "—") + " |")
    total_changed = sum(1 for item in forks if ((item.get("sync") or {}).get("ahead_by") or 0) > 0)
    lines.append(f"| **合计** | **{len(forks)}** | " + (f"**{total_changed}**" if total_changed else "—") + " |")
    return "\n".join(lines)


def render_groups(forks, curation):
    buckets = buckets_of(forks, curation)
    blocks = []
    for group in ordered_groups(curation, buckets):
        members = buckets.get(group["id"]) or []
        if not members:
            continue
        members = sorted(members, key=lambda item: sort_key(item, curation))
        block = ["### " + str(group.get("title") or group["id"]), ""]
        if group.get("desc"):
            block.extend([one_line(group["desc"]), ""])
        block.extend(
            [
                "| 仓库 | 上游 | 语言 | 我的改动 | 状态 | 说明 |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        block.extend(table_row(item, curation) for item in members)
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def render_watchlist(forks, generated_at, errors=None):
    now = parse_time(generated_at) or datetime.now(timezone.utc)
    behind, changed, dead, sleepy = [], [], [], []
    for fork in forks:
        sync = fork.get("sync") or {}
        upstream = fork.get("upstream")
        if (sync.get("ahead_by") or 0) > 0:
            changed.append(fork)
        if sync.get("state") == "behind":
            behind.append(fork)
        if not upstream or upstream.get("archived") or sync.get("state") == "blocked":
            dead.append(fork)
            continue
        pushed = parse_time(fork.get("pushed_at"))
        if pushed and (now - pushed) > timedelta(days=SLEEPY_DAYS):
            sleepy.append(fork)

    sections = []
    if behind:
        behind.sort(key=lambda item: -((item.get("sync") or {}).get("behind_by") or 0))
        lines = [f"### ⬇️ 该同步了（{len(behind)}）", ""]
        for fork in behind:
            count = (fork.get("sync") or {}).get("behind_by") or 0
            lines.append(f"- **[{fork['name']}]({fork['html_url']})** — 落后上游 {count} 个提交")
        sections.append("\n".join(lines))
    if changed:
        lines = [f"### ✏️ 有本地改动（{len(changed)}）", "", "同步上游前先看一眼，别把自己的提交盖掉。", ""]
        for fork in changed:
            ahead = (fork.get("sync") or {}).get("ahead_by") or 0
            lines.append(f"- **[{fork['name']}]({fork['html_url']})** — 我多出 {ahead} 个提交")
        sections.append("\n".join(lines))
    if dead:
        lines = [f"### 🗄️ 上游已归档 / 已删（{len(dead)}）", ""]
        for fork in dead:
            sync = fork.get("sync") or {}
            if sync.get("state") == "blocked":
                text = "GitHub 已屏蔽这个仓库（ToS），页面上打不开"
            elif (fork.get("upstream") or {}).get("archived"):
                text = "上游已归档"
            else:
                text = "上游仓库已消失"
            lines.append(f"- **[{fork['name']}]({fork['html_url']})** — {text}")
        sections.append("\n".join(lines))
    if sleepy:
        lines = [f"### 😴 一年没动过（{len(sleepy)}）", ""]
        for fork in sorted(sleepy, key=lambda item: str(item.get("pushed_at") or "")):
            stamp = localize(fork.get("pushed_at")).split(" ")[0]
            lines.append(f"- **[{fork['name']}]({fork['html_url']})** — 最后一次推送 {stamp}")
        sections.append("\n".join(lines))
    if errors:
        lines = [f"### ⚠️ 这次没抓到（{len(errors)}）", ""]
        for item in errors:
            lines.append("- " + str(item.get("repo")) + " — " + one_line(item.get("error"), 90))
        sections.append("\n".join(lines))
    return "\n\n".join(sections) if sections else "_暂时没有需要回头看的。_"


def render(data, curation):
    forks = data.get("forks") or []
    total = len(forks)
    changed = sum(1 for item in forks if ((item.get("sync") or {}).get("ahead_by") or 0) > 0)
    behind = sum(1 for item in forks if (item.get("sync") or {}).get("state") == "behind")
    dead = sum(
        1
        for item in forks
        if not item.get("upstream")
        or (item.get("upstream") or {}).get("archived")
        or (item.get("sync") or {}).get("state") == "blocked"
    )
    total_line = (
        f"**{total}** 个 fork · **{changed}** 个我改过 · "
        f"**{behind}** 个落后上游 · **{dead}** 个上游已失效"
    )
    replacements = {
        "{{TOTAL_LINE}}": total_line,
        "{{GENERATED_AT}}": localize(data.get("generated_at")),
        "{{OVERVIEW}}": render_overview(forks, curation),
        "{{GROUPS}}": render_groups(forks, curation),
        "{{WATCHLIST}}": render_watchlist(forks, data.get("generated_at"), data.get("errors")),
    }
    text = TEMPLATE_FILE.read_text(encoding="utf-8")
    for key, value in replacements.items():
        if key not in text:
            print("[fork-radar] 警告：README.template.md 里缺少占位符 " + key, file=sys.stderr)
        text = text.replace(key, value)
    if not text.endswith("\n"):
        text = text + "\n"
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description="渲染 README.md")
    parser.add_argument("--check", action="store_true", help="只校验 README.md 是否最新，不写入")
    args = parser.parse_args(argv)

    if not DATA_FILE.exists():
        raise SystemExit("缺少 data/forks.json，先跑 python scripts/fetch_forks.py")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    curation = json.loads(CURATION_FILE.read_text(encoding="utf-8")) if CURATION_FILE.exists() else {}
    text = render(data, curation)

    if args.check:
        current = README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else ""
        if current == text:
            print("[fork-radar] README.md 是最新的")
            return 0
        print("[fork-radar] README.md 已过期，跑一次 python scripts/build_readme.py", file=sys.stderr)
        return 1

    README_FILE.write_text(text, encoding="utf-8", newline="\n")
    print(f"[fork-radar] 已写入 README.md（{len(data.get('forks') or [])} 个 fork）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
