# 数据来源清单 — 网易 2026-11-20

## 一手原件（SEC EDGAR，CIK 0001110646）

| 文件 | accession | 用途 |
|---|---|---|
| NetEase Announces Third Quarter 2026 Unaudited Financial Results | 0001104659-26-129894 / tm2630023d1_ex99-1.htm | Q3 损益、资产负债表、现金流、分部表、分红、回购 |
| Q2 2026 业绩公告 | 0001104659-26-098940 / tm2623482d1_ex99-1.htm | Q2 分部、分红、回购现金流 |
| Q1 2026 业绩公告 | 0001104659-26-064764 / tm2615053d1_ex99-1.htm | Q1 分部 |
| FY2025 业绩公告（含 Q4） | 0001104659-26-012943 / tm265608d1_ex99-1.htm | FY2025 损益、资产负债表、现金流、分部、分红 |
| FY2024 业绩公告 | 0001104659-25-015361 / tm256696d1_ex99-1.htm | FY2024 收入/毛利/归母/CFO |
| FY2022 业绩公告 | 0001104659-23-024438 / tm237341d1_ex99-1.htm | FY2022 收入/毛利/归母 |
| Next Day Disclosure Return（FF305） | 0001104659-26-120860、-123549、-114177 | 股本、库存股、回购明细 |
| SEC XBRL companyconcept（GrossProfit / OperatingIncomeLoss / CFO） | data.sec.gov | 年度趋势交叉核对（美元口径） |

## 行情与估值

| 来源 | 用途 |
|---|---|
| 腾讯行情 API `qt.gtimg.cn`（hk09999 / usNTES） | 收盘价、市值、PE、股本、YTD 涨跌幅 |
| 新浪行情 API `hq.sinajs.cn`（rt_hk09999 / gb_ntes）| 收盘价第二来源、港股 PE 交叉核对 |
| 东方财富 `push2.eastmoney.com`（116.09999 / 105.NTES） | 市值第二来源 |
| 欧洲央行 EUR 参考汇率（eurofxref-daily.xml） | USD/CNY、HKD/CNY 三角换算 |
| 腾讯行情前复权日线 `web.ifzq.gtimg.cn` | 52 周区间、YTD、ADR 溢价 241 日序列 |
| FRED `DGS10` | 美债 10 年期 5.07%（2026-11-18） |

## 行业与新闻

| 来源 | 用途 |
|---|---|
| 《2026 年 1—6 月中国游戏产业报告》（音数协游戏工委） | 上半年国内游戏市场实际销售收入 1,884.50 亿元、同比 +12.17%（新华网/央广网/国际金融报转载） |
| Motley Fool NTES Q3 2026 电话会转录 | 丁磊"短剧"表述原文、Ananta 上线日、回购口径 |
| 凤凰网 / 观察者网 / 驱动之家 / DoNews / 证券之星 | 电话会中文转述（作为第二来源） |
| 财联社 / TradingView / 观点网 / 智通财经 | 野村下调、花旗下调至 176 美元、小摩维持增持 280 港元 |

## 无法取得的来源（缺口）

- **HKEX 卖空日报**：`dayquot/d261119e.htm` 及其 `?sc_lang=en` 变体只含买卖记录与市场摘要，卖空表未在页面内找到；另试探 `mthstat/ShortSelling`、`dayquot/d2611*` 多路径均 404。本报告因此无卖空比例。
- **南向资金**：东财 `RPT_MUTUAL_STOCK_NORTHSTA` 返回 `{"success":false,"message":"服务器繁忙"}`；东财 push2 南向字段（f164/f165）返回空。本报告因此无南向流向。
- **aastocks**：`company-fundamental` 页面 302 后返回纯 JS 壳，无法取数。
- **macrotrends / stockanalysis**：均返回 403（反爬），改用 SEC 原件 + StockAnalysis 引用值。
