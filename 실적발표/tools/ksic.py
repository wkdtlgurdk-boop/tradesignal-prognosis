import json,time,urllib.request,urllib.parse,concurrent.futures as cf,fin
F={x['code']:x for x in json.load(open('fin3.json'))}
A=json.load(open('analysis.json'))['rows']
def get(d):
    cc=F[d['code']]['corp_code']
    for i in range(6):
        try:
            r=json.load(urllib.request.urlopen("https://opendart.fss.or.kr/api/company.json?"+urllib.parse.urlencode(dict(crtfc_key=fin.K,corp_code=cc)),timeout=30))
            if r.get('status')=='020': time.sleep(5*(i+1));continue
            return d['code'],r.get('induty_code'),r.get('corp_name')
        except Exception: time.sleep(2)
    return d['code'],None,None
with cf.ThreadPoolExecutor(4) as ex: res=list(ex.map(get,A))
json.dump(res,open('ksic.json','w'),ensure_ascii=False)
print(len(res),sum(1 for r in res if r[1] is None))
