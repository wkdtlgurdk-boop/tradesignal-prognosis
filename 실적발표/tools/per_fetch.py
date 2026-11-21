"""종목 목록(stocks_base.json 의 rows[].code)에 대해 네이버 모바일 증권의 PER·추정PER·PBR 을 수집 -> per_all.json
사용: python3 per_fetch.py stocks_base.json
참고용 값이다(대부분 직전 확정 분기 기준). 아티팩트의 PER 은 per_ttm.py 로 직접 계산한 값을 쓴다."""
import sys,json,re,time,urllib.request,concurrent.futures as cf
codes=sorted({r['code'] for r in json.load(open(sys.argv[1]))['rows']})
def num(s):
    m=re.search(r'-?[\d,]+(\.\d+)?',str(s or ''))
    return float(m.group(0).replace(',','')) if m else None
def get(c):
    for i in range(3):
        try:
            d=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{c}/integration",timeout=20))
            o=dict(code=c)
            for x in d['totalInfos']:
                k=x['code']
                if k=='per': o['per']=num(x['value']);o['per_period']=x.get('valueDesc')
                if k=='cnsPer': o['cns_per']=num(x['value'])
                if k=='pbr': o['pbr']=num(x['value'])
            return o
        except Exception: time.sleep(1)
    return dict(code=c,err=True)
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(get,codes))
json.dump({r['code']:r for r in res},open('per_all.json','w'),ensure_ascii=False)
print(len(res),'실패',sum(1 for r in res if r.get('err')),'PER 없음',sum(1 for r in res if not r.get('err') and r.get('per') is None))
