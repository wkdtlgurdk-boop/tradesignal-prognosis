"""당분기 컨센서스(네이버 모바일 finance/quarter, isConsensus=Y 열) 수집 -> cons.json
사용: python3 consensus.py 202609   (analysis.json 의 YoY 또는 QoQ 해당 종목 대상). 금액 단위 억원."""
import json,sys,time,urllib.request,concurrent.futures as cf
key=sys.argv[1]
A=[d for d in json.load(open('analysis.json'))['rows'] if d['yoy'] or d['qoq']]
def num(v):
    try: return float(str(v).replace(',','').strip())
    except: return None
def get(d):
    for i in range(3):
        try:
            f=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{d['code']}/finance/quarter",timeout=20))['financeInfo']
            flag={t['key']:t['isConsensus'] for t in f['trTitleList']}
            out=dict(code=d['code'],flag=flag.get(key))
            for r in f['rowList']:
                if r['title']=='매출액': out['rev']=num(r['columns'].get(key,{}).get('value'))
                if r['title']=='영업이익': out['op']=num(r['columns'].get(key,{}).get('value'))
            return out
        except Exception as e: err=str(e);time.sleep(1)
    return dict(code=d['code'],flag=None,err=err)
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(get,A))
json.dump(res,open('cons.json','w'),ensure_ascii=False)
import collections
print(len(res),collections.Counter(r.get('flag') for r in res),'rev없음',sum(1 for r in res if r.get('rev') is None),'op없음',sum(1 for r in res if r.get('op') is None))
