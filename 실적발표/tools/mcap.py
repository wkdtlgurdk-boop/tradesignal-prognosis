import json,re,urllib.request,concurrent.futures as cf,time
rows=json.load(open('filings.json'))
codes=sorted({x['stock_code'] for x in rows if x['stock_code'].strip()})
def parse(v):
    t=0
    m=re.search(r'([\d,]+)조',v)
    if m:t+=int(m.group(1).replace(',',''))*10**12
    v2=re.sub(r'[\d,]+조','',v)
    m=re.search(r'([\d,]+)억',v2)
    if m:t+=int(m.group(1).replace(',',''))*10**8
    m=re.search(r'([\d,]+)만',v2)
    if m:t+=int(m.group(1).replace(',',''))*10**4
    return t
def f(c):
    for i in range(3):
        try:
            d=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{c}/integration",timeout=20))
            mv=[x['value'] for x in d['totalInfos'] if x['code']=='marketValue'][0]
            return c,d.get('stockName'),mv,parse(mv)
        except Exception as e:
            err=str(e);time.sleep(1)
    return c,None,err,None
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(f,codes))
json.dump(res,open('mcap.json','w'),ensure_ascii=False)
bad=[r for r in res if r[3] is None]
print(len(res),'fail',len(bad),bad[:10])
print('>=2000억',sum(1 for r in res if r[3] and r[3]>=2000*10**8))
