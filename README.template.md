<div align="center">

# 📡 fork-radar

**我 fork 过的开源项目，全摊在一页里。**

我只翻 GitHub 第一页 —— 后面的仓库基本不看，fork 也跟着沉底。
这张表把它们捞起来，标出哪些落后上游、哪些我动过手，每天自动刷新。

{{TOTAL_LINE}}

[![update](https://github.com/yehuoshun/fork-radar/actions/workflows/update.yml/badge.svg)](https://github.com/yehuoshun/fork-radar/actions/workflows/update.yml)

数据快照：{{GENERATED_AT}}

</div>

> 这张 README 由脚本生成，**别手改**：改文案动 `README.template.md`，改分组和备注动 `curation.json`。

## 怎么读

| 状态 | 含义 |
| --- | --- |
| ✅ 同步 | 和上游完全一致 |
| ⬇️ 落后 N | 上游有 N 个新提交我没跟上 |
| ✏️ 领先 N | 我在 fork 上改出了上游没有的 N 个提交 |
| ✂️ +A / −B | 两边都动过：我多 A 个提交，上游多 B 个 |
| 🗄️ 上游已归档 | 上游作者归档了仓库，不用再等更新 |
| ⛔ 上游已删 | 上游仓库消失（删库或封禁），fork 成了唯一副本 |
| ❔ 未知 | 分支名或接口异常，算不出差异 |

「我的改动」列 = 相对上游多出来的提交数，`—` 表示我没碰过。

## 总览

{{OVERVIEW}}

## 分组

{{GROUPS}}

## 值得回头看

{{WATCHLIST}}

---

## 这套东西怎么用

- **新增 fork 不用管**：只要 fork 了公开仓库，第二天自动出现在表里。想立刻看到就跑 `Actions → update → Run workflow`。
- **分组放错了**：改 `curation.json` 里那一条的 `group`，push 后自动重排。
- **想给自己也做一份**：fork 本仓库 → 改 `curation.json` → 删掉 `data/forks.json` → 跑一次 workflow。脚本只用 Python 标准库 + `GITHUB_TOKEN`，没有外部依赖。

## 本地跑

```bash
python scripts/fetch_forks.py --token-file ../../config/github_token.txt   # 抓数据
python scripts/build_readme.py                                             # 重算 README
python scripts/build_readme.py --check                                     # 只校验是否过期
```

`fetch_forks.py` 也认 `GITHUB_TOKEN` / `GH_TOKEN` 环境变量。每次跑约 `2 + 2 × fork 数` 个请求，5000/小时的额度绰绰有余。

## License

MIT，见 [LICENSE](LICENSE)。
