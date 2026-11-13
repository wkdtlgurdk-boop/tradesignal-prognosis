import json,time,urllib.request,urllib.parse
import fin,docparse as D
exec(open('retry.py').read().split("fin.call=call")[0].split("import fin")[1])  # reuse call w/ backoff
fin.call=call
res=json.load(open('fin2.json'))
for x in res:
    if not x.get('err'): continue
    t=D.fetch(x['rcept_no']); p=D.parse(t) if t else None
    if not p: x['err']='원문 미생성/파싱불가' if not t else '파싱불가'; continue
    fs,u,d=p
    fs2,l2=fin.getfs(x['corp_code'],fin.RC_PREV)
    out={}
    for key,ids,nms in(('rev',fin.REV_ID,fin.REV_NM),('op',fin.OP_ID,fin.OP_NM)):
        v=d.get(key)
        if not v: out[key]=None;continue
        q2=None
        if l2:
            b=fin.pick(l2,ids,nms)
            if b: q2=fin.num(b.get('thstrm_amount'))
        q3=v[0]*u; py=v[2]*u if len(v)>=4 else None
        out[key]=dict(q3=q3,q3_py=py,q2=q2,q3_alt=None,acc='doc')
    x.update(out); x['fs']=fs; x['src']='원문파싱'; x.pop('err')
json.dump(res,open('fin3.json','w'),ensure_ascii=False)
print([(x['name'],x['err']) for x in res if x.get('err')])
print(sum(1 for x in res if x.get('src')),'parsed from doc')
