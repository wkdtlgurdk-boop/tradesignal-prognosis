"""관심·보유 종목 당분기 실적 점검 (YoY / QoQ / TTM / 컨센 대비). 시총 필터 없음.
사용: (작업 폴더에 watch.json 준비)  python3 watch_check.py [YEAR=2026] [분기보고서코드=11014] [직전분기코드=11012] [컨센키=202609]
  watch.json = [{"code":"278470","name":"에이피알","group":"보유"}, ...]   ← 개인 정보이므로 저장소에 올리지 말 것
결과: watch_result.json   (이어서 gen_watch_xlsx.py)
- 분기보고서가 아직 없으면 영업(잠정)실적 공정공시로 계산(src='잠정'), 둘 다 없으면 '미발표'.
- 이 파일은 fin.py 를 import 하지 않는다(fin.py 는 import 시 이번 분기 파일을 읽는다)."""
import sys,os,io,json,re,time,html,zipfile,urllib.request,urllib.parse
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import docparse as D
K=os.environ['DART_API_KEY']
YEAR=int(sys.argv[1]) if len(sys.argv)>1 else 2026
RC_CUR=sys.argv[2] if len(sys.argv)>2 else '11014'
RC_PREV=sys.argv[3] if len(sys.argv)>3 else '11012'
CKEY=sys.argv[4] if len(sys.argv)>4 else '202609'
REV_ID=['ifrs-full_Revenue','dart_Revenue'];REV_NM=['매출액','수익(매출액)','영업수익','매출','순매출액']
OP_ID=['dart_OperatingIncomeLoss'];OP_NM=['영업이익','영업이익(손실)','영업손익']
REV=(REV_ID,REV_NM);OP=(OP_ID,OP_NM)
def num(s):
    try: return int(str(s).replace(',','').strip())
    except: return None
def pick(lst,ids,nms):
    L=[a for a in lst if a.get('sj_div') in('IS','CIS')]
    for i in ids:
        for a in L:
            if a.get('account_id')==i: return a
    for n in nms:
        for a in L:
            if a.get('account_nm','').replace(' ','')==n: return a
def jget(url):
    for i in range(6):
        try:
            d=json.load(urllib.request.urlopen(url,timeout=40))
            if d.get('status')=='020': time.sleep(5*(i+1));continue
            return d
        except Exception: time.sleep(3)
    return {'status':'ERR'}
def stmt(cc,year,rc,fs):
    d=jget("https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"+urllib.parse.urlencode(dict(crtfc_key=K,corp_code=cc,bsns_year=year,reprt_code=rc,fs_div=fs)))
    return d['list'] if d.get('status')=='000' and d.get('list') else None
def stmt_any(cc,year,rc,pref):
    for fs in[pref]+[x for x in('CFS','OFS') if x!=pref]:
        l=stmt(cc,year,rc,fs)
        if l: return fs,l
    return None,None
def g(cur,base): return (cur/base-1) if (cur is not None and base is not None and base>0) else None
# ---- 종목코드 -> corp_code, 당분기 보고서/잠정공시 찾기
def corp_map(codes):
    b=urllib.request.urlopen("https://opendart.fss.or.kr/api/corpCode.xml?"+urllib.parse.urlencode(dict(crtfc_key=K)),timeout=180).read()
    z=zipfile.ZipFile(io.BytesIO(b));t=z.read(z.namelist()[0]).decode('utf-8')
    m={}
    for e in re.findall(r'<list>(.*?)</list>',t,re.S):
        gg=lambda k:(re.search(rf'<{k}>(.*?)</{k}>',e,re.S) or [None,''])[1].strip()
        if gg('stock_code') in codes: m[gg('stock_code')]=gg('corp_code')
    return m
def find_filings(cc,bgn,end):
    r=jget("https://opendart.fss.or.kr/api/list.json?"+urllib.parse.urlencode(dict(crtfc_key=K,corp_code=cc,bgn_de=bgn,end_de=end,page_count=100)))
    L=r.get('list',[])
    rep=[x for x in L if re.match(r'(\[.*\])?(분기|반기)보고서',x['report_nm'].strip()) and f"{CKEY[:4]}.{CKEY[4:]}" in x['report_nm']]
    pre=[x for x in L if '잠정' in x['report_nm']]
    rep.sort(key=lambda x:x['rcept_no']);pre.sort(key=lambda x:x['rcept_no'],reverse=True);pre.sort(key=lambda x:'연결' not in x['report_nm'])
    return (rep[-1] if rep else None),pre   # pre: 연결 우선·최신순 후보 목록
UNIT={'원':1,'천원':1e3,'백만원':1e6,'억원':1e8}
def prelim(rn):
    t=D.fetch(rn)
    if not t: return None
    txt=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t)))
    pm=re.search(r'당기실적\s*(\d{4})-(\d{2})-\d{2}\s*~\s*(\d{4})-(\d{2})-\d{2}',txt)
    if not pm or f"{pm.group(3)}{pm.group(4)}"!=CKEY: return None   # 대상 분기 공시가 아님(1·2분기 잠정 등)
    u=1e6;m=re.search(r'단위\s*:\s*([가-힣]+)',txt)
    if m and m.group(1) in UNIT: u=UNIT[m.group(1)]
    def tok(s):
        s=s.replace('△','-').replace('(','-').replace(')','')
        try: return float(s.replace(',',''))
        except: return None
    out={}
    for key,lab in(('rev','매출액'),('op','영업이익')):
        i=txt.find(lab+' 당해실적')
        if i<0: return None
        seg=txt[i+len(lab)+5:i+len(lab)+200];j=seg.find('누계실적')
        cur=seg[:j].split();cum=seg[j+4:].split()
        v=dict(q3=tok(cur[0]),q2=tok(cur[1]),py=tok(cur[4]) if len(cur)>4 else None,m26=tok(cum[0]),m25=tok(cum[4]) if len(cum)>4 else None)
        for k in v:
            if v[k] is not None: v[k]*=u
        out[key]=v
    return out
def pmcap(v):
    t=0;m=re.search(r'([\d,]+)조',v)
    if m:t+=int(m.group(1).replace(',',''))*10**12
    m=re.search(r'([\d,]+)억',re.sub(r'[\d,]+조','',v))
    if m:t+=int(m.group(1).replace(',',''))*10**8
    return t
def naver(code):
    out={}
    try:
        d=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{code}/integration",timeout=20))
        out['mcap']=pmcap([x['value'] for x in d['totalInfos'] if x['code']=='marketValue'][0])
    except Exception: pass
    try:
        f=json.load(urllib.request.urlopen(f"https://m.stock.naver.com/api/stock/{code}/finance/quarter",timeout=20))['financeInfo']
        out['cflag']={t['key']:t['isConsensus'] for t in f['trTitleList']}.get(CKEY)
        nn=lambda v:float(str(v).replace(',','')) if re.fullmatch(r'-?[\d,]+(\.\d+)?',str(v)) else None
        for r in f['rowList']:
            if r['title']=='매출액': out['c_rev']=nn(r['columns'].get(CKEY,{}).get('value'))
            if r['title']=='영업이익': out['c_op']=nn(r['columns'].get(CKEY,{}).get('value'))
    except Exception as e: out['cerr']=str(e)
    return out
def ttm(v):
    if None not in(v.get('fy25'),v.get('m25'),v.get('m26'),v.get('fy24'),v.get('m24')):
        v['ttm']=v['fy25']-v['m25']+v['m26'];v['ttm_prev']=v['fy24']-v['m24']+v['m25'];v['ttm_g']=g(v['ttm'],v['ttm_prev'])
def work(w,cc,rep,pre):
    o=dict(w);o.update(naver(w['code']))
    p=None;used=None
    if not rep:
        for cand in pre:
            p=prelim(cand['rcept_no'])
            if p: used=cand;break
    if not rep and not p: o['err']='당분기 미발표(분기보고서·잠정실적 모두 없음)';return o
    if rep:
        fs,l3=stmt_any(cc,YEAR,RC_CUR,'CFS');o['src']='API';doc=None
        if not l3:
            t=D.fetch(rep['rcept_no']);doc=D.parse(t) if t else None
            if not doc: o['err']='재무 조회 불가';return o
            fs=doc[0];o['src']='원문'
        o['rcept_dt']=rep['rcept_dt']
    else:
        l3=None;doc=None;fs='CFS';o['src']='잠정';o['rcept_dt']=used['rcept_dt']
    fs2,l2=stmt_any(cc,YEAR,RC_PREV,fs);fsb,L25=stmt_any(cc,YEAR-1,RC_CUR,fs);fsc,LA=stmt_any(cc,YEAR-1,'11011',fs)
    o['fs']=fs;o['mixed']=len({x for x in(fs,fsb,fsc) if x})>1
    for key,(ids,nms) in(('rev',REV),('op',OP)):
        v=dict(q3=None,py=None,q2=None,m26=None,m25=None,m24=None,fy25=None,fy24=None)
        if o['src']=='API':
            a=pick(l3,ids,nms)
            if a: v.update(q3=num(a.get('thstrm_amount')),py=num(a.get('frmtrm_q_amount')),m26=num(a.get('thstrm_add_amount')),m25=num(a.get('frmtrm_add_amount')))
        elif o['src']=='원문':
            r=doc[2].get(key);u=doc[1]
            if r and len(r)>=4: v['q3'],v['m26'],v['py'],v['m25']=[x*u for x in r[:4]]
        else: v.update(p[key])
        if v['q2'] is None and l2:
            b=pick(l2,ids,nms)
            if b: v['q2']=num(b.get('thstrm_amount'))
        if L25:
            a=pick(L25,ids,nms)
            if a: v['m24']=num(a.get('frmtrm_add_amount'))
        if LA:
            a=pick(LA,ids,nms)
            if a: v['fy25']=num(a.get('thstrm_amount'));v['fy24']=num(a.get('frmtrm_amount'))
        v['yoy']=g(v['q3'],v['py']);v['qoq']=g(v['q3'],v['q2']);ttm(v);o[key]=v
    return o
if __name__=='__main__':
    W=json.load(open('watch.json'))
    cm=corp_map({w['code'] for w in W})
    bgn,end=f"{YEAR}0101",time.strftime('%Y%m%d')
    out=[]
    for w in W:
        cc=cm.get(w['code'])
        if not cc: out.append(dict(w,err='DART 고유번호 없음'));continue
        rep,pre=find_filings(cc,bgn,end)
        out.append(work(w,cc,rep,pre))
        o=out[-1];print(w['code'],w['name'],o.get('err') or (o['src'],o['fs'],'혼합' if o['mixed'] else ''),flush=True)
    json.dump(out,open('watch_result.json','w'),ensure_ascii=False)
