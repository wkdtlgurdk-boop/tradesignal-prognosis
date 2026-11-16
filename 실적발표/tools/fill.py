"""API 에 재무 데이터가 아직 없는 종목(최근 접수분)을 보고서 원문(document.xml)에서 파싱해 채운다 -> fin3.json
fin2.json 읽음. 병렬 6개, 종목별 결과를 fill_cache.json 에 계속 저장(중간에 끊겨도 이어서 실행 가능).
DART 는 마감 직후 문서 다운로드가 연결당 느려서(건당 수십 초) 병렬로 받는다."""
import json,time,os,threading,urllib.request,urllib.parse,concurrent.futures as cf
import fin,docparse as D
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'retry.py')).read().split("fin.call=call")[0].split("import fin")[1])  # call() with 020 backoff
fin.call=call
res=json.load(open('fin2.json'))
CP='fill_cache.json'
cache=json.load(open(CP)) if os.path.exists(CP) else {}
lock=threading.Lock()
def one(x):
    code=x['code']
    if code in cache: return
    t=D.fetch(x['rcept_no']);p=D.parse(t) if t else None
    if not p:
        out={'err':'원문 미생성/파싱불가' if not t else '파싱불가'}
    else:
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
            out[key]=dict(q3=v[0]*u,q3_py=v[2]*u if len(v)>=4 else None,q2=q2,q3_alt=None,acc='doc')
        out['fs']=fs;out['src']='원문파싱'
    with lock:
        cache[code]=out
        json.dump(cache,open(CP,'w'),ensure_ascii=False)
todo=[x for x in res if x.get('err')]
print('원문 파싱 대상',len(todo),'이미 처리',sum(1 for x in todo if x['code'] in cache),flush=True)
with cf.ThreadPoolExecutor(int(os.environ.get('FILL_THREADS','6'))) as ex: list(ex.map(one,todo))
for x in res:
    if x['code'] in cache and x.get('err'):
        out=cache[x['code']]
        if 'err' in out: x['err']=out['err']
        else: x.update(out);x.pop('err',None)
json.dump(res,open('fin3.json','w'),ensure_ascii=False)
print([(x['name'],x['err']) for x in res if x.get('err')])
print(sum(1 for x in res if x.get('src')),'parsed from doc')
