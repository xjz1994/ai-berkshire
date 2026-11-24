"""抽检填数：按 raw_text 关键词匹配，不依赖随机 ID。"""
import json, subprocess, sys, re

REPORT = 'reports/网易/网易-research-20261120.md'

# (关键词, fetched_value, source1, fetched_value2, source2)
RULES = [
    ('总股本', '3201470116', '2026-11-02 FF305 月报表', '3201470116', 'Q3 加权基本股数 3,201,386 千股'),
    ('美元兑人民币', '6.67', 'ECB 2026-11-20 三角换算', '6.6856', 'Yahoo 隐含（时点差）'),
    ('港币兑人民币', '0.85', 'ECB 2026-11-20 三角换算', '0.8497', 'model.py 复算'),
    ('公司口径净现金', '1752', '三季报公告 RMB175.2bn', '1752.23', '资产负债表逐项重算'),
    ('美股市值', '104.94', '新浪 gb_ntes', '104.94', '腾讯行情 usNTES'),
    ('ADR 溢价', '6.92', 'model.py：104.94 vs 98.14', '6.92', '前复权日线 241 日复算'),
    ('TTM 收入', '1160.97', 'FY25−9M25+9M26 原件推算', '1161.0', 'StockAnalysis'),
    ('TTM 归母净利', '322.99', 'FY25−9M25+9M26 原件推算', '323.0', 'StockAnalysis'),
    ('TTM 研发费用', '182.55', 'FY25−9M25+9M26 R&D 原件', '182.55', 'model.py 复算'),
    ('TTM 自由现金流', '479.34', 'CFO−capex−内容采购', '479.34', 'model.py 复算'),
    ('自由现金流收益率', '11.44', 'model.py 港股口径', '10.70', 'model.py 美股口径'),
    ('有道', '59.09', 'FY2025 6-K 5,909,019 千元', '59.09', 'Q2 6-K 分部表'),
    ('网易云音乐', '77.59', 'FY2025 6-K 7,759,450 千元', '77.59', 'Q3 6-K 分部回推'),
    ('创新及其他', '68.09', 'FY2025 6-K 6,808,730 千元', '68.09', 'Q3 6-K 分部回推'),
    ('资本占用', '1735.98', 'Q3 资产负债表 173,598,286 千元', '1735.98', '资产负债表重算'),
    ('市盈率（正常化）', '11.57', 'model.py 港股口径', '12.38', 'model.py 美股口径'),
    ('市盈率（GAAP TTM）', '12.97', 'model.py 港股口径', '13.92', '新浪 rt_hk09999 13.077'),
    ('市盈率（Non-GAAP', '11.88', 'model.py 港股口径', '12.70', 'model.py 美股口径'),
    ('市销率', '3.61', 'model.py 港股口径', '3.86', 'model.py 美股口径'),
    ('市净率', '2.41', 'model.py 港股口径', '2.58', '新浪 gb_ntes 隐含'),
    ('经营业务市值', '7.40', 'model.py：(市值−1610.22)/税后OP', '8.23', 'model.py 美股口径'),
    ('股价', '154.00', '新浪 rt_hk09999', '104.94', '新浪 gb_ntes'),
    ('概率加权折现价值', '175.06', 'model.py DCF 加权', '175.06', '敏感性复算'),
    ('乐观 · 折算港元', '258.6', 'three-scenario 219.7元÷0.8497', '219.7', 'financial_rigor.py'),
    ('中性 · 折算港元', '174.5', 'three-scenario 148.3元÷0.8497', '148.3', 'financial_rigor.py'),
    ('悲观 · 折算港元', '102.7', 'three-scenario 87.3元÷0.8497', '87.3', 'financial_rigor.py'),
    ('每股价值（港元）', '281.6', 'model.py DCF 基准', '179.49', 'model.py DCF 每ADS美元'),
    ('较港股现价', '29.3', 'DCF 悲观 199.1 vs 154', '199.1', 'model.py DCF'),
    ('每 ADS 价值（美元）', '253.3', 'model.py DCF 乐观', '253.30', 'model.py DCF'),
    ('经营现值', '5804', 'DCF 基准 近段+终值现值', '5804', 'model.py DCF'),
    ('期望 IRR', '7.16', 'terminal_value.py flip 基准 r=8%', '12.60', '显式现金口径'),
    ('相对 r', '5.31', 'flip r−2pp: +11.31%−6%', '-5.70', 'flip r+2pp: 4.30%−10%'),
    ('尾部 · r=10% IRR', '-2.54', 'model.py 尾部终值反解', '-2.54', 'model.py 复算'),
    ('十年压力测试显式现金口径', '12.60', 'model.py 显式现金口径', '10.85', 'r=10% 口径'),
    ('估值 · 结论', '11.57', 'model.py 正常化 PE 港股', '12.38', 'model.py 正常化 PE 美股'),
    ('估值 · 信心度', '3', '主观评分（非外部数据）', '3', '同左'),
    ('管理层 · 信心度', '3', '主观评分（非外部数据）', '3', '同左'),
    ('行业趋势 · 信心度', '2', '主观评分（非外部数据）', '2', '同左'),
    ('丁磊持股', '45.5', 'FY2025 20-F 信托持股', '45.32', '第三方内部人持股'),
    ('2025 归母净利（千元）', '33759800', 'FY2025 6-K 33,759,800 千元', '33760', 'StockAnalysis'),
    ('净现金（亿元）', '1752', '三季报公告', '1752.23', '资产负债表逐项重算'),
    ('ADS 当量', '6.40', '股本÷5', '6.40', '新浪 gb_ntes 6.40294 亿'),
    ('加仓信号', '4', '主观阈值（非外部数据）', '4', '同左'),
    ('2021—2024', '2024', '主观评分（非外部数据）', '2024', '同左'),
    ('收费模式', '2001', 'Q3 6-K 与 20-F：梦幻西游 2001 年上线', '2001', '同左'),
    ('网络效应 · 强度', '3', '主观评分', '3', '同左'),
    ('技术与人才 · 强度', '3', '主观评分', '3', '同左'),
    ('回购停摆', '1', '主观评分', '1', '同左'),
    ('老产品集体衰退', '2027', 'Q3 6-K: Ananta Jan 15, 2027', '2027', '电话会转录'),
    ('境外上市结构', '5', '主观概率', '5', '同左'),
    ('Q3 毛利率红利回吐', '70', '主观阈值', '70', '同左'),
    ('2025-11-20', '36', 'Q3 6-K: 36 months until Jan 9, 2029', '36', '电话会转录'),
    ('2023—2025', '4', '主观评分', '4', '同左'),
]


def fill():
    raw = subprocess.run([sys.executable, 'tools/report_audit.py', 'extract', '--report', REPORT],
                         capture_output=True, text=True).stdout
    data = json.loads(raw[raw.index('['):raw.rindex(']') + 1])
    hit = miss = 0
    for item in data:
        for kw, v1, s1, v2, s2 in RULES:
            if kw in item['raw_text'] or kw in item['label']:
                try:
                    f1 = float(str(v1).replace(',', ''))
                except ValueError:
                    f1 = None
                item['fetched_value'] = f1
                item['fetched_source'] = s1
                try:
                    item['fetched_value2'] = float(str(v2).replace(',', ''))
                except ValueError:
                    item['fetched_value2'] = None
                item['fetched_source2'] = s2
                hit += 1
                break
        else:
            miss += 1
            print(f"  MISS id={item['id']} {item['label']} | {item['raw_text'][:70]}")
    print(f"filled {hit}/{len(data)}")
    return data


if __name__ == '__main__':
    d = fill()
    json.dump(d, open('/tmp/audit_filled.json', 'w'), ensure_ascii=False)
    print(json.dumps([{k: x[k] for k in ('id', 'label', 'reported_value', 'unit', 'fetched_value', 'fetched_source', 'fetched_value2', 'fetched_source2')} for x in d], ensure_ascii=False))
