"""analysis.json + ttm_final.json -> 분기 실적발표 엑셀. 사용: python3 gen_xlsx.py analysis.json ttm_final.json 출력.xlsx '2026년 3분기' """
import json,sys
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter as L
an,tt,out,title=sys.argv[1:5]
A=json.load(open(an));TT=json.load(open(tt))
rows=sorted(A['rows'],key=lambda d:-d['mcap'])
FN='Arial'
def font(**k): return Font(name=FN,size=10,**k)
HF=PatternFill('solid',fgColor='1F3864');HFont=Font(name=FN,size=10,bold=True,color='FFFFFF')
YEL=PatternFill('solid',fgColor='FFFF00');GRN=PatternFill('solid',fgColor='E2EFDA')
thin=Side(style='thin',color='BFBFBF');BD=Border(left=thin,right=thin,top=thin,bottom=thin)
wb=Workbook();ws0=wb.active;ws0.title='요약'
def b(v): return None if v is None else round(v/1e8,1)
def header(ws,cols,r=1):
    for i,c in enumerate(cols,1):
        x=ws.cell(r,i,c);x.font=HFont;x.fill=HF;x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True);x.border=BD
    ws.row_dimensions[r].height=32
def perf_sheet(name,data):
    ws=wb.create_sheet(name)
    cols=['종목','코드','시총(억)','매출(억)','전년동기 매출(억)','전분기 매출(억)','영업이익(억)','전년동기 영업이익(억)','전분기 영업이익(억)','매출 YoY','매출 QoQ','영업이익 YoY','영업이익 QoQ','YoY 해당','QoQ 해당','구분','재무 기준','접수일']
    header(ws,cols)
    for i,d in enumerate(data,2):
        vals=[d['name'],d['code'],b(d['mcap']),b(d['rev']),b(d['rev_py']),b(d['rev_q2']),b(d['op']),b(d['op_py']),b(d['op_q2'])]
        for j,v in enumerate(vals,1): ws.cell(i,j,v)
        ws.cell(i,10,f'=IF(N(E{i})>0,D{i}/E{i}-1,"n/a")');ws.cell(i,11,f'=IF(N(F{i})>0,D{i}/F{i}-1,"n/a")')
        ws.cell(i,12,f'=IF(N(H{i})>0,G{i}/H{i}-1,"n/a")');ws.cell(i,13,f'=IF(N(I{i})>0,G{i}/I{i}-1,"n/a")')
        ws.cell(i,14,f'=IF(AND(ISNUMBER(J{i}),ISNUMBER(L{i})),IF(AND(J{i}>=\'요약\'!$C$5,L{i}>=\'요약\'!$C$5),"O",""),"")')
        ws.cell(i,15,f'=IF(AND(ISNUMBER(K{i}),ISNUMBER(M{i})),IF(AND(K{i}>=\'요약\'!$C$5,M{i}>=\'요약\'!$C$5),"O",""),"")')
        ws.cell(i,16,f'=IF(AND(N{i}="O",O{i}="O"),"둘다",IF(N{i}="O","YoY",IF(O{i}="O","QoQ","")))')
        ws.cell(i,17,('연결' if d['fs']=='연결' else '별도')+('·원문' if d['src']!='API' else ''))
        ws.cell(i,18,f"{d['dt'][:4]}-{d['dt'][4:6]}-{d['dt'][6:]}")
        for j in range(1,19):
            c=ws.cell(i,j);c.font=font();c.border=BD
            if j in(3,4,5,6,7,8,9):c.number_format='#,##0;(#,##0);-'
            if 10<=j<=13:c.number_format='0%;-0%;0%';c.alignment=Alignment(horizontal='right')
            if j>=14:c.alignment=Alignment(horizontal='center')
        if d['both']: 
            for j in(1,2): ws.cell(i,j).fill=GRN
    for j,w in enumerate([22,9,11,11,12,12,12,13,13,9,9,11,11,8,8,8,10,11],1): ws.column_dimensions[L(j)].width=w
    ws.freeze_panes='C2';ws.auto_filter.ref=f"A1:R{len(data)+1}"
    return ws,len(data)+1
# 시트
tabs=[('실적전체',rows),('YoY·QoQ 둘다',[d for d in rows if d['both']]),('QoQ 해당',[d for d in rows if d['qoq']]),('YoY 해당',[d for d in rows if d['yoy']])]
ends={}
# 요약 먼저 입력 셀 만들기 (참조 대상)
ws0['B2']=f'{title} 실적발표 스크리닝';ws0['B2'].font=Font(name=FN,size=14,bold=True)
ws0['B3']='접수 기간 기준 이번 주 분기보고서 제출 상장사 중 시총 2,000억 이상. 매출·영업이익 둘 다 기준 이상 증가 (당분기 3개월, 비교 기준이 흑자일 때만)'
ws0['B3'].font=font(italic=True)
ws0['B5']='YoY/QoQ 증가율 기준';ws0['C5']=0.20;ws0['B6']='TTM(최근 4분기 합산) 증가율 기준';ws0['C6']=0.15
for r in(5,6):
    ws0.cell(r,2).font=font(bold=True);c=ws0.cell(r,3);c.font=Font(name=FN,size=10,color='0000FF',bold=True);c.fill=YEL;c.number_format='0%';c.border=BD
ws0['D5']='← 입력 셀(파란 글자/노란 배경). 바꾸면 해당 여부가 다시 계산됨';ws0['D5'].font=font(italic=True)
for name,data in tabs: perf_sheet(name,data)
# TTM
ws=wb.create_sheet('TTM(최근4분기)')
R=TT['rows'];R.sort(key=lambda r:(not r['pass'],-r['mcap']))
header(ws,['종목','코드','시총(억)','3분기 구분','TTM 매출(억)','직전 TTM 매출(억)','매출 증가율','TTM 영업이익(억)','직전 TTM 영업이익(억)','영업이익 증가율','TTM 통과','재무 기준'])
for i,r in enumerate(R,2):
    for j,v in enumerate([r['name'],r['code'],b(r['mcap']),r['tag'],b(r['rev']['cur']),b(r['rev']['prv']),None,b(r['op']['cur']),b(r['op']['prv'])],1):
        if v is not None: ws.cell(i,j,v)
    ws.cell(i,7,f'=IF(N(F{i})>0,E{i}/F{i}-1,"n/a")');ws.cell(i,10,f'=IF(N(I{i})>0,H{i}/I{i}-1,"n/a")')
    ws.cell(i,11,f'=IF(AND(ISNUMBER(G{i}),ISNUMBER(J{i})),IF(AND(G{i}>=\'요약\'!$C$6,J{i}>=\'요약\'!$C$6),"O",""),"")')
    ws.cell(i,12,('연결' if r['fs']=='CFS' else '별도')+('·원문' if r['src']!='API' else ''))
    for j in range(1,13):
        c=ws.cell(i,j);c.font=font();c.border=BD
        if j in(3,5,6,8,9):c.number_format='#,##0;(#,##0);-'
        if j in(7,10):c.number_format='0%;-0%;0%';c.alignment=Alignment(horizontal='right')
        if j in(4,11):c.alignment=Alignment(horizontal='center')
for j,w in enumerate([22,9,11,10,12,13,10,13,14,11,9,10],1): ws.column_dimensions[L(j)].width=w
ws.freeze_panes='C2';ws.auto_filter.ref=f"A1:L{len(R)+1}"
n=len(R)+1
ws.cell(n+2,1,'TTM = 직전 연도 4분기 + 올해 1~3분기 (= FY − 전년 1~3분기 누적 + 올해 1~3분기 누적). 증가율 n/a는 직전 TTM 영업이익이 적자(흑자전환 포함)').font=font(italic=True)
for k,(nm,cd,why) in enumerate(TT['excl']): ws.cell(n+3+k,1,f'비교 불가: {nm}({cd}) - {why}').font=font(italic=True)
# 요약 표
m=perf_sheet.__name__
ws0['B8']='구분';ws0['C8']='종목 수'
for c in('B8','C8'):
    ws0[c].font=HFont;ws0[c].fill=HF;ws0[c].alignment=Alignment(horizontal='center');ws0[c].border=BD
items=[('분석 대상(시총 2,000억↑, 계정 확인 가능)','=COUNTA(\'실적전체\'!A2:A{})'.format(len(rows)+1)),
 ('YoY 해당','=COUNTIF(\'실적전체\'!N2:N{},"O")'.format(len(rows)+1)),
 ('QoQ 해당','=COUNTIF(\'실적전체\'!O2:O{},"O")'.format(len(rows)+1)),
 ('YoY·QoQ 모두 해당','=COUNTIF(\'실적전체\'!P2:P{},"둘다")'.format(len(rows)+1)),
 ('YoY 또는 QoQ 해당 (TTM 확인 대상)','=B13+B14-B15'),
 ('TTM 둘 다 기준↑ 통과','=COUNTIF(\'TTM(최근4분기)\'!K2:K{},"O")'.format(n))]
# 위 수식은 열 B/C 배치에 맞춰 C열에 기록
rowsum=[('분석 대상(시총 2,000억↑, 계정 확인 가능)',f"=COUNTA('실적전체'!A2:A{len(rows)+1})"),
 ('YoY 해당',f"=COUNTIF('실적전체'!N2:N{len(rows)+1},\"O\")"),
 ('QoQ 해당',f"=COUNTIF('실적전체'!O2:O{len(rows)+1},\"O\")"),
 ('YoY·QoQ 모두 해당',f"=COUNTIF('실적전체'!P2:P{len(rows)+1},\"둘다\")"),
 ('YoY 또는 QoQ 해당 (TTM 확인 대상)','=C10+C11-C12'),
 ('TTM 둘 다 기준↑ 통과',f"=COUNTIF('TTM(최근4분기)'!K2:K{n},\"O\")")]
for k,(lab,fm) in enumerate(rowsum):
    r=9+k;ws0.cell(r,2,lab).font=font();c=ws0.cell(r,3,fm);c.font=font(bold=True);c.alignment=Alignment(horizontal='center')
    ws0.cell(r,2).border=BD;c.border=BD
# 흑자전환/제외/주의
ws2=wb.create_sheet('흑자전환·제외·주의')
TY=[d for d in rows if d['op_turn_yoy'] and d['rev_yoy'] is not None and d['rev_yoy']>=.2]
TQ=[d for d in rows if d['op_turn_qoq'] and d['rev_qoq'] is not None and d['rev_qoq']>=.2]
lines=[('영업이익 흑자전환 (매출 20%↑, 비교 기준 적자라 증가율 계산 불가 → 해당 목록에서 제외)',None),
 (f'YoY 흑자전환 ({len(TY)})',', '.join(f"{d['name']}({d['code']})" for d in TY)),
 (f'QoQ 흑자전환 ({len(TQ)})',', '.join(f"{d['name']}({d['code']})" for d in TQ)),
 ('',None),('분석 제외 (금융업 등 매출/영업이익 계정 부재)',', '.join(f"{a}({b_})" for a,b_,_ in A['excl'])),
 ('',None),('주의',None),
 ('1','접수일 기준 이번 주(월~금) 공시만 포함. 마감일이 주말이면 다음 월요일 제출분은 다음 갱신 때 추가 필요'),
 ('2','11/13 접수분은 DART 재무 API에 반영 전이라 보고서 원문을 직접 파싱(재무 기준 열 "원문" 표기). API 값과 대조해 검증'),
 ('3','직전 분기(2분기)는 반기보고서 값. 합병·분할 등으로 재작성된 기업은 QoQ가 왜곡될 수 있음'),
 ('4','TTM은 연간 보고서와 2025년 3분기 보고서 값을 합산. 유바이오로직스는 별도 기준으로 통일, 한화엔진은 2024년 1~3분기만 별도 값 사용'),
 ('5','시총은 네이버증권 작성일 종가 기준. 지분법손익이 매출에 섞이는 지주사(예: 효성)는 계정 라벨 차이로 누락될 수 있음')]
for i,(a,b2) in enumerate(lines,2):
    ws2.cell(i,1,a).font=font(bold=(b2 is None and a!='')or a.startswith('YoY') or a.startswith('QoQ'))
    if b2:
        c=ws2.cell(i,2,b2);c.font=font();c.alignment=Alignment(wrap_text=True,vertical='top')
ws2.column_dimensions['A'].width=34;ws2.column_dimensions['B'].width=120
ws0.column_dimensions['A'].width=3;ws0.column_dimensions['B'].width=44;ws0.column_dimensions['C'].width=12;ws0.column_dimensions['D'].width=50
wb.save(out);print('saved',out)
