import json,time,urllib.request,urllib.parse,concurrent.futures as cf
import fin,docparse as D
def call(corp_code,year,rc,fs):
    q=urllib.parse.urlencode(dict(crtfc_key=fin.K,corp_code=corp_code,bsns_year=year,reprt_code=rc,fs_div=fs))
    for i in range(6):
        try:
            d=json.load(urllib.request.urlopen("https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"+q,timeout=30))
            if d.get('status')=='020': time.sleep(5*(i+1));continue
            return d
        except Exception: time.sleep(3)
    return {'status':'ERR'}
def stmt(cc,year,rc,fs):
    d=call(cc,year,rc,fs)
    if d.get('status')=='000' and d.get('list'): return d['list']
    return None
A=json.load(open('analysis.json'))['rows']
F={x['code']:x for x in json.load(open('fin3.json'))}
T=[d for d in A if d['yoy'] or d['qoq']]
print('대상',len(T))
def work(d):
    x=F[d['code']];cc=x['corp_code'];fs=x['fs']
    o=dict(code=d['code'],name=d['name'],fs=fs,src=x.get('src','API'))
    out={}
    try:
        L26=None
        if o['src']=='API': L26=stmt(cc,2026,'11014',fs)
        L25=stmt(cc,2025,'11014',fs)      # 2025 3Q: frmtrm_add = 2024 9M
        LA=stmt(cc,2025,'11011',fs)       # FY2025 annual: thstrm FY25, frmtrm FY24
        doc=None
        if o['src']!='API':
            p=D.parse(D.fetch(x['rcept_no']))
            if p: doc=p
        for key,ids,nms in(('rev',fin.REV_ID,fin.REV_NM),('op',fin.OP_ID,fin.OP_NM)):
            v=dict(m26=None,m25=None,m24=None,fy25=None,fy24=None)
            if L26:
                a=fin.pick(L26,ids,nms)
                if a: v['m26']=fin.num(a.get('thstrm_add_amount'));v['m25']=fin.num(a.get('frmtrm_add_amount'))
            elif doc:
                fsn,u,res=doc;r=res.get(key)
                if r and len(r)>=4: v['m26']=r[1]*u;v['m25']=r[3]*u
            if L25:
                a=fin.pick(L25,ids,nms)
                if a: v['m24']=fin.num(a.get('frmtrm_add_amount'))
            if LA:
                a=fin.pick(LA,ids,nms)
                if a: v['fy25']=fin.num(a.get('thstrm_amount'));v['fy24']=fin.num(a.get('frmtrm_amount'))
            out[key]=v
        o.update(out)
    except Exception as e: o['err']=str(e)
    return o
with cf.ThreadPoolExecutor(3) as ex: res=list(ex.map(work,T))
json.dump(res,open('ttm.json','w'),ensure_ascii=False)
print('done',len(res),'err',sum(1 for r in res if r.get('err')))
