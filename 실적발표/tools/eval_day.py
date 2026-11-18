import json,sys
sys.path.insert(0,'/home/user/tradesignal-prognosis/실적발표/tools')
from semi import make
cl=make('ksic.json','/home/user/tradesignal-prognosis/data.json')
A={d['code']:d for d in json.load(open('analysis.json'))['rows']}
T={r['code']:r for r in json.load(open('ttm_final.json'))['rows']}
C={r['code']:r for r in json.load(open('cons.json'))}
CH=json.load(open('chart_all.json'))
g=lambda a,b:(a/b-1) if (a is not None and b is not None and b>0) else None
mn=lambda x,y:min(x,y) if (x is not None and y is not None) else None
P=[]
for c,d in A.items():
    if not(d['yoy'] or d['qoq']): continue
    t=T.get(c);k=C.get(c,{});cons=k.get('flag')=='Y' and k.get('rev') is not None and k.get('op') is not None
    e=dict(code=c,name=d['name'],mcap=d['mcap'],semi=cl(c,d['name'])[0],both=d['both'])
    e['m_yoy']=mn(d['rev_yoy'],d['op_yoy']);e['m_qoq']=mn(d['rev_qoq'],d['op_qoq'])
    e['m_ttm']=mn(g(t['rev']['cur'],t['rev']['prv']),g(t['op']['cur'],t['op']['prv'])) if t else None
    e['yoy']=bool(d['yoy']);e['qoq']=bool(d['qoq']);e['ttm']=bool(t and t['pass'])
    e['sur_rev']=(d['rev']/1e8/k['rev']-1) if cons and k['rev']>0 else None
    e['sur_op']=(d['op']/1e8/k['op']-1) if cons and k['op']>0 else None
    e['cons']=(d['rev']/1e8>=k['rev'] and d['op']/1e8>=k['op']) if cons else None
    ch=CH.get(c);e['d_hi']=ch['d_hi'] if ch else None;e['chart']=bool(ch and ch['d_hi']>=-0.05);e['chart_days']=ch['days'] if ch else None
    e['passes']=sum(bool(x) for x in(e['yoy'],e['qoq'],e['ttm'],e['cons'],e['chart']))
    P.append(e)
N=len(P)
for k in('yoy','qoq','ttm'):
    for e in P:
        m=e['m_'+k];e['p_'+k]=0 if m is None else N-sum(1 for x in P if x['m_'+k] is not None and x['m_'+k]>m)
for e in P: e['tot']=e['p_yoy']+e['p_qoq']+e['p_ttm']
json.dump(P,open('eval_day.json','w'),ensure_ascii=False)
f=lambda v:'—' if v is None else f"{v*100:+.0f}%"
mk=lambda b:'O' if b else ('—' if b is None else 'X')
tag=lambda e:' [반도체]' if e['semi']=='반도체' else (' [경계]' if e['semi']=='경계' else '')
print('대상',N,'| 둘다',sum(e['both'] for e in P),'TTM통과',sum(e['ttm'] for e in P),'컨센상회',sum(1 for e in P if e['cons']),'차트5%',sum(e['chart'] for e in P))
import collections
print('통과개수 분포',sorted(collections.Counter(e['passes'] for e in P).items()))
key=lambda e:(-e['passes'],-e['tot'])
def show(L,title,k):
    print('==',title)
    for e in sorted(L,key=key)[:k]:
        print(f"{e['name']:10s}{tag(e)} 시총{e['mcap']/1e8:,.0f}억 통과{e['passes']} 종합{e['tot']} | YoY{mk(e['yoy'])}{f(e['m_yoy'])} QoQ{mk(e['qoq'])}{f(e['m_qoq'])} TTM{mk(e['ttm'])}{f(e['m_ttm'])} 컨센{mk(e['cons'])}{f(e['sur_rev'])}/{f(e['sur_op'])} 차트{mk(e['chart'])}{f(e['d_hi'])}")
show(P,'다섯 기준 통과 상위',15)
show([e for e in P if e['semi']!='반도체'],'반도체 제외 상위',12)
print('둘다(YoY·QoQ):',[e['name'] for e in P if e['both']])
print('5/5:',[e['name'] for e in P if e['passes']==5])
