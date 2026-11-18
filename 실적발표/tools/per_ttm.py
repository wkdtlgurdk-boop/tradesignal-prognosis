"""PER 재계산: 시총(현재) / 최근 4분기 합산 지배주주 순이익 (= 작년 4분기 + 올해 1~3분기 = FY25 − 9M25 + 9M26)"""
import sys,os,json,re,time,urllib.request,concurrent.futures as cf
sys.argv=['x']
sys.path.insert(0,'/home/user/tradesignal-prognosis/실적발표/tools')
import watch_check as w
S=json.load(open('stocks.json'))['rows']   # 평가 대상 종목 목록(code 열이 있는 rows)
codes=[r['code'] for r in S]
# corp_code 수집: 이미 받은 fin3.json 들에서, 없으면 corpCode.xml
cm={}
for p in('fin3.json',):   # 필요하면 다른 접수분의 fin3.json 도 추가
    try:
        for x in json.load(open(p)): cm.setdefault(x['code'],x['corp_code'])
    except Exception as e: print('skip',p,e)
miss=[c for c in codes if c not in cm]
print('corp_code 확보',len(codes)-len(miss),'/ 없음',len(miss),flush=True)
if miss: cm.update(w.corp_map(set(miss)))
NI_ID='ifrs-full_ProfitLossAttributableToOwnersOfParent'
def pick_ni(L):
    R=[a for a in L if a.get('sj_div') in('IS','CIS')]
    for a in R:
        if a.get('account_id')==NI_ID: return a,'지배주주'
    for a in R:
        n=a.get('account_nm','').replace(' ','')
        if '지배' in n and ('순이익' in n or '당기순' in n) and '비지배' not in n: return a,'지배주주'
    for a in R:
        if a.get('account_id')=='ifrs-full_ProfitLoss': return a,'당기순이익(지배 구분 없음)'
    for a in R:
        if a.get('account_nm','').replace(' ','') in('당기순이익','당기순이익(손실)','분기순이익','분기순이익(손실)'): return a,'당기순이익(지배 구분 없음)'
    return None,None
def mcap(code):
    for i in range(3):
        try:
            d=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{code}/integration",timeout=20))
            return w.pmcap([x['value'] for x in d['totalInfos'] if x['code']=='marketValue'][0])
        except Exception: time.sleep(1)
def one(code):
    o=dict(code=code);cc=cm.get(code)
    o['mcap']=mcap(code)
    if not cc: o['err']='corp_code 없음';return o
    fs,L3=w.stmt_any(cc,2026,'11014','CFS')
    if not L3: o['err']='3분기 재무 API 없음';return o
    fs2,LA=w.stmt_any(cc,2025,'11011',fs)
    if not LA: o['err']='FY25 재무 없음';return o
    a3,k3=pick_ni(L3);aa,ka=pick_ni(LA)
    if not a3 or not aa: o['err']='순이익 계정 없음';return o
    m26=w.num(a3.get('thstrm_add_amount')) if a3.get('thstrm_add_amount') not in(None,'') else w.num(a3.get('thstrm_amount'))
    m25=w.num(a3.get('frmtrm_add_amount')) if a3.get('frmtrm_add_amount') not in(None,'') else w.num(a3.get('frmtrm_amount'))
    fy25=w.num(aa.get('thstrm_amount'))
    o.update(fs=fs,fs_fy=fs2,mixed=(fs!=fs2),kind=k3,kind_fy=ka,m26=m26,m25=m25,fy25=fy25)
    if None in(m26,m25,fy25): o['err']='순이익 값 누락';return o
    o['ni_ttm']=fy25-m25+m26
    if o['ni_ttm']>0 and o['mcap']: o['per_ttm']=o['mcap']/o['ni_ttm']
    return o
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(one,codes))
json.dump(res,open('per_ttm.json','w'),ensure_ascii=False)
import collections
print('완료',len(res),'오류',collections.Counter(r.get('err') for r in res),'PER 계산',sum(1 for r in res if r.get('per_ttm')),'적자(TTM NI≤0)',sum(1 for r in res if r.get('ni_ttm') is not None and r['ni_ttm']<=0))
