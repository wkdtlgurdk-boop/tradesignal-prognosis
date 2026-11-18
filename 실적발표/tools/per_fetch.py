import json,re,time,urllib.request,concurrent.futures as cf
day=json.load(open('day1116/eval_day.json'))
wk=json.load(open('pick_result.json'))
codes=sorted({e['code'] for e in day}|{e['code'] for e in wk})
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
                if k=='per': o['per']=num(x['value']);o['per_txt']=x['value'];o['per_period']=x.get('valueDesc')
                if k=='cnsPer': o['cns_per']=num(x['value']);o['cns_txt']=x['value']
                if k=='pbr': o['pbr']=num(x['value'])
                if k=='eps': o['eps_period']=x.get('valueDesc')
            return o
        except Exception as e: time.sleep(1)
    return dict(code=c,err=True)
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(get,codes))
json.dump({r['code']:r for r in res},open('per_all.json','w'),ensure_ascii=False)
import collections
print(len(res),'실패',sum(1 for r in res if r.get('err')),'PER 없음(적자 등)',sum(1 for r in res if not r.get('err') and r.get('per') is None))
print(collections.Counter(r.get('per_period') for r in res).most_common(5))
