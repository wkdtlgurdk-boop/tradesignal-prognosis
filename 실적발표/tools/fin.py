import os,json,urllib.request,urllib.parse,concurrent.futures as cf,time
K=os.environ['DART_API_KEY']
filings=json.load(open('filings.json'))
mc={c:(n,mv,v) for c,n,mv,v in json.load(open('mcap.json'))}
corp={}
for x in filings:
    if x['stock_code'].strip(): corp.setdefault(x['stock_code'],x)
targets=[c for c in corp if mc.get(c) and mc[c][2] and mc[c][2]>=2000*10**8]
def call(corp_code,rc,fs):
    q=urllib.parse.urlencode(dict(crtfc_key=K,corp_code=corp_code,bsns_year=2026,reprt_code=rc,fs_div=fs))
    for i in range(3):
        try: return json.load(urllib.request.urlopen("https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"+q,timeout=30))
        except Exception: time.sleep(1.5)
    return {'status':'ERR'}
def num(s):
    try: return int(str(s).replace(',','').strip())
    except: return None
REV_ID=['ifrs-full_Revenue','dart_Revenue']; REV_NM=['매출액','수익(매출액)','영업수익','매출','순매출액']
OP_ID=['dart_OperatingIncomeLoss']; OP_NM=['영업이익','영업이익(손실)','영업손익']
def pick(lst,ids,nms):
    L=[a for a in lst if a.get('sj_div') in('IS','CIS')]
    for i in ids:
        for a in L:
            if a.get('account_id')==i: return a
    for n in nms:
        for a in L:
            if a.get('account_nm','').replace(' ','')==n: return a
    return None
def getfs(cc,rc):
    for fs in('CFS','OFS'):
        r=call(cc,rc,fs)
        if r.get('status')=='000' and r.get('list'): return fs,r['list']
    return None,None
def work(c):
    cc=corp[c]['corp_code']
    out=dict(code=c,name=mc[c][0],mcap=mc[c][2],corp_code=cc,rcept_no=corp[c]['rcept_no'],rcept_dt=corp[c]['rcept_dt'])
    fs3,l3=getfs(cc,'11014')
    if not l3: out['err']='3Q 재무 없음';return out
    fs2,l2=getfs(cc,'11012')
    out['fs']=fs3
    for key,ids,nms in(('rev',REV_ID,REV_NM),('op',OP_ID,OP_NM)):
        a=pick(l3,ids,nms)
        if not a: out[key]=None;continue
        cur=num(a.get('thstrm_amount')); py=num(a.get('frmtrm_q_amount'))
        cum=num(a.get('thstrm_add_amount'))
        q2=None;q2h=None
        if l2:
            b=pick(l2,ids,nms)
            if b:
                q2=num(b.get('thstrm_amount')); q2h=num(b.get('thstrm_add_amount'))
        alt=(cum-q2h) if (cum is not None and q2h is not None) else None
        out[key]=dict(q3=cur,q3_py=py,q2=q2,q3_alt=alt,acc=a.get('account_nm'))
    out['fs2']=fs2
    return out
if __name__=='__main__':
    with cf.ThreadPoolExecutor(5) as ex: res=list(ex.map(work,targets))
    json.dump(res,open('fin.json','w'),ensure_ascii=False)
    print(len(targets),'done; errs',sum(1 for r in res if r.get('err')),'norev',sum(1 for r in res if r.get('rev') is None and not r.get('err')),'noop',sum(1 for r in res if r.get('op') is None and not r.get('err')))
