"""ttm_final.json -> TTM(최근 4분기 합산) 15% 스크리닝 md. 사용: python3 gen_ttm_md.py ttm_final.json 출력.md '2026년 3분기' """
import json,sys
src,out,title=sys.argv[1:4]
ks=sys.argv[4] if len(sys.argv)>4 else None   # ksic.json
thp=sys.argv[5] if len(sys.argv)>5 else None  # data.json(테마분석)
A=json.load(open(src));R=A['rows'];ex=A['excl']
f=lambda v:'n/a' if v is None else f"{v*100:+,.0f}%"
e=lambda v:f"{v/1e8:,.0f}"
def tbl(L):
    h="| 종목 | 코드 | 시총(억) | 3분기 구분 | TTM 매출(억) | 직전 | 증가율 | TTM 영업이익(억) | 직전 | 증가율 | 기준 |\n|---|---|--:|---|--:|--:|--:|--:|--:|--:|---|\n"
    for r in L:
        h+=f"| {r['name']}{' †' if r.get('semi')=='경계' else ''} | {r['code']} | {r['mcap']/1e8:,.0f} | {r['tag']} | {e(r['rev']['cur'])} | {e(r['rev']['prv'])} | {f(r['rev']['g'])} | {e(r['op']['cur'])} | {e(r['op']['prv'])} | {f(r['op']['g'])} | {'연결' if r['fs']=='CFS' else '별도'}{'·원문' if r['src']!='API' else ''} |\n"
    return h
P=[r for r in R if r['pass']];N=[r for r in R if not r['pass']]
s=f"# {title} 연환산(TTM) 성장 확인 — 매출·영업이익 15%↑\n\n"
s+=f"- 대상: [{title} 실적발표 스크리닝](2026-3Q_실적발표.md)에서 YoY 또는 QoQ에 해당한 {len(R)+len(ex)}곳\n"
s+="- **TTM(최근 4분기 합산)** = 직전 연도 4분기 + 올해 1~3분기. 직전 TTM = 전전년 4분기 + 직전 연도 1~3분기\n"
s+="  - 올해 TTM = FY2025 − 2025년 1~3분기 누적 + 2026년 1~3분기 누적 / 직전 TTM = FY2024 − 2024년 1~3분기 누적 + 2025년 1~3분기 누적\n"
s+="- 기준: TTM 매출액·영업이익 증가율이 **둘 다 15% 이상** (직전 TTM이 흑자일 때만 계산)\n\n"
s+=f"## 요약\n\n| 구분 | 종목 수 |\n|---|--:|\n| 확인 대상 | {len(R)+len(ex)} |\n| **TTM 둘 다 15%↑ 통과** | **{len(P)}** |\n| 미통과 | {len(N)} |\n| 비교 불가 제외 | {len(ex)} |\n\n"
s+=f"## 1. 통과 ({len(P)})\n\n"+tbl(P)+"\n"
s+=f"## 2. 미통과 ({len(N)})\n\n"+tbl(N)+"\n"
if ks or thp:
    from semi import make
    cl=make(ks,thp)
    for r in R: r['semi'],r['semi_why']=cl(r['code'],r['name'])
    P2=[r for r in P if r['semi']!='반도체'];P3=[r for r in P if r['semi']=='']
    s+=f"## 3. 반도체 제외 통과 ({len(P2)})\n\n"
    s+="분류 기준: 테마분석(`data.json`)에 테마가 있으면 \"반도체\" 포함 여부로, 없는 종목은 업종코드(KSIC 261*·29271)와 소부장 수동 분류로 판단. †는 반도체 비중이 애매해 제외하지 않은 종목(경계까지 빼면 %d곳).\n\n"%len(P3)
    s+=tbl(P2)+"\n"
    s+="제외된 반도체 통과 종목(%d): "%(len(P)-len(P2))+', '.join(r['name'] for r in P if r['semi']=='반도체')+"\n\n"
PY=[r for r in P if r['tag'] in('둘다','YoY')];P3=[r for r in P if r['tag']=='둘다']
s+=f"## 4. TTM·YoY 모두 해당 ({len(PY)})\n\n"
s+=f"TTM 통과 {len(P)}곳은 전부 YoY도 해당하므로 1번 목록과 같음(QoQ만 해당한 종목은 TTM에서 모두 탈락). 반도체 제외 시 {len([r for r in PY if r.get('semi')!='반도체'])}곳.\n\n"
s+=f"## 5. TTM·YoY·QoQ 모두 해당 ({len(P3)})\n\n"+tbl(P3)+"\n"
X3=[r for r in P3 if r.get('semi')!='반도체']
s+=f"### 반도체 제외 ({len(X3)})\n\n"+tbl(X3)+"\n"
s+="## 비교 불가\n\n"+('\n'.join(f"- {n}({c}): {w}" for n,c,w in ex) if ex else '없음')+"\n\n"
s+="## 주의\n\n- 증가율 n/a는 직전 TTM 영업이익이 적자(흑자전환 포함)라 증가율을 계산할 수 없는 경우로, 통과에 넣지 않음\n- 연간 보고서(FY2025·FY2024)와 2025년 3분기 보고서 값을 합산하므로, 이후 재작성(합병·분할·회계변경)된 기업은 왜곡될 수 있음\n- 3분기 구분: 둘다 = YoY·QoQ 모두 해당 / YoY·QoQ = 해당 항목만\n- 유바이오로직스는 2026년만 연결로 바뀌어 별도 기준으로 통일해 계산\n- 한화엔진은 2024년 1~3분기만 별도 값(연결과 동일 범위) 사용\n"
open(out,'w').write(s);print(len(P),len(N),len(ex))
