<div align="center">

# 📡 fork-radar

**我 fork 过的开源项目，全摊在一页里。**

我只翻 GitHub 第一页 —— 后面的仓库基本不看，fork 也跟着沉底。
这张表把它们捞起来，标出哪些落后上游、哪些我动过手，每天自动刷新。

**7** 个 fork · **2** 个我改过 · **0** 个落后上游 · **1** 个上游已失效

[![update](https://github.com/yehuoshun/fork-radar/actions/workflows/update.yml/badge.svg)](https://github.com/yehuoshun/fork-radar/actions/workflows/update.yml)

数据快照：2026-11-22 13:15 (UTC+8)

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

| 分组 | 数量 | 其中我改过 |
| --- | --- | --- |
| 🧩 MCP / AI 工具链 | 2 | — |
| ☕ Java 生态 | 2 | — |
| 🎮 游戏工具 / MOD / 资源 | 3 | 2 |
| **合计** | **7** | **2** |

## 分组

### 🧩 MCP / AI 工具链

把模型接到真实工具上的那一类，索引仓库居多。

| 仓库 | 上游 | 语言 | 我的改动 | 状态 | 说明 |
| --- | --- | --- | --- | --- | --- |
| [awesome-mcp-servers](https://github.com/yehuoshun/awesome-mcp-servers) | [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) ⭐98.4k | — | — | ✅ 同步 | MCP 服务器总表（punkpeye），我这份是纯副本，看内容请回上游 |
| [awesome-china-mcp](https://github.com/yehuoshun/awesome-china-mcp) | [zackchewa/awesome-china-mcp](https://github.com/zackchewa/awesome-china-mcp) ⭐179 | — | — | ✅ 同步 | 国内 App 的 MCP 服务索引 |

### ☕ Java 生态

MyBatis 周边与中间件扩展。

| 仓库 | 上游 | 语言 | 我的改动 | 状态 | 说明 |
| --- | --- | --- | --- | --- | --- |
| [mybatis-plus-join](https://github.com/yehuoshun/mybatis-plus-join) | [bobo667/mybatis-plus-join](https://github.com/bobo667/mybatis-plus-join) ⭐147 | Java | — | ✅ 同步 | MyBatis-Plus 多表联查插件，完全照 MP 的用法写 |
| [MongoPlus](https://github.com/yehuoshun/MongoPlus) | [anwenmp/MongoPlus](https://github.com/anwenmp/MongoPlus) ⭐75 | Java | — | ✅ 同步 | 把 MyBatis-Plus 的写法搬到 MongoDB 上；fork 过来只为跟踪上游 |

### 🎮 游戏工具 / MOD / 资源

游戏增强、解包资源、自动签到这类小工具。

| 仓库 | 上游 | 语言 | 我的改动 | 状态 | 说明 |
| --- | --- | --- | --- | --- | --- |
| [rebirth-hoarder-mod](https://github.com/yehuoshun/rebirth-hoarder-mod) | [thus1235/rebirth-hoarder-mod](https://github.com/thus1235/rebirth-hoarder-mod) ⭐5 | C# | +5 | ✏️ 领先 5 | 《末世：我有一辆房车》3.5 单机增强：F8 修改面板 + 存档修改器；我在这儿留了本地提交 |
| [1999GameResource](https://github.com/yehuoshun/1999GameResource) | [HanaHye/Reverse1999Resource](https://github.com/HanaHye/Reverse1999Resource) ⭐0 | — | +1 | ✂️ +1 / −1 · 📦 我已归档 | 《重返未来1999》解包资源，2023 年的留档 |
| [genshin-helper](https://github.com/yehuoshun/genshin-helper) | — | — | — | 🚫 仓库已屏蔽 | 原神米游社自动签到 |

## 值得回头看

### ✏️ 有本地改动（2）

同步上游前先看一眼，别把自己的提交盖掉。

- **[1999GameResource](https://github.com/yehuoshun/1999GameResource)** — 我多出 1 个提交
- **[rebirth-hoarder-mod](https://github.com/yehuoshun/rebirth-hoarder-mod)** — 我多出 5 个提交

### 🗄️ 上游已归档 / 已删（1）

- **[genshin-helper](https://github.com/yehuoshun/genshin-helper)** — GitHub 已屏蔽这个仓库（ToS），页面上打不开

### 😴 一年没动过（1）

- **[1999GameResource](https://github.com/yehuoshun/1999GameResource)** — 最后一次推送 2023-07-07

### ⚠️ 这次没抓到（1）

- yehuoshun/genshin-helper — GitHub 已屏蔽该仓库（Repository access blocked / ToS）

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
