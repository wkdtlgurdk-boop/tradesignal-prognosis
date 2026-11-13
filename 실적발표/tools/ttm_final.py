import json,sys
T=json.load(open('ttm.json'));A={d['code']:d for d in json.load(open('analysis.json'))['rows']}
P=json.load(open('patch.json'))
for t in T:
    if t['code']=='082740':
        # 연결(2026 3Q 연결, 연간 연결) + 2024 9M은 별도 보완
        t['rev']['m24']=875936605980; t['op']['m24']=53336713981
    if t['code']=='206650':
        t['rev']=P['uby']['rev'];t['op']=P['uby']['op'];t['fs']='OFS'
rows=[];excl=[]
for t in T:
    a=A[t['code']];r=dict(code=t['code'],name=t['name'],mcap=a['mcap'],fs=t['fs'],src=t['src'],
        tag='둘다' if a['both'] else ('YoY' if a['yoy'] else 'QoQ'))
    if t['code']=='499790': excl.append((t['name'],t['code'],'2024년 연결 규모가 미미(FY24 연결 매출 383억→FY25 4,817억)해 직전 TTM 비교 불가'));continue
    bad=False
    for k in('rev','op'):
        v=t[k]
        if any(v[x] is None for x in('m26','m25','m24','fy25','fy24')): bad=True;break
        cur=v['fy25']-v['m25']+v['m26'];prv=v['fy24']-v['m24']+v['m25']
        r[k]=dict(cur=cur,prv=prv,g=(cur/prv-1) if prv>0 else None)
    if bad: excl.append((t['name'],t['code'],'데이터 누락'));continue
    r['pass']=all(r[k]['g'] is not None and r[k]['g']>=.15 for k in('rev','op'))
    rows.append(r)
rows.sort(key=lambda r:-r['mcap'])
json.dump(dict(rows=rows,excl=excl),open('ttm_final.json','w'),ensure_ascii=False)
print(len(rows),'통과',sum(r['pass'] for r in rows),'제외',excl)
