import json,urllib.request,time,concurrent.futures as cf
A=json.load(open('analysis.json'))['rows']
codes=[d['code'] for d in A if d['yoy'] or d['qoq']]
n=lambda s:float(str(s).replace(',',''))
def chart(code):
    for i in range(3):
        try:
            d=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{code}/price?pageSize=25&page=1",timeout=20))[:20]
            cut=len(d);brk=None
            for k in range(len(d)-1):
                ch=n(d[k]['closePrice'])/n(d[k+1]['closePrice'])-1
                if abs(ch)>0.30: cut=k+1;brk=d[k]['localTradedAt'];break
            d=d[:cut]
            c=n(d[0]['closePrice']);hi=max(n(x['highPrice']) for x in d);lo=min(n(x['lowPrice']) for x in d)
            return dict(close=c,d_hi=c/hi-1,d_lo=c/lo-1,date=d[0]['localTradedAt'],days=len(d),break_day=brk)
        except Exception: time.sleep(1)
    return None
with cf.ThreadPoolExecutor(6) as ex: CH=dict(zip(codes,ex.map(chart,codes)))
json.dump(CH,open('chart_all.json','w'))
print(len(CH),'실패',[c for c,v in CH.items() if v is None])
