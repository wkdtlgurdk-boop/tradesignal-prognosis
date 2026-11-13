import json,time,urllib.request,urllib.parse
import fin
def call(corp_code,rc,fs):
    q=urllib.parse.urlencode(dict(crtfc_key=fin.K,corp_code=corp_code,bsns_year=fin.YEAR,reprt_code=rc,fs_div=fs))
    for i in range(6):
        try:
            d=json.load(urllib.request.urlopen("https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"+q,timeout=30))
            if d.get('status')=='020': time.sleep(5*(i+1));continue
            return d
        except Exception: time.sleep(3)
    return {'status':'ERR'}
fin.call=call
res=json.load(open('fin.json'))
out=[]
for x in res:
    if x.get('err'):
        time.sleep(0.5); y=fin.work(x['code'])
        x=y
    out.append(x)
json.dump(out,open('fin2.json','w'),ensure_ascii=False)
print('errs',[(x['code'],x['name']) for x in out if x.get('err')])
