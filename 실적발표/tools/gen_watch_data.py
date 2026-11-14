"""watch_result.json -> 아티팩트용 데이터 파일 watch.json ({rows, meta}, 단위 억원). 개인 정보 → 저장소에 올리지 말 것.
사용: python3 gen_watch_data.py watch_result.json watch.json
이어서: Artifact publish(asset:true, file_path=watch.json)로 올리고 datasets/watch 의 source.url 을 새 /_blob/<id> 로 바꾼다.
페이지 코드는 watch_page.html (종목 정보 없음)."""
import json,sys,os
src,out=sys.argv[1:3]
R=json.load(open(src))
b=lambda v:None if v is None else round(v/1e8,1)
rows=[]
for o in R:
    r=dict(name=o['name'],code=o['code'],group=o['group'],mcap=b(o.get('mcap')))
    if o.get('err'):
        r.update(status='미발표',src=None,fs=None,note='당분기 분기보고서·잠정실적 공시 없음(마감일이 주말이면 월요일 제출 가능)');rows.append(r);continue
    rv,op=o['rev'],o['op'];nb=[]
    if o['src']=='잠정': nb.append('잠정실적 기준')
    if o['src']=='원문': nb.append('보고서 원문 파싱')
    if o.get('mixed'): nb.append('연결·별도 기준 혼합(TTM 신뢰 낮음)')
    if o.get('cflag')=='N': nb.append('컨센서스가 실제 값으로 갱신됨')
    if o['group']=='보유': nb.append('매매일지 기준 임시 목록')   # 한투 API 목록으로 바꾸면 이 줄을 지운다
    cons=o.get('cflag')=='Y' and o.get('c_rev') is not None and o.get('c_op') is not None
    r.update(status='발표',src=o['src'],fs='연결' if o['fs']=='CFS' else '별도',rcept_dt=f"{o['rcept_dt'][:4]}-{o['rcept_dt'][4:6]}-{o['rcept_dt'][6:]}",
      rev=b(rv['q3']),rev_py=b(rv['py']),rev_q2=b(rv['q2']),op=b(op['q3']),op_py=b(op['py']),op_q2=b(op['q2']),
      ttm_rev=b(rv.get('ttm')),ttm_rev_prev=b(rv.get('ttm_prev')),ttm_op=b(op.get('ttm')),ttm_op_prev=b(op.get('ttm_prev')),
      mixed=bool(o.get('mixed')),c_rev=o['c_rev'] if cons else None,c_op=o['c_op'] if cons else None,note='; '.join(nb) or None)
    rows.append(r)
code=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'watch_check.py')).read()
meta=[{"label":"watch_check.py","value":code,"type":"code","lang":"python"},
 {"label":"Input","value":"DART OpenAPI(분기·반기·사업보고서 재무, 영업(잠정)실적 공정공시), 네이버 모바일 증권(시총·분기 컨센서스). 금액 단위 억원"}]
json.dump(dict(rows=rows,meta=meta),open(out,'w'),ensure_ascii=False);print(len(rows),'종목 ->',out)
