"""watch_result.json -> 관심·보유 종목 실적 점검 엑셀 (보유종목 / 관심종목 시트).
사용: python3 gen_watch_xlsx.py watch_result.json 출력.xlsx '2026년 3분기'   ※ 결과 파일은 개인 정보 → 저장소에 올리지 말고 SendUserFile 로 전달"""
import json,sys
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter as L
src,out,title=sys.argv[1:4]
R=json.load(open(src))
FN='Arial';font=lambda **k:Font(name=FN,size=10,**k)
HF=PatternFill('solid',fgColor='1F3864');HFont=Font(name=FN,size=10,bold=True,color='FFFFFF');YEL=PatternFill('solid',fgColor='FFFF00')
thin=Side(style='thin',color='BFBFBF');BD=Border(left=thin,right=thin,top=thin,bottom=thin)
b=lambda v:None if v is None else round(v/1e8,1)
wb=Workbook();ws0=wb.active;ws0.title='요약'
ws0['B2']=f'{title} 관심·보유 종목 실적 점검';ws0['B2'].font=Font(name=FN,size=14,bold=True)
ws0['B3']='시총 필터 없음. YoY/QoQ/TTM 모두 매출액·영업이익 둘 다 기준 이상일 때 해당(비교 기준이 흑자일 때만).';ws0['B3'].font=font(italic=True)
for r,(lab,v) in((5,('YoY/QoQ 증가율 기준',0.2)),(6,('TTM(최근 4분기 합산) 증가율 기준',0.15))):
    ws0.cell(r,2,lab).font=font(bold=True);c=ws0.cell(r,3,v);c.font=Font(name=FN,size=10,color='0000FF',bold=True);c.fill=YEL;c.number_format='0%';c.border=BD
ws0['B7']='※ C5·C6은 입력 셀. 바꾸면 해당 여부가 다시 계산됨';ws0['B7'].font=font(italic=True)
COLS=['종목','코드','시총(억)','데이터 출처','재무 기준','접수일','매출(억)','전년동기 매출','전분기 매출','영업이익(억)','전년동기 영업이익','전분기 영업이익',
 '매출 YoY','매출 QoQ','영업이익 YoY','영업이익 QoQ','YoY 해당','QoQ 해당','TTM 매출(억)','직전 TTM 매출','매출 TTM 증가율','TTM 영업이익','직전 TTM 영업이익','영업이익 TTM 증가율','TTM 통과',
 '컨센 매출(억)','컨센 영업이익(억)','매출 서프라이즈','영업이익 서프라이즈','컨센 판정','비고']
def sheet(name,data):
    ws=wb.create_sheet(name)
    for i,c in enumerate(COLS,1):
        x=ws.cell(1,i,c);x.font=HFont;x.fill=HF;x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True);x.border=BD
    ws.row_dimensions[1].height=32
    data=sorted(data,key=lambda o:(bool(o.get('err')),-(o.get('mcap') or 0)))
    for i,o in enumerate(data,2):
        ws.cell(i,1,o['name']);ws.cell(i,2,o['code']);ws.cell(i,3,b(o.get('mcap')))
        if o.get('err'):
            ws.cell(i,31,o['err'])
        else:
            r,p=o['rev'],o['op']
            vals={4:o['src'],5:'연결' if o['fs']=='CFS' else '별도',6:f"{o['rcept_dt'][:4]}-{o['rcept_dt'][4:6]}-{o['rcept_dt'][6:]}",
                  7:b(r['q3']),8:b(r['py']),9:b(r['q2']),10:b(p['q3']),11:b(p['py']),12:b(p['q2']),
                  19:b(r.get('ttm')),20:b(r.get('ttm_prev')),22:b(p.get('ttm')),23:b(p.get('ttm_prev'))}
            for k,v in vals.items():
                if v is not None: ws.cell(i,k,v)
            ws.cell(i,13,f'=IF(N(H{i})>0,G{i}/H{i}-1,"n/a")');ws.cell(i,14,f'=IF(N(I{i})>0,G{i}/I{i}-1,"n/a")')
            ws.cell(i,15,f'=IF(N(K{i})>0,J{i}/K{i}-1,"n/a")');ws.cell(i,16,f'=IF(N(L{i})>0,J{i}/L{i}-1,"n/a")')
            ws.cell(i,17,f'=IF(AND(ISNUMBER(M{i}),ISNUMBER(O{i})),IF(AND(M{i}>=\'요약\'!$C$5,O{i}>=\'요약\'!$C$5),"O","X"),"n/a")')
            ws.cell(i,18,f'=IF(AND(ISNUMBER(N{i}),ISNUMBER(P{i})),IF(AND(N{i}>=\'요약\'!$C$5,P{i}>=\'요약\'!$C$5),"O","X"),"n/a")')
            ws.cell(i,21,f'=IF(N(T{i})>0,S{i}/T{i}-1,"n/a")');ws.cell(i,24,f'=IF(N(W{i})>0,V{i}/W{i}-1,"n/a")')
            ws.cell(i,25,f'=IF(AND(ISNUMBER(U{i}),ISNUMBER(X{i})),IF(AND(U{i}>=\'요약\'!$C$6,X{i}>=\'요약\'!$C$6),"O","X"),"n/a")')
            cons=o.get('cflag')=='Y' and o.get('c_rev') is not None and o.get('c_op') is not None
            if cons: ws.cell(i,26,o['c_rev']);ws.cell(i,27,o['c_op'])
            ws.cell(i,28,f'=IF(N(Z{i})>0,G{i}/Z{i}-1,"n/a")');ws.cell(i,29,f'=IF(N(AA{i})>0,J{i}/AA{i}-1,"n/a")')
            ws.cell(i,30,f'=IF(OR(Z{i}="",AA{i}=""),"컨센 없음",IF(AND(G{i}>=Z{i},J{i}>=AA{i}),"매출·영업 상회",IF(J{i}>=AA{i},"영업만 상회",IF(G{i}>=Z{i},"매출만 상회","하회"))))')
            nb=[]
            if o['src']=='잠정': nb.append('잠정실적 기준(확정치와 다를 수 있음)')
            if o['src']=='원문': nb.append('보고서 원문 파싱')
            if o.get('mixed'): nb.append('연결/별도 기준 혼합 → TTM 신뢰 낮음')
            if o.get('cflag')=='N': nb.append('컨센서스가 실제 값으로 갱신됨')
            if o['op']['q3'] is not None and o['op']['q3']<0: nb.append('영업 적자')
            ws.cell(i,31,'; '.join(nb) or None)
        for j in range(1,32):
            c=ws.cell(i,j);c.font=font();c.border=BD
            if j in(3,7,8,9,10,11,12,19,20,22,23,26,27):c.number_format='#,##0;(#,##0);-'
            if j in(13,14,15,16,21,24,28,29):c.number_format='0%;-0%;0%';c.alignment=Alignment(horizontal='right')
            if j in(4,5,17,18,25,30):c.alignment=Alignment(horizontal='center')
        if not o.get('err'):
            for j in(26,27):
                if ws.cell(i,j).value is not None: ws.cell(i,j).font=Font(name=FN,size=10,color='0000FF')
    for j,w in enumerate([18,9,10,9,8,11,10,10,10,11,11,11,9,9,10,10,8,8,11,11,10,11,11,11,8,10,11,10,11,14,44],1): ws.column_dimensions[L(j)].width=w
    ws.freeze_panes='C2';ws.auto_filter.ref=f"A1:AE{len(data)+1}"
    n=len(data)+1
    for k,t in enumerate(['컨센서스: 네이버증권(FnGuide) 당분기 컨센서스(파란 글자), 억원. 조회 시점의 최신 값이라 먼저 실적을 낸 기업은 발표 후 조정분이 섞였을 수 있음',
                          'TTM = 직전 연도 4분기 + 올해 누적. 증가율 n/a는 비교 기준이 적자. 시총 순 정렬, 미발표는 맨 아래']): ws.cell(n+2+k,1,t).font=font(italic=True)
    return n
rows={}
for g,nm in(('보유','보유종목'),('관심','관심종목')):
    D=[o for o in R if o.get('group')==g]
    if D: rows[nm]=(D,sheet(nm,D))
# 요약 집계
ws0['B9']='구분';ws0['C9']='보유종목';ws0['D9']='관심종목'
for c in('B9','C9','D9'):
    ws0[c].font=HFont;ws0[c].fill=HF;ws0[c].alignment=Alignment(horizontal='center');ws0[c].border=BD
items=[('종목 수',None,None),('3분기 실적 발표(분기보고서·잠정)','D','<>'),('YoY 해당','Q','O'),('QoQ 해당','R','O'),('TTM 통과','Y','O'),('컨센 매출·영업 상회','AD','매출·영업 상회')]
for k,(lab,col,val) in enumerate(items):
    r=10+k;ws0.cell(r,2,lab).font=font();ws0.cell(r,2).border=BD
    for m,nm in enumerate(('보유종목','관심종목')):
        if nm not in rows: continue
        n=rows[nm][1];rng=lambda c:f"'{nm}'!{c}2:{c}{n}"
        if col is None: f=f"=COUNTA({rng('A')})"
        elif lab.startswith('3분기'): f=f'=COUNTIF({rng("D")},"?*")'
        else: f=f'=COUNTIF({rng(col)},"{val}")'
        c=ws0.cell(r,3+m,f);c.font=font(bold=True);c.alignment=Alignment(horizontal='center');c.border=BD
ws0.column_dimensions['A'].width=3;ws0.column_dimensions['B'].width=34
for c in'CD':ws0.column_dimensions[c].width=14
wb.save(out);print('saved',out)
