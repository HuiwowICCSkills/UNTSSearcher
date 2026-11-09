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
