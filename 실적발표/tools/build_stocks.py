"""'N분기 실적상승 종목' 아티팩트용 데이터 파일(stocks.json = {rows, meta})을 만든다.

단계 1 (base): 접수분(pool)마다 만들어 둔 eval_day.json 을 합쳐 종목 목록과 다섯 기준 지표를 만든다.
  python3 build_stocks.py base --pool DIR:'11/16 접수' --pool DIR2:'11/9~13 접수' --out stocks_base.json
  - DIR 에는 그 접수분의 analysis.json, eval_day.json 이 있어야 한다(eval_day.py 가 만든다).
  - --pool 은 우선순위 순서(앞이 우선). 두 접수분에 모두 있는 종목은 앞쪽(보통 더 늦은 날의 확정치)만 쓴다.
  - **스크리닝 대상(analysis.json 의 YoY 또는 QoQ 해당)과 정확히 같은 종목 집합**인지 검사한다.
    (보유종목을 빼거나 관심종목을 끼워 넣으면 공개 결과와 대조해 개인 목록이 추정된다. 다르면 중단한다.)

  이어서(같은 폴더에서): per_fetch.py stocks_base.json → per_all.json, per_ttm.py stocks_base.json → per_ttm.json,
                         fng_fetch.py stocks_base.json → per_fng.json

단계 2 (final): 위 결과를 합쳐 최종 파일을 만든다.
  python3 build_stocks.py final --base stocks_base.json --out stocks.json
  (per_all.json, per_ttm.json, per_fng.json 은 현재 폴더에서 읽는다)
  - 시총은 per_ttm 의 현재 시총, PER 은 아티팩트 페이지가 시총 ÷ 최근 4분기 합산 순이익으로 계산한다(여기엔 순이익만 담는다).
  - 마지막에 민감 문자열(보유·관심·경로·이름 등)이 없는지 검사한다."""
import sys,os,json,argparse,re
ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True)
b=sp.add_parser('base');b.add_argument('--pool',action='append',required=True);b.add_argument('--out',default='stocks_base.json')
f=sp.add_parser('final');f.add_argument('--base',default='stocks_base.json');f.add_argument('--out',default='stocks.json')
a=ap.parse_args()
TOOLS=os.path.dirname(os.path.abspath(__file__))
FIELDS=['m_yoy','m_qoq','m_ttm','cons','sur_rev','sur_op','d_hi']
if a.cmd=='base':
    rows=[];seen={}
    for spec in a.pool:
        d,label=spec.rsplit(':',1)
        ev=json.load(open(os.path.join(d,'eval_day.json')))
        an=json.load(open(os.path.join(d,'analysis.json')))['rows']
        uni={x['code'] for x in an if x['yoy'] or x['qoq']}
        got={e['code'] for e in ev}
        if uni!=got: sys.exit(f"[{label}] 스크리닝 대상 {len(uni)}곳과 eval_day.json {len(got)}곳이 다르다: 빠짐 {sorted(uni-got)[:5]}, 더 있음 {sorted(got-uni)[:5]}")
        n=0
        for e in ev:
            if e['code'] in seen: continue
            r=dict(code=e['code'],name=e['name'],set=label,mcap=round(e['mcap']/1e8,1),semi=e['semi'] or None)
            for k in FIELDS: r[k]=e.get(k)
            rows.append(r);seen[e['code']]=label;n+=1
        print(f"{label}: 스크리닝 {len(uni)}곳 중 {n}곳 추가(중복 제외)")
    json.dump({'rows':rows},open(a.out,'w'),ensure_ascii=False)
    print('종목',len(rows),'->',a.out)
else:
    B=json.load(open(a.base))['rows']
    PA=json.load(open('per_all.json'));PT={r['code']:r for r in json.load(open('per_ttm.json'))};PF={r['code']:r for r in json.load(open('per_fng.json'))}
    out=[]
    for r in B:
        c=r['code'];o=dict(r);p=PA.get(c,{});t=PT.get(c,{});g=PF.get(c,{})
        o['per_naver']=p.get('per');o['per_naver_period']=(p.get('per_period') or '').strip('.') or None;o['pbr']=p.get('pbr')
        if t.get('mcap'): o['mcap']=round(t['mcap']/1e8,1)
        o['ni_ttm']=None if t.get('ni_ttm') is None else round(t['ni_ttm']/1e8,1)
        o['ni_kind']=t.get('kind');o['ni_note']=t.get('err') or ('연결·별도 혼합' if t.get('mixed') else None)
        o['cns_per27']=g.get('per2027')
        out.append(o)
    def clean(v):
        v=v.replace('/home/user/tradesignal-prognosis/실적발표/tools','tools').replace("'/home/user/tradesignal-prognosis/data.json'","'data.json'")
        return re.sub(r"sys\.path\.insert\(0,'tools'\)\n","",v)
    meta=[{"label":"Input","value":"실적: DART 분기보고서(시총 2,000억원 이상 중심, 연결 우선). 순이익: DART 지배기업 소유주지분 순이익(구분이 없으면 당기순이익). 컨센서스 PER: FnGuide. 시총·네이버 PER·차트·분기 컨센서스: 네이버 모바일 증권. 금액 단위 억원"},
          {"label":"지표","value":"YoY·QoQ·TTM 지표 = 매출·영업이익 증가율 중 낮은 쪽. 컨센 = 매출·영업이익이 모두 컨센서스 이상(O/X). 차트 = 종가가 최근 20거래일 고가 대비 얼마나 아래인지(권리락 이전 시세 제외)"},
          {"label":"PER 계산","value":"PER = 현재 시총 ÷ 최근 4분기 합산 순이익(작년 4분기 + 올해 1~3분기 = FY − 전년 누적 + 올해 누적). 순이익이 0 이하이거나 직전 연도 재무가 없는 신규 상장은 PER 없음. 2027E PER 은 FnGuide 컨센서스 페이지의 2027/12 PER(조회일 주가 ÷ 컨센서스 EPS)이고 컨센서스가 있는 기업만 넣음."}]
    for fn in('per_fetch.py','eval_day.py','per_ttm.py','fng_fetch.py'):   # build_stocks.py 자신은 넣지 않는다(검사 목록 문구가 자기 검사에 걸림)
        meta.append({"label":fn,"value":clean(open(os.path.join(TOOLS,fn),encoding='utf-8').read()),"type":"code","lang":"python"})
    J={'rows':out,'meta':meta}
    txt=json.dumps(J,ensure_ascii=False)
    bad=[p for p in('/home/user','scratchpad','/tmp/','보유','관심','잔고','계좌','매매일지','체크리스트','@gmail','appkey','secret','KIS_') if p in txt.replace('보유종목 매수','')]
    if bad: sys.exit('민감 문자열이 들어 있어 중단: '+str(bad))
    json.dump(J,open(a.out,'w'),ensure_ascii=False)
    print('종목',len(out),'PER 계산 가능',sum(1 for o in out if o['ni_ttm'] is not None and o['ni_ttm']>0),'2027E PER 있음',sum(1 for o in out if o['cns_per27'] is not None),'->',a.out)
