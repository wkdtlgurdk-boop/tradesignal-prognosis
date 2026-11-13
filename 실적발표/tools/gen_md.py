"""analysis.json -> 분기 실적발표 md 생성. 사용: python3 gen_md.py analysis.json 출력.md '2026년 3분기' '11/09~11/13' """
import json,sys,collections
src,out,title,period=sys.argv[1:5]
ks=sys.argv[5] if len(sys.argv)>5 else None   # ksic.json
thp=sys.argv[6] if len(sys.argv)>6 else None  # data.json(테마분석)
csp=sys.argv[7] if len(sys.argv)>7 else None  # cons.json(컨센서스)
tfp=sys.argv[8] if len(sys.argv)>8 else None  # ttm_final.json
A=json.load(open(src));rows=sorted(A['rows'],key=lambda d:-d['mcap']);excl=A['excl']
f=lambda v:'n/a' if v is None else f"{v*100:+,.0f}%"
e=lambda v:'-' if v is None else f"{v/1e8:,.0f}"
def tbl(L,star=True):
    h="| 종목 | 코드 | 시총(억) | 매출(억) | 매출 YoY | 매출 QoQ | 영업이익(억) | 영업이익 YoY | 영업이익 QoQ | 기준 |\n|---|---|--:|--:|--:|--:|--:|--:|--:|---|\n"
    for d in L:
        nm=d['name']+(' ★' if star and d['both'] else '')+(' †' if d.get('semi')=='경계' else '')
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
if ks or thp:
    from semi import make
    cl=make(ks,thp)
    for d in rows: d['semi'],d['semi_why']=cl(d['code'],d['name'])
    xs=lambda L:[d for d in L if d['semi']!='반도체']
    xb=lambda L:[d for d in L if d['semi']=='']
    NY,NQ,NB=xs(Y),xs(Q),xs(B)
    s+="## 반도체 제외\n\n"
    s+="분류 기준: 테마분석(`data.json`)에 테마가 있으면 \"반도체\" 포함 여부로, 없는 종목은 업종코드(KSIC 261*·29271)와 소부장 수동 분류로 판단. †는 반도체 비중이 애매해 제외하지 않은 종목.\n\n"
    s+="| 구분 | 전체 | 반도체 제외 | 반도체·경계 제외 |\n|---|--:|--:|--:|\n"
    for lab,L in(('분석 대상',rows),('YoY 해당',Y),('QoQ 해당',Q),('YoY·QoQ 모두 해당',B)):
        s+=f"| {lab} | {len(L)} | {len(xs(L))} | {len(xb(L))} |\n"
    s+=f"\n### 반도체 제외 · YoY·QoQ 모두 해당 ({len(NB)})\n\n"+tbl(NB,False)+"\n"
    s+=f"### 반도체 제외 · QoQ 해당 ({len(NQ)})\n\n★ = YoY도 해당\n\n"+tbl(NQ)+"\n"
    s+=f"### 반도체 제외 · YoY 해당 ({len(NY)})\n\n★ = QoQ도 해당\n\n"+tbl(NY)+"\n"
    ex=[d for d in rows if d['semi']=='반도체' and (d['yoy'] or d['qoq'])]
    s+=f"### 제외된 반도체 종목 ({len(ex)}, YoY 또는 QoQ 해당분)\n\n"+', '.join(f"{d['name']}({'테마' if d['semi_why'].startswith('테마') else ('업종코드' if d['semi_why'].startswith('KSIC') else '수동')})" for d in ex)+"\n\n"
if csp:
    CONS={r['code']:r for r in json.load(open(csp))}
    TP={r['code'] for r in json.load(open(tfp))['rows'] if r['pass']} if tfp else set()
    CR=[]
    for d in rows:
        if not(d['yoy'] or d['qoq']): continue
        c=CONS.get(d['code'],{})
        if not(c.get('flag')=='Y' and c.get('rev') is not None and c.get('op') is not None): continue
        sr=d['rev']/1e8/c['rev']-1 if c['rev']>0 else None
        so=d['op']/1e8/c['op']-1 if c['op']>0 else None
        CR.append(dict(d=d,cr=c['rev'],co=c['op'],sr=sr,so=so,ttm=d['code'] in TP))
    CR.sort(key=lambda x:(x['so'] is None,-(x['so'] or 0)))
    def ctbl(L):
        h="| 종목 | 코드 | 시총(억) | TTM | 실제 매출(억) | 컨센 매출(억) | 매출 서프라이즈 | 실제 영업이익(억) | 컨센 영업이익(억) | 영업이익 서프라이즈 | 판정 |\n|---|---|--:|---|--:|--:|--:|--:|--:|--:|---|\n"
        for x in L:
            d=x['d']
            v='매출·영업 상회' if (x['sr'] is not None and x['so'] is not None and x['sr']>=0 and x['so']>=0) else ('영업만 상회' if (x['so'] or -1)>=0 else ('매출만 상회' if (x['sr'] or -1)>=0 else '하회'))
            h+=f"| {d['name']}{' †' if d.get('semi')=='경계' else ''}{' (반도체)' if d.get('semi')=='반도체' else ''} | {d['code']} | {d['mcap']/1e8:,.0f} | {'O' if x['ttm'] else ''} | {e(d['rev'])} | {x['cr']:,.0f} | {f(x['sr'])} | {e(d['op'])} | {x['co']:,.0f} | {f(x['so'])} | {v} |\n"
        return h
    T49=[x for x in CR if x['ttm']]
    nb=lambda L:sum(1 for x in L if x['sr'] is not None and x['so'] is not None and x['sr']>=0 and x['so']>=0)
    s+="## 컨센서스 대비 (영업이익 서프라이즈 순)\n\n"
    s+="컨센서스는 네이버증권(FnGuide) 당분기 컨센서스(조회 시점 최신). 먼저 실적을 낸 기업은 발표 후 조정분이 섞였을 수 있고, 컨센서스가 없는 종목은 제외했다. 전체 종목(컨센 없는 곳 포함)은 엑셀 `컨센대비(86)`·`컨센대비(TTM49)` 시트.\n\n"
    s+=f"- YoY 또는 QoQ 해당 대상 중 컨센서스 확보 {len(CR)}곳 → 매출·영업이익 모두 상회 {nb(CR)}곳\n- TTM 통과 중 컨센서스 확보 {len(T49)}곳 → 매출·영업이익 모두 상회 {nb(T49)}곳\n\n"
    s+=f"### TTM 통과 종목 ({len(T49)})\n\n"+ctbl(T49)+"\n"
    s+=f"### YoY·QoQ 해당 대상 상위 20 / 하위 5 (전체 {len(CR)})\n\n"+ctbl(CR[:20])+"\n...\n\n"+ctbl(CR[-5:])+"\n"
s+="## 주의·한계\n\n"
s+="- 접수일 기준 이번 주(월~금) 공시만 포함. 법정 제출 마감이 토요일이면 다음 영업일로 넘어가므로 마감 직후 월요일 제출분은 다음 갱신 때 추가 필요.\n"
s+="- 11/13 접수분은 DART 재무 API에 아직 반영되지 않아 **보고서 원문을 직접 파싱**한 종목이 있음(표의 '원문' 표기). 파서는 API 값과 대조 검증함.\n"
s+="- 직전 분기(2분기)는 반기보고서 값 사용. 이후 재작성(합병·분할 등)된 기업은 QoQ가 왜곡될 수 있음.\n"
s+="- 지분법손익이 매출에 섞이는 지주사 등은 계정 라벨 차이로 누락될 수 있음.\n"
s+="- 제외: "+', '.join(f"{n}({c})" for n,c,_ in excl)+"\n"
open(out,'w').write(s)
print(len(s))
