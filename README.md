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
