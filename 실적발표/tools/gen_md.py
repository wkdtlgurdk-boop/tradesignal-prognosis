"""analysis.json -> 분기 실적발표 md 생성. 사용: python3 gen_md.py analysis.json 출력.md '2026년 3분기' '11/09~11/13' """
import json,sys,collections
src,out,title,period=sys.argv[1:5]
A=json.load(open(src));rows=sorted(A['rows'],key=lambda d:-d['mcap']);excl=A['excl']
f=lambda v:'n/a' if v is None else f"{v*100:+,.0f}%"
e=lambda v:'-' if v is None else f"{v/1e8:,.0f}"
def tbl(L,star=True):
    h="| 종목 | 코드 | 시총(억) | 매출(억) | 매출 YoY | 매출 QoQ | 영업이익(억) | 영업이익 YoY | 영업이익 QoQ | 기준 |\n|---|---|--:|--:|--:|--:|--:|--:|--:|---|\n"
    for d in L:
        nm=d['name']+(' ★' if star and d['both'] else '')
        h+=f"| {nm} | {d['code']} | {d['mcap']/1e8:,.0f} | {e(d['rev'])} | {f(d['rev_yoy'])} | {f(d['rev_qoq'])} | {e(d['op'])} | {f(d['op_yoy'])} | {f(d['op_qoq'])} | {d['fs']}{'·원문' if d['src']!='API' else ''} |\n"
    return h
Y=[d for d in rows if d['yoy']];Q=[d for d in rows if d['qoq']];B=[d for d in rows if d['both']]
TY=[d for d in rows if d['op_turn_yoy'] and d['rev_yoy'] is not None and d['rev_yoy']>=.2]
TQ=[d for d in rows if d['op_turn_qoq'] and d['rev_qoq'] is not None and d['rev_qoq']>=.2]
s=f"# {title} 실적발표 스크리닝 ({period} 접수분)\n\n"
s+=f"- 대상: 이번 주 DART에 분기보고서를 낸 상장사 중 **시총 2,000억원 이상** {len(rows)+len(excl)}곳 (금융업 등 계정 부재로 제외 {len(excl)}곳 → 분석 {len(rows)}곳)\n"
s+="- 기준: 매출액과 영업이익이 **둘 다** 20% 이상 증가 (당분기 3개월 기준, 비교 기준값이 흑자일 때만)\n"
s+="  - **YoY**: 전년 동기(3분기) 대비 / **QoQ**: 직전 분기(2분기) 대비\n"
s+="- 재무: 연결 우선, 없으면 별도. 시총: 네이버증권 기준 작성일 종가\n\n"
s+=f"## 요약\n\n| 구분 | 종목 수 |\n|---|--:|\n| YoY 해당 | {len(Y)} |\n| QoQ 해당 | {len(Q)} |\n| **YoY·QoQ 모두 해당 ★** | **{len(B)}** |\n\n"
s+=f"## 1. YoY·QoQ 모두 해당 ({len(B)})\n\n"+tbl(B,False)+"\n"
s+=f"## 2. QoQ 해당 ({len(Q)})\n\n★ = YoY도 해당\n\n"+tbl(Q)+"\n"
s+=f"## 3. YoY 해당 ({len(Y)})\n\n★ = QoQ도 해당\n\n"+tbl(Y)+"\n"
s+="## 참고: 영업이익 흑자전환 (매출 20%↑, 비교 기준 적자라 증가율 계산 불가 → 위 목록에서 제외)\n\n"
for nm,L in(('YoY 흑자전환',TY),('QoQ 흑자전환',TQ)):
    s+=f"**{nm}** ({len(L)}): "+(', '.join(f"{d['name']}({d['code']})" for d in L) if L else '없음')+"\n\n"
s+="## 주의·한계\n\n"
s+="- 접수일 기준 이번 주(월~금) 공시만 포함. 법정 제출 마감이 토요일이면 다음 영업일로 넘어가므로 마감 직후 월요일 제출분은 다음 갱신 때 추가 필요.\n"
s+="- 11/13 접수분은 DART 재무 API에 아직 반영되지 않아 **보고서 원문을 직접 파싱**한 종목이 있음(표의 '원문' 표기). 파서는 API 값과 대조 검증함.\n"
s+="- 직전 분기(2분기)는 반기보고서 값 사용. 이후 재작성(합병·분할 등)된 기업은 QoQ가 왜곡될 수 있음.\n"
s+="- 지분법손익이 매출에 섞이는 지주사 등은 계정 라벨 차이로 누락될 수 있음.\n"
s+="- 제외: "+', '.join(f"{n}({c})" for n,c,_ in excl)+"\n"
open(out,'w').write(s)
print(len(s))
