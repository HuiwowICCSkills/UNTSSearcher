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

## 实测效果（2026-11-09）

以下命令与结果来自本机 `~/.codex/skills/UNTSSearcher` 的实网运行；检索日期 2026-11-09（Asia/Shanghai），输出为该次运行实际返回的 JSON 报告。

```powershell
& .\run.ps1 search 'Charter' --max-pages 5 --limit 5
```

- 状态：`ok`；`total = 5`；本次返回 5 条；本次扫描的 `Treaties.aspx` 页数为 `catalogues_requested = 5`，可发现目录共 `catalogues_discovered = 29`。
- 代表性结果（`result_type` 均为 `retrieved_metadata`，`via` 均为 `unts-title-catalogue`）：

| 题名 | 类型 / 日期 | 链接 |
| --- | --- | --- |
| Charter of the United Nations (deposited in the archives of the Government of the United States of America).   San Francisco, 26 June 1945 | retrieved_metadata；JSON 无日期字段（日期见题名） | https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=I-1&chapter=1&clang=_en |
| Declarations of Acceptance of the Obligations contained in the Charter of the United Nations - Admission of States to Membership in the United Nations in accordance with Article 4 of the Charter.   San Francisco, 24 October 1945 | retrieved_metadata；JSON 无日期字段（日期见题名） | https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=I-2&chapter=1&clang=_en |
| Amendments to Articles 23,27 and 61 of the Charter of the United Nations, adopted by the General Assembly of the United Nations in resolutions 1991 A and B (XVIII) of 17 December 1963.   New York, 17 December 1963 | retrieved_metadata；JSON 无日期字段（日期见题名） | https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=I-5-a&chapter=1&clang=_en |

> 说明：`total = 5` 是本次扫描到的 MTDSG 标题目录**标题匹配数**，不是 UNTS 全库命中数——本次只请求了 29 个目录中的 5 个，标题匹配还是区分大小写的子串匹配。返回的是目录条目**元数据**（`content_scope`：catalogue title match; treaty detail page not yet fetched），不是条约正文；要读条文、缔约方与保留需另用 `fetch` 打开详细页。上表三份文书分别是《联合国宪章》本身、依第四条接受义务的声明、以及 1963 年对第 23、27、61 条的修正。
