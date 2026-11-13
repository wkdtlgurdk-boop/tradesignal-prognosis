import json,math,sys
src=sys.argv[1] if len(sys.argv)>1 else 'fin3.json'
res=json.load(open(src))
TH=0.20
def g(cur,base):
    if cur is None or base is None: return None
    if base>0: return cur/base-1
    return None
def fix_q2(q3,q2):
    # 원문 파싱분의 단위 불일치 보정: q3/q2 가 비정상이면 10^3 단위로 보정
    if q3 is None or q2 in(None,0): return q2
    for s in(1,1e3,1e6,1e-3,1e-6):
        r=q3/(q2*s) if q2*s else 0
        if 0.05<abs(r)<20: return q2*s
    return q2
rows=[];excl=[]
for x in res:
    if x.get('err'): excl.append((x['name'],x['code'],x['err']));continue
    R,O=x.get('rev'),x.get('op')
    if not R or not O: excl.append((x['name'],x['code'],'매출/영업이익 계정 없음(금융업 등)'));continue
    q2r=fix_q2(R['q3'],R['q2']) if x.get('src') else R['q2']
    q2o=fix_q2(O['q3'],O['q2']) if x.get('src') else O['q2']
    d=dict(name=x['name'],code=x['code'],mcap=x['mcap'],dt=x['rcept_dt'],fs='연결' if x['fs']=='CFS' else '별도',
        rev=R['q3'],op=O['q3'],rev_py=R['q3_py'],op_py=O['q3_py'],rev_q2=q2r,op_q2=q2o,
        rev_yoy=g(R['q3'],R['q3_py']),op_yoy=g(O['q3'],O['q3_py']),
        rev_qoq=g(R['q3'],q2r),op_qoq=g(O['q3'],q2o),src=x.get('src','API'))
    # 흑자전환
    d['op_turn_yoy']=(O['q3_py'] is not None and O['q3_py']<=0 and O['q3']>0)
    d['op_turn_qoq']=(q2o is not None and q2o<=0 and O['q3']>0)
    rows.append(d)
def ok(a,b): return a is not None and b is not None and a>=TH and b>=TH
for d in rows:
    d['yoy']=ok(d['rev_yoy'],d['op_yoy']); d['qoq']=ok(d['rev_qoq'],d['op_qoq'])
    d['both']=d['yoy'] and d['qoq']
json.dump(dict(rows=rows,excl=excl),open('analysis.json','w'),ensure_ascii=False)
print('분석',len(rows),'제외',len(excl),'YoY',sum(d['yoy'] for d in rows),'QoQ',sum(d['qoq'] for d in rows),'둘다',sum(d['both'] for d in rows))
