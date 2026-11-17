#!/usr/bin/env python3
"""fork-radar · 抓取自己名下全部公开 fork，并记录上游与同步状态。

输出 data/forks.json，给 scripts/build_readme.py 渲染 README 用。
只读公开仓库，因此 Actions 里用默认的 GITHUB_TOKEN 就能跑，不需要额外配 PAT。

凭据：环境变量 GITHUB_TOKEN / GH_TOKEN，或 --token-file 指定的文件（整份内容即 token）。
只读权限即可，GitHub Actions 自动注入的 GITHUB_TOKEN 够用。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_ROOT = "https://api.github.com"
USER_AGENT = "fork-radar (+https://github.com/yehuoshun/fork-radar)"
RETRIES = 3
REPO_ROOT = Path(__file__).resolve().parent.parent


class ApiError(RuntimeError):
    def __init__(self, path: str, code: int, message: str) -> None:
        super().__init__(f"{path} -> HTTP {code}: {message}")
        self.path = path
        self.code = code
        self.message = message


class Client:
    """极简 GitHub REST 客户端，只用标准库。"""

    def __init__(self, token: str) -> None:
        self.token = token
        self.calls = 0

    def _headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        return headers

    def get(self, path: str):
        url = path if path.startswith("http") else API_ROOT + path
        last = None
        for attempt in range(RETRIES):
            request = urllib.request.Request(url, headers=self._headers())
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    self.calls += 1
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                self.calls += 1
                body = exc.read().decode("utf-8", "replace").replace("\n", " ")[:300]
                last = ApiError(path, exc.code, body)
                busy = exc.code >= 500 or (exc.code in (403, 429) and "rate limit" in body.lower())
                if busy and attempt + 1 < RETRIES:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise last from None
            except urllib.error.URLError as exc:
                self.calls += 1
                last = ApiError(path, 0, str(exc.reason))
                if attempt + 1 < RETRIES:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise last from None
        raise last if last else ApiError(path, 0, "unreachable")


def read_token(token_file):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and token.strip():
        return token.strip()
    if token_file:
        path = Path(token_file).expanduser()
        if not path.is_absolute():
            path = REPO_ROOT / path
        if not path.exists():
            raise SystemExit("找不到 token 文件：" + str(path))
        return path.read_text(encoding="utf-8").strip()
    raise SystemExit("缺少凭据：设置 GITHUB_TOKEN，或用 --token-file 指定文件")


def list_repos(client, owner):
    """只读公开仓库列表：Actions 里注入的 GITHUB_TOKEN 读得了，也永远不会把私有仓库漏进 README。"""
    repos = []
    page = 1
    while True:
        path = f"/users/{owner}/repos?type=owner&per_page=100&sort=pushed&page={page}"
        batch = client.get(path)
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def sync_state(client, detail):
    """比对 fork 与上游的分支差异：base=上游分支，head=我的分支。"""
    parent = detail.get("parent") or {}
    owner = (detail.get("owner") or {}).get("login") or detail.get("full_name", "/").split("/")[0]
    head_branch = detail.get("default_branch") or "main"
    base_branch = parent.get("default_branch") or "main"
    path = "/repos/" + str(parent.get("full_name")) + "/compare/" + base_branch + "..." + owner + ":" + head_branch
    try:
        compare = client.get(path)
    except ApiError as exc:
        return {
            "state": "unknown",
            "ahead_by": None,
            "behind_by": None,
            "base_branch": base_branch,
            "head_branch": head_branch,
            "error": str(exc),
        }
    mapping = {"identical": "synced", "ahead": "ahead", "behind": "behind", "diverged": "diverged"}
    return {
        "state": mapping.get(compare.get("status") or "", "unknown"),
        "ahead_by": compare.get("ahead_by"),
        "behind_by": compare.get("behind_by"),
        "total_commits": compare.get("total_commits"),
        "base_branch": base_branch,
        "head_branch": head_branch,
    }


def upstream_of(parent):
    return {
        "full_name": parent.get("full_name"),
        "html_url": parent.get("html_url"),
        "description": parent.get("description"),
        "language": parent.get("language"),
        "stars": parent.get("stargazers_count"),
        "archived": bool(parent.get("archived")),
        "default_branch": parent.get("default_branch"),
        "pushed_at": parent.get("pushed_at"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="抓取公开 fork 及其上游同步状态")
    parser.add_argument("--token-file", help="token 文件路径（不给就读 GITHUB_TOKEN 环境变量）")
    parser.add_argument("--owner", help="账号名，默认取 GITHUB_REPOSITORY_OWNER 或 token 持有者")
    parser.add_argument("--out", default=str(REPO_ROOT / "data" / "forks.json"), help="输出 JSON 路径")
    args = parser.parse_args(argv)

    client = Client(read_token(args.token_file))
    owner = args.owner or os.environ.get("GITHUB_REPOSITORY_OWNER") or client.get("/user").get("login")
    print("[fork-radar] 账号 " + str(owner) + "，开始扫描……", file=sys.stderr)

    repos = list_repos(client, owner)
    forks = [item for item in repos if item.get("fork") and not item.get("private")]
    forks.sort(key=lambda item: item["full_name"].lower())
    print(
        "[fork-radar] 仓库 " + str(len(repos)) + " 个，其中公开 fork " + str(len(forks)) + " 个",
        file=sys.stderr,
    )

    entries = []
    errors = []
    for repo in forks:
        upstream = None
        sync = {"state": "unknown", "ahead_by": None, "behind_by": None}
        try:
            detail = client.get("/repos/" + repo["full_name"])
            parent = detail.get("parent")
            if parent:
                upstream = upstream_of(parent)
                sync = sync_state(client, detail)
            else:
                sync = {"state": "upstream-missing", "ahead_by": None, "behind_by": None}
        except ApiError as exc:
            blocked = exc.code == 403 and "blocked" in (exc.message or "").lower()
            snapshot = "GitHub 已屏蔽该仓库（Repository access blocked / ToS）" if blocked else str(exc)
            sync = {
                "state": "blocked" if blocked else "unknown",
                "ahead_by": None,
                "behind_by": None,
                "error": snapshot,
            }
            errors.append({"repo": repo["full_name"], "error": snapshot})
            print("[fork-radar] 抓取失败 " + repo["full_name"] + ": " + snapshot, file=sys.stderr)

        entries.append(
            {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "html_url": repo["html_url"],
                "description": repo.get("description"),
                "language": repo.get("language"),
                "topics": repo.get("topics") or [],
                "stars": repo.get("stargazers_count"),
                "archived": bool(repo.get("archived")),
                "default_branch": repo.get("default_branch"),
                "created_at": repo.get("created_at"),
                "pushed_at": repo.get("pushed_at"),
                "upstream": upstream,
                "sync": sync,
            }
        )
        print("  - " + repo["name"] + " → " + str(sync.get("state")), file=sys.stderr)

    payload = {
        "owner": owner,
        "source": "https://github.com/" + str(owner),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "api_calls": client.calls,
        "total_repos": len(repos),
        "fork_count": len(entries),
        "forks": entries,
        "errors": errors,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[fork-radar] 写入 " + out.name + "：" + str(len(entries)) + " 个 fork，"
        + str(client.calls) + " 次 API 调用",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
