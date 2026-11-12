---
name: UNTSSearcher
description: 独立检索联合国条约集（UNTS/UNTC）秘书长保存的 MTDSG 标题目录，查找条约标题、登记页和详情页；明确区分标题目录与完整 UNTS 登记库。
---

# UNTSSearcher

> **`<skill-dir>`** = 本 SKILL.md 所在目录。核心脚本为 `<skill-dir>/scripts/unts_search.py`；Windows 用 `<skill-dir>/run.ps1`，macOS/Linux 用 `<skill-dir>/run.sh`。部署与排错见 [README.md](README.md)。

这个 skill 只做 `treaties.un.org` 一个站点，扫描 UNTC 的 **MTDSG 标题目录**：

- 从 `ParticipationStatus.aspx` 发现各章 `Treaties.aspx` 页面；
- 在页面中提取 `ViewDetails.aspx` 条约记录；
- 按标题关键词返回条约名称和详情页链接；
- `fetch` 可读取详情/状态页，或下载 PDF 提取文本。

## 命令

```powershell
& '<skill-dir>/run.ps1' search "Charter" --max-pages 5 --limit 10 --out './unts.json'

# UNTS Online Title/Keyword Search（全部 UNTS 登记，不只 MTDSG 目录）
& '<skill-dir>/run.ps1' search "genocide" --mode title --match phrase --limit 10

& '<skill-dir>/run.ps1' fetch 'https://treaties.un.org/Pages/ViewDetails.aspx?...' --out './treaty.json' --text-out './treaty.txt'
& '<skill-dir>/run.ps1' doctor
```

通用参数：`--out`、`--cache`、`--cache-ttl`、`--offline`、`--timeout`。`search` 另有 `--limit`、`--offset`、`--max-pages`；`fetch` 另有 `--text-out`、`--pdf-out`、`--max-mb`。

## 结果边界

- 这是 **MTDSG 标题目录**，不是完整 UNTS 登记库；它只覆盖秘书长保存的多边条约目录。双边条约、未列入 MTDSG 的登记和完整 UNTS Advanced Search 仍属人工补检。
- `--mode title` 改用 UNTS Online 的 **Title/Keyword Search**（`UNTSOnline.aspx?id=2`），覆盖全部 UNTS 登记；`--match phrase|all|any` 对应站点的“Match this phrase / Match all these words / Match any of these words”。它仍是标题检索，不是全文检索；Volume Search、Participant Search、Full-text Search 和 AdvanceSearch 的文档类型/属性组合检索仍见 [references/unts-search.md](references/unts-search.md)，目前按人工或浏览器入口处理。
- `total` 是本次扫描目录页面中匹配的条约标题数，不是全库命中数；`status=partial` 表示某些目录页抓取失败或未访问完。
- `search` 只按标题匹配；要按当事国、登记号、卷页或条约正文检索，使用 UNTS Advanced Search 或人工补检。
- `fetch` 的 PDF 页号是 PDF 位置，不是印刷页码；扫描件可能 `needs_ocr=true`。

## 参考

- 2026-11-09 实测：29 个 `Treaties.aspx` 页面、`ViewDetails.aspx` 记录和 `Charter` 命中：[references/unts-search.md](references/unts-search.md)
- 部署、环境与排错：[README.md](README.md)
