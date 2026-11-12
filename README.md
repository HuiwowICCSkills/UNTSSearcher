# UNTSSearcher 部署指引

独立检索联合国条约集（UNTC）的 MTDSG 标题目录。只访问 `treaties.un.org`。

仓库：<https://github.com/HuiwowICCSkills/UNTSSearcher>（公开）。

## 环境

Python 3.10+，依赖 `requests`、`beautifulsoup4`、`pypdf`；无需浏览器或登录。

## 安装与自检

```powershell
git clone https://github.com/HuiwowICCSkills/UNTSSearcher.git "$env:USERPROFILE\.codex\skills\UNTSSearcher"
python -m pip install -r "$env:USERPROFILE\.codex\skills\UNTSSearcher\requirements.txt"
& "$env:USERPROFILE\.codex\skills\UNTSSearcher\run.ps1" doctor
```

## 使用

```powershell
$unts = "$env:USERPROFILE\.codex\skills\UNTSSearcher\run.ps1"
& $unts search "Charter" --max-pages 5 --limit 10 --out './unts.json'
& $unts fetch 'https://treaties.un.org/Pages/ViewDetails.aspx?...' --out './treaty.json' --text-out './treaty.txt'
```

`--max-pages` 控制扫描的 `Treaties.aspx` 页面数；默认 20。`total` 是本次扫描到的标题匹配数，不是 UNTS 全库命中数。

## 边界

- 只覆盖 MTDSG 标题目录，不覆盖全部 UNTS 登记、双边条约和完整 Advanced Search。
- 标题匹配是区分大小写的子串匹配；检索词尽量使用条约标题中的英文词。
- 详细页可能只有状态表；PDF 文本需另行 `fetch`。

## 实测效果（2026-11-12）

以下命令与结果来自本机 `~/.codex/skills/UNTSSearcher` 的实网运行；检索日期 2026-11-12（Asia/Shanghai），输出为该次运行实际返回的 JSON 报告。

```powershell
$unts = "$env:USERPROFILE\.codex\skills\UNTSSearcher\run.ps1"
& $unts search 'genocide' --mode title --match phrase --limit 5
```

- 状态：`ok`；UNTS Online 页面报告 `Record Count : 2`；本次返回 2 条。
- 模式：`title`，即 UNTS Online 的 Title/Keyword Search（`UNTSOnline.aspx?id=2`），覆盖全部 UNTS 登记，不只 MTDSG 标题目录。
- 代表性结果：

| 登记号 | 条约 | 结论日期 / 类型 | 链接 |
| --- | --- | --- | --- |
| I-1021 | Convention on the Prevention and Punishment of the Crime of Genocide | 09/12/1948；Open Multilateral | https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280027fac&clang=_en |
| I-43680 | Agreement on surrender of persons between the United States of America and the International Criminal Tribunal for the Prosecution of Persons Responsible for Genocide and Other Serious Violations of International Humanitarian Law Committed in the Territory of Rwanda and Rwandan Citizens Responsible for Genocide and Other Such Violations Committed in the Territory of Neighbouring States | 24/01/1995；Bilateral | https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280060ebf&clang=_en |

> 说明：以上是 UNTS 登记目录的**检索元数据**，不是条约正文；`total=2` 是本查询的标题命中数。Volume、Participant、Full-text 和 AdvanceSearch 的文档类型/属性组合检索仍需原站操作。
