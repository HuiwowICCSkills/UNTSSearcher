# UNTS/UNTC 检索实测记录（2026-11-09）

## 入口

- 根页：`https://treaties.un.org/Pages/ParticipationStatus.aspx?clang=_en`
- 目录页：`https://treaties.un.org/Pages/Treaties.aspx?id=<chapter>&subid=A&clang=_en`
- 条约详情：`https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=...&chapter=...&clang=_en`

实测根页返回 200、80,834 字节，发现 29 个 `Treaties.aspx?` 目录链接。

## 解析

- 只把 URL 路径含 `ViewDetails.aspx` 的链接当作条约记录。
- 标题来自链接文本；详情页 URL 保留 `mtdsg_no` 和 `chapter` 参数。
- `Charter --max-pages 2` → 5 条标题命中（Charter、Statute of the ICJ、Charter amendments 等）。

## 边界

- 这是 MTDSG 标题目录，不是全量 UNTS 登记库。
- 没有服务端全文检索；`--max-pages` 控制扫描的目录页数量。

## UNTS Online 的五种检索入口（2026-11-12 浏览器核对）

`https://treaties.un.org/Pages/AdvanceSearch.aspx?tab=UNTS&clang=_en` 左侧列出五种模式；它们不是同一个表单：

| 模式 | 页面/入口 | 主要字段 |
| --- | --- | --- |
| Advanced Search | `AdvanceSearch.aspx?tab=UNTS&clang=_en` | 先选 document type（Action/CN/CTC/Maps/Treaty），再按属性添加多条 criteria（`drpSearchObj`、`drpAttribute`、`TextBox1`、`btnAdd`、`btnSubmit`） |
| Volume Search | `UNTSOnline.aspx?id=1` | 卷号/页码 |
| Title Search | `UNTSOnline.aspx?id=2` | `txtTitle` + `Adv_srch`（cnd3=phrase，cnd2=all words，cnd1=any words） |
| Participant Search | `UNTSOnline.aspx?id=3` | `lstParticipants` 复选框（约 1,000+ 个当事方） |
| Full-text Search | `UNTSOnline.aspx?id=4` | 条约正文全文 |

Title Search 的 ASP.NET postback 已实现为 `--mode title`：先 GET `UNTSOnline.aspx?id=2`，抓取 `__VIEWSTATE`/`__EVENTVALIDATION`，再 POST `txtTitle`、`Adv_srch`、`btnSubmit`、`drpPageSize=50`。实测 `genocide` → `Record Count : 2`，两条分别为 1948 年《灭绝种族罪公约》和 1995 年卢旺达问题相关协定。`--offset` 只支持第一页 50 条以内；更多结果需缩小查询或使用网站分页。
