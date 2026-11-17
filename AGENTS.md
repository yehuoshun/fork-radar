# fork-radar 项目约定

- `README.md` 是生成物，**别手改**：文案改 `README.template.md`，分组与备注改 `curation.json`，逻辑改 `scripts/`。
- `data/forks.json` 是抓取快照，**要一起提交**：README 靠它离线复现，Actions 靠它算差异。
- 改完必须跑 `python scripts/fetch_forks.py` + `python scripts/build_readme.py`，并让 `--check` 通过。
- 只用 Python 标准库，不引入第三方依赖。
- 提交信息：`范围: 改了什么(为什么)`，范围用 `scripts` / `docs` / `data` / `chore`；一修改一 push。
