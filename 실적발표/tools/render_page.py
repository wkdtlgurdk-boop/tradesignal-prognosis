"""페이지 템플릿(per_page.html)의 {{...}} 자리를 채워 아티팩트 files/index.html 문서용 JSON 을 만든다.
사용: python3 render_page.py per_page.html out_doc.json --quarter 3분기 --asof 2026-11-18 --today 2026-11-21
  {{분기}} {{기준일}}(MM/DD) {{기준일_한글}}(M월 D일) {{정리일_한글}}(YYYY년 M월 D일)
  out_doc.json = {"text": ..., "edit": {"via":"claude","at": 지금(UTC)}}  (ArtifactData set/update 의 file_path 로 쓴다)
  --html 로 출력하면 문서가 아니라 렌더된 HTML 만 쓴다(검증용)."""
import sys,json,argparse,datetime
ap=argparse.ArgumentParser();ap.add_argument('tpl');ap.add_argument('out')
ap.add_argument('--quarter',required=True);ap.add_argument('--asof',required=True);ap.add_argument('--today',required=True);ap.add_argument('--html',action='store_true')
a=ap.parse_args()
d=lambda s:datetime.date.fromisoformat(s)
asof,today=d(a.asof),d(a.today)
vals={'{{분기}}':a.quarter,'{{기준일}}':f'{asof.month}/{asof.day}','{{기준일_한글}}':f'{asof.month}월 {asof.day}일','{{정리일_한글}}':f'{today.year}년 {today.month}월 {today.day}일'}
t=open(a.tpl,encoding='utf-8').read()
for k,v in vals.items(): t=t.replace(k,v)
left=[x for x in ('{{',) if x in t]
if left: sys.exit('치환되지 않은 자리표시자가 남았다')
if a.html: open(a.out,'w',encoding='utf-8').write(t)
else:
    now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    json.dump({'text':t,'edit':{'via':'claude','at':now}},open(a.out,'w',encoding='utf-8'),ensure_ascii=False)
print('ok',a.out,len(t))
