"""FnGuide(wcomp) 컨센서스 페이지의 연도별 PER·EPS(2026E~2028E)를 수집 -> per_fng.json
사용: python3 fng_fetch.py stocks.json   (rows[].code)"""
import sys,re,json,time,urllib.request,concurrent.futures as cf
S=json.load(open(sys.argv[1]))['rows']
codes=[r['code'] for r in S]
UA='Mozilla/5.0 (X11; Linux x86_64)'
def num(v):
    try: return float(v)
    except: return None
def one(code):
    url=f"https://wcomp.fnguide.com/CompanyInfo/Consensus?cmp_cd={code}"
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA})
            t=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore')
            break
        except Exception as e: t=None;time.sleep(2)
    if not t: return dict(code=code,err='접속 실패')
    m=re.search(r'<title>(.*?)</title>',t,re.S);title=re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
    if f'({code})' not in title: return dict(code=code,err='종목 불일치: '+title[:40])
    i=t.find('perforTrend:')
    if i<0: return dict(code=code,title=title,err='컨센서스 표 없음')
    j=t.find('{',i);d=0
    for k in range(j,len(t)):
        if t[k]=='{':d+=1
        elif t[k]=='}':
            d-=1
            if d==0:break
    P=json.loads(t[j:k+1])
    hdr=P['header'] if isinstance(P['header'],list) else json.loads(P['header'].replace("'",'"'))
    col={h['YYMM']:h['CD'] for h in hdr if h.get('YYMM')}
    rows={r['NAME'].strip():r for r in P['data']}
    o=dict(code=code,title=title,cols=list(col))
    for yr in('2026','2027','2028'):
        cd=next((c for y,c in col.items() if y.startswith(yr)),None)
        if cd:
            o['per'+yr]=num(rows.get('PER',{}).get(cd));o['eps'+yr]=num(rows.get('EPS',{}).get(cd));o['ni'+yr]=num(rows.get('당기순이익(지배)',{}).get(cd))
            o['ym'+yr]=next(y for y,c in col.items() if c==cd)
    return o
res=[]
with cf.ThreadPoolExecutor(4) as ex:
    def safe(c):
        time.sleep(0.2)
        try: return one(c)
        except Exception as e: return dict(code=c,err='파싱 오류: '+repr(e)[:60])
    for r in ex.map(safe,codes): res.append(r)
json.dump(res,open('per_fng.json','w'),ensure_ascii=False)
import collections
print('완료',len(res),'오류',collections.Counter(r.get('err') for r in res),'2027E PER 있음',sum(1 for r in res if r.get('per2027') is not None),'2027E EPS 있음',sum(1 for r in res if r.get('eps2027') is not None))
