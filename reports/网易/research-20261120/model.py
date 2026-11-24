"""网易 NTES / 09999.HK 估值模型 — 2026-11-20
所有算式用 Decimal，杜绝浮点误差。单位约定：
  RMB 金额均为「千元」（公司报表口径）；YI = 1e5 千元 = 1 亿元
  股价金额为「元」；BN = 1e9 元；MN = 1e6 股
"""
from decimal import Decimal as D, getcontext

getcontext().prec = 30
YI = D('1e5')     # 千元 -> 亿元
CY = D('1e8')     # 元   -> 亿元
BN = D('1e9')     # 元 -> 十亿
T = D('1000')      # 千元 -> 元
MN = D('1e6')     # 股 -> 百万


def f(x, n=2):
    return f"{x:,.{n}f}"


# ================= 汇率（ECB 2026-11-20 参考价，三角换算） =================
EURUSD, EURCNY, EURHKD = D('1.0992'), D('7.3280'), D('8.6239')
USDCNY = EURCNY / EURUSD
HKDCNY = EURCNY / EURHKD
HKDUSD = EURHKD / EURUSD

# ================= 股本与股价 =================
SH = D('3201470116')          # 2026-09-30 报表口径；加权基本股数 3,201,386 千股
ADS = SH / 5
HKP = D('154.00')             # 9999.HK 2026-11-20 收盘
USP = D('104.94')             # NTES 2026-11-19 收盘

mcap_hk = HKP * SH            # HKD
mcap_hk_cny = mcap_hk * HKDCNY
mcap_us = USP * ADS           # USD
mcap_us_cny = mcap_us * USDCNY
hk_implied_ads = HKP * 5 / HKDUSD

print("=" * 70)
print("汇率与市值")
print("=" * 70)
print(f"USD/CNY {USDCNY:.4f}   HKD/CNY {HKDCNY:.4f}   HKD/USD {HKDUSD:.4f}")
print(f"股本 {SH} 股   ADS 当量 {ADS/MN:,.4f} 百万")
print(f"港股市值 {f(mcap_hk/CY,2)} 亿港元 = {f(mcap_hk_cny/CY,2)} 亿人民币")
print(f"美股市值 {f(mcap_us/CY,2)} 亿美元 = {f(mcap_us_cny/CY,2)} 亿人民币")
print(f"港股折算每 ADS {hk_implied_ads:.2f} 美元 -> ADR 溢价 {(USP/hk_implied_ads-1)*100:+.2f}%")

# ================= 损益（千元） =================
FY25_rev, FY25_ni, FY25_nongaap, FY25_op, FY25_cfo = (D('112625807'), D('33759800'),
                                                     D('37343702'), D('35834867'), D('50739800'))
N9M25 = dict(rev=D('85078834'), ni=D('27517844'), nongaap=D('30270715'),
             op=D('27515709'), cfo=D('35916469'))
N9M26 = dict(rev=D('88550227'), ni=D('26056985'), nongaap=D('28185107'),
             op=D('34174014'), cfo=D('34247844'))
Q325 = dict(rev=D('28358625'), gp=D('18177605'), op=D('8013466'), ni=D('8615677'),
            games=D('23327508'), games_gp=D('16176378'))
Q226 = dict(rev=D('30106546'), gp=D('21217325'), op=D('12089338'), ni=D('6980656'),
            games=D('25022788'))
Q326 = dict(rev=D('27852400'), gp=D('19045025'), op=D('9427843'), ni=D('8402223'),
            games=D('22937367'), games_gp=D('17053275'))


def ttm(fy, cur, prior):
    return fy - prior + cur


ttm_rev = ttm(FY25_rev, N9M26['rev'], N9M25['rev'])
ttm_ni = ttm(FY25_ni, N9M26['ni'], N9M25['ni'])
ttm_ng = ttm(FY25_nongaap, N9M26['nongaap'], N9M25['nongaap'])
ttm_op = ttm(FY25_op, N9M26['op'], N9M25['op'])
ttm_cfo = ttm(FY25_cfo, N9M26['cfo'], N9M25['cfo'])

print()
print("=" * 70)
print("经营数据（人民币亿元）")
print("=" * 70)
print(f"TTM 收入 {f(ttm_rev/YI)} | 归母 {f(ttm_ni/YI)} | Non-GAAP {f(ttm_ng/YI)} | 经营利润 {f(ttm_op/YI)} | CFO {f(ttm_cfo/YI)}")
print(f"TTM 经营利润率 {ttm_op/ttm_rev*100:.2f}%   净利率 {ttm_ni/ttm_rev*100:.2f}%")
print()
print(f"Q3 收入 {f(Q326['rev']/YI)} 同比 {(Q326['rev']/Q325['rev']-1)*100:+.2f}%")
print(f"Q3 毛利 {f(Q326['gp']/YI)} 毛利率 {Q326['gp']/Q326['rev']*100:.2f}% (上年同期 {Q325['gp']/Q325['rev']*100:.2f}%)")
print(f"Q3 游戏 {f(Q326['games']/YI)} 同比 {(Q326['games']/Q325['games']-1)*100:+.2f}% 环比 {(Q326['games']/Q226['games']-1)*100:+.2f}%")
print(f"Q3 游戏毛利率 {Q326['games_gp']/Q326['games']*100:.2f}% (上年同期 {Q325['games_gp']/Q325['games']*100:.2f}%)")
print(f"Q3 经营利润 {f(Q326['op']/YI)} 同比 {(Q326['op']/Q325['op']-1)*100:+.2f}%   归母 {f(Q326['ni']/YI)} 同比 {(Q326['ni']/Q325['ni']-1)*100:+.2f}%")
print(f"Q2 经营利润 {f(Q226['op']/YI)}  归母 {f(Q226['ni']/YI)}")

# ================= 现金流口径 =================
capex_ttm = D('1065376') - D('927558') + D('506211')
content_ttm = D('930988') - D('803103') + D('365572')
da_ttm = D('2247427') - D('1527060') + D('1264742')
sbc_ttm = D('3583902') - D('2752871') + D('2128122')
nci_ttm = D('1033718') - D('554819') + D('487144')
fcf = ttm_cfo - capex_ttm - content_ttm

print()
print(f"TTM 资本开支 {f(capex_ttm/YI)} | 内容与版权采购 {f(content_ttm/YI)} | 折旧摊销 {f(da_ttm/YI)} | 股权激励 {f(sbc_ttm/YI)} | 少数股东损益 {f(nci_ttm/YI)}")
print(f"TTM 自由现金流（CFO−资本开支−内容采购）{f(fcf/YI)}")
print(f"FCF 收益率 港股口径 {fcf*T/mcap_hk_cny*100:.2f}%  美股口径 {fcf*T/mcap_us_cny*100:.2f}%")
print(f"CFO/归母净利 {ttm_cfo/ttm_ni:.2f}x   FCF/归母净利 {fcf/ttm_ni:.2f}x")

# ================= 资产负债表 2026-09-30（千元） =================
cash, td_cur, restr_cur, sti = D('14333233'), D('100906832'), D('4197727'), D('67398463')
td_ncur, restr_ncur, st_loans = D('260000'), D('3723'), D('11876923')
net_cash = cash + td_cur + restr_cur + sti + td_ncur + restr_ncur - st_loans
usable = net_cash - (restr_cur + restr_ncur) - D('10000000')   # 扣受限现金 + 100 亿经营备付
equity = D('173598286')
bvps = equity * 1000 / SH   # 千元 -> 元

print()
print("=" * 70)
print("资产负债表与净现金（2026-09-30）")
print("=" * 70)
print(f"现金及等价物 {f(cash/YI)} | 定期存款(流动) {f(td_cur/YI)} | 短期投资 {f(sti/YI)} | 受限现金 {f((restr_cur+restr_ncur)/YI)} | 短期借款 {f(st_loans/YI)}")
print(f"净现金（逐项重算）{f(net_cash/YI)} 亿元   公司口径 1752 亿元")
print(f"可动用净现金 {f(usable/YI)} 亿元 = 港股市值 {usable*T/mcap_hk_cny*100:.2f}% / 美股市值 {usable*T/mcap_us_cny*100:.2f}%")
print(f"归母权益 {f(equity/YI)} 亿元  BVPS {bvps:.2f} 元   PB 港股口径 {HKP*HKDCNY/bvps:.2f}x  美股口径 {USP*USDCNY*5/bvps:.2f}x")

# ================= 正常化利润与估值倍数 =================
TAXR = D('0.18')
norm_op = ttm_op * (1 - TAXR) - nci_ttm          # 千元
int_at = usable * D('0.018') * (1 - D('0.20'))   # 千元
norm_total = norm_op + int_at
eps_norm = norm_total * T / SH                   # 元/股
eps_norm_ads = eps_norm * 5 / USDCNY             # 美元/ADS
ni_cny = ttm_ni * T                              # 元
ng_cny = ttm_ng * T
rev_cny = ttm_rev * T
op_cny = ttm_op * T

print()
print("=" * 70)
print("估值倍数")
print("=" * 70)
print(f"正常化利润：经营利润×(1−18%) {f(norm_op/YI)}（已扣少数股东）+ 税后利息 {f(int_at/YI)} = {f(norm_total/YI)}")
print(f"正常化每股收益 {eps_norm:.2f} 元 = 每 ADS {eps_norm_ads:.2f} 美元")
print(f"PE 正常化   港股口径 {HKP*HKDCNY/eps_norm:.2f}x   美股口径 {USP/eps_norm_ads:.2f}x")
print(f"PE GAAP(TTM) 港股 {mcap_hk_cny/ni_cny:.2f}x  美股 {mcap_us_cny/ni_cny:.2f}x")
print(f"PE Non-GAAP  港股 {mcap_hk_cny/ng_cny:.2f}x  美股 {mcap_us_cny/ng_cny:.2f}x")
print(f"PS(TTM)      港股 {mcap_hk_cny/rev_cny:.2f}x  美股 {mcap_us_cny/rev_cny:.2f}x")
print(f"PB           港股口径 {HKP*HKDCNY/bvps:.2f}x   美股口径 {USP*USDCNY/(bvps*5):.2f}x")

opbiz_hk, opbiz_us = mcap_hk_cny - usable * T, mcap_us_cny - usable * T
print()
print(f"经营业务市值（扣可动用净现金）港股 {f(opbiz_hk/CY)} / 美股 {f(opbiz_us/CY)} 亿元")
print(f"  ÷ 税后经营利润  {opbiz_hk/(op_cny*(1-TAXR)):.2f}x  /  {opbiz_us/(op_cny*(1-TAXR)):.2f}x")
print(f"  ÷ 税前经营利润  {opbiz_hk/op_cny:.2f}x  /  {opbiz_us/op_cny:.2f}x")

# ================= 股息 =================
div_ads = D('1.16') + D('0.720') + D('0.480') + D('0.585')   # Q4'25 + Q1'26 + Q2'26 + Q3'26
div_cny = div_ads * USDCNY
print()
print(f"最近四季宣派每 ADS {div_ads} 美元   股息率 港股 {div_cny/(HKP*HKDCNY*5)*100:.2f}%  美股 {div_ads/USP*100:.2f}%")

# ================= 反向 DCF：现价隐含增速 =================
print()
print("=" * 70)
print("反向折现：经营业务隐含永续增速（终值模型）")
print("=" * 70)
op_fcf = norm_op + da_ttm - capex_ttm - content_ttm   # 千元
print(f"经营业务税后现金流 = 正常化税后经营利润 {f(norm_op/YI)} + 折旧摊销 {f(da_ttm/YI)} − 资本开支 {f(capex_ttm/YI)} − 内容采购 {f(content_ttm/YI)} = {f(op_fcf/YI)}")
for rs in ['0.06', '0.08', '0.10', '0.12']:
    r = D(rs)
    g_hk = r - op_fcf*T/opbiz_hk
    g_us = r - op_fcf*T/opbiz_us
    print(f"  r={r*100:.0f}%: 港股口径隐含 g = {g_hk*100:+.2f}%   美股口径隐含 g = {g_us*100:+.2f}%")

# ================= 十年现金流折现 =================
print()
print("=" * 70)
print("十年现金流折现（人民币口径，r=8%）")
print("=" * 70)


def dcf(base_fcf, path, term_g, r, years=10):
    """base_fcf 千元; path 为逐年增速列表(长度 years); 返回 2036 自由现金流与现值"""
    fcf = base_fcf
    pv = D('0')
    growths = []
    for i in range(years):
        g_i = path[i] if i < len(path) else path[-1]
        growths.append(g_i)
        fcf = fcf * (1 + g_i)
        pv += fcf / (1 + r) ** (i + 1)
    tv = fcf * (1 + term_g) / (r - term_g)
    pv_tv = tv / (1 + r) ** years
    return fcf, pv + pv_tv, pv, pv_tv


R = D('0.08')
scen = {
    '悲观': (D('0.25'), [-D('0.10')] + [-D('0.02')] * 9, D('0.005')),
    '基准': (D('0.50'), [D('0.02')] + [D('0.04')] * 4 + [D('0.03')] * 5, D('0.020')),
    '乐观': (D('0.20'), [D('0.08')] * 5 + [D('0.05')] * 5, D('0.025')),
}
base_fcf = op_fcf * T   # 千元 -> 元
wsum = D('0')
print(f"{'情景':<6}{'概率':>6}{'2036FCF':>12}{'经营现值':>12}{'现金终值':>11}{'终值占比':>9}{'每ADS美元':>12}")
for k, (p, path, tg) in scen.items():
    f_term, pv, pv_exp, pv_tv = dcf(base_fcf, path, tg, R)
    value = pv + usable * T * (1 + D('0.0144')) ** 10      # 现金按税后 1.44% 复利累积
    per_ads = value / ADS * 1 / USDCNY * 1                 # 元 -> 美元
    wsum += p * per_ads
    cashv = usable * T * (D('1.0144')) ** 10
    print(f"{k:<6}{p*100:>5.0f}%{f_term/CY:>12,.0f}亿{pv_exp/CY:>12,.0f}亿{cashv/CY:>11,.0f}亿{pv_tv/pv*100:>9.1f}%{per_ads:>13,.2f}")
# 尾部
tail = (usable * T * D('0.5') + norm_op * T * D('5')) / ADS / USDCNY
print(f"{'尾部':<6}{5:>5.0f}%{'现金5折+利润5倍':>12}{'':>12}{'':>11}{'':>9}{tail:>13,.2f}")
wsum += D('0.05') * tail
print(f"{'加权':<6}{'100%':>6}{'':>12}{'':>12}{'':>11}{'':>9}{wsum:>13,.2f}   较美股现价 {(wsum/USP-1)*100:+.1f}%  较港股折算 {(wsum/hk_implied_ads-1)*100:+.1f}%")

print()
print("折现率敏感性（基准情景每 ADS 美元）：")
p0, path0, tg0 = scen['基准']
for rs in ['0.07', '0.08', '0.09', '0.10']:
    rr = D(rs)
    _, pv, _, _ = dcf(base_fcf, path0, tg0, rr)
    value = pv + usable * T * (D('1.0144')) ** 10
    print(f"  r={rr*100:.0f}%  {value/ADS/USDCNY:>8,.2f}")

print()
print("税率敏感性（基准情景，r=8%）：")
for tr in ['0.15', '0.18', '0.22']:
    t_r = D(tr)
    op_n = ttm_op * (1 - t_r) - nci_ttm
    f2 = (op_n + da_ttm - capex_ttm - content_ttm) * T
    _, pv, _, _ = dcf(f2, path0, tg0, R)
    value = pv + usable * T * (D('1.0144')) ** 10
    print(f"  税率 {t_r*100:.0f}%  {value/ADS/USDCNY:>8,.2f}")

# ================= 十年 IRR（终值倍数口径） =================
print()
print("=" * 70)
print("十年 IRR：终值倍数口径（现金不增长，低估留存现金）")
print("=" * 70)
ROIC = D('0.25')


def exit_pe(g, r):
    return (1 - g / ROIC) / (r - g)


base_profit = norm_op * T   # 元/年
# 现金利息按税后 1.44% 复利进利润
cash_int = usable * T * D('0.0144')
rows = []
for k, (p, path, tg) in scen.items():
    prof = base_profit
    for g_i in path:
        prof = prof * (1 + g_i)
    prof_2036 = prof + cash_int * (D('1.0144')) ** 10
    for rs in ['0.08', '0.10']:
        rr = D(rs)
        pe_x = exit_pe(tg, rr)
        tv = prof_2036 * pe_x
        irr = (tv / mcap_hk_cny) ** (D(1) / 10) - 1 + D('0.030') - D('0.005')
        rows.append((k, rs, prof_2036 / CY, pe_x, tv / CY, irr * 100))
print(f"{'情景':<5}{'r':>6}{'2036利润':>11}{'退出PE':>8}{'2036市值':>11}{'IRR':>9}")
for k, rs, pr, pe_x, tv, irr in rows:
    print(f"{k:<5}{rs:>6}{pr:>10,.0f}亿{pe_x:>7.1f}x{tv:>10,.0f}亿{irr:>8.2f}%")
exp08 = sum(D(str(p)) * D(str(irr)) for (p, k, rs, irr) in
            [(scen[k][0], k, rs, irr) for k, rs, _, _, _, irr in rows if rs == '0.08'])
exp10 = sum(D(str(p)) * D(str(irr)) for (p, k, rs, irr) in
            [(scen[k][0], k, rs, irr) for k, rs, _, _, _, irr in rows if rs == '0.10'])
print(f"\n期望 IRR（不含尾部，概率归一前）：r=8% {exp08:.2f}%   r=10% {exp10:.2f}%")
print(f"尾部情景（现金5折+利润5倍）计入：")

tail_irr = lambda: (( (usable*T*D('0.5') + base_profit*5) / mcap_hk_cny ) ** (D('0.1')) - 1 + D('0.03') - D('0.005'))*100
print(f"  尾部 IRR {tail_irr():.2f}%")
for rs, base in (('0.08', exp08), ('0.10', exp10)):
    e = base * D('0.95') + D('0.05') * tail_irr()
    print(f"  含尾部 r={rs}: 期望 IRR {e:.2f}%")

# ================= 显式现金口径 IRR =================
print()
print("=" * 70)
print("十年 IRR：显式现金口径（派息40% + 回购抵消稀释，其余现金按1.44%税后累积）")
print("=" * 70)
PAYOUT = D('0.40')
for k, (p, path, tg) in scen.items():
    prof = base_profit
    cash_bal = usable * T
    for g_i in path:
        prof = prof * (1 + g_i)
        cash_bal = cash_bal * (1 + D('0.0144')) + prof * (1 - PAYOUT)
    prof_2036 = prof + cash_bal * D('0.0144')
    for rs in ['0.08', '0.10']:
        rr = D(rs)
        tv = prof_2036 * exit_pe(tg, rr) + cash_bal      # 现金按 1 倍计入
        irr = (tv / mcap_hk_cny) ** (D('0.1')) - 1 + D('0.030') - D('0.005')
        print(f"{k:<5}r={rs}  2036利润 {prof_2036/CY:>7,.0f}亿  现金 {cash_bal/CY:>7,.0f}亿  终值 {tv/CY:>8,.0f}亿  IRR {irr*100:>6.2f}%")

# 尾部显式现金口径 + 期望值汇总
tail_tv = usable * T * D('0.5') + base_profit * 5
tail_irr_exp8 = ((tail_tv / mcap_hk_cny) ** D('0.1') - 1 + D('0.03') - D('0.005')) * 100
print(f"\n尾部（现金5折+利润5倍）终值 {tail_tv/CY:,.0f}亿  IRR {tail_irr_exp8:.2f}%")
E8 = D('0.25')*D('8.72') + D('0.50')*D('14.18') + D('0.20')*D('17.30') + D('0.05')*tail_irr_exp8
E10 = D('0.25')*D('7.49') + D('0.50')*D('12.23') + D('0.20')*D('14.97') + D('0.05')*tail_irr_exp8
print(f"显式现金口径 期望 IRR: r=8% {E8:.2f}%   r=10% {E10:.2f}%")
print(f"（悲观档已含尾部风险，此处概率按 25/50/20/5 分配，尾部单列避免重复计数）")
