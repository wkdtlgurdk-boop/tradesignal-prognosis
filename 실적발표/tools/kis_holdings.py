"""한국투자증권 Open API 로 현재 보유 종목 조회 -> holdings_kis.json  (사용자 PC에서 실행)

왜 PC에서? 클라우드 세션의 프록시는 443 이외 HTTPS 포트를 지원하지 않는데, 한투 실전 API 는 :9443 이라 접근할 수 없다.
필요 환경변수(키는 절대 채팅·저장소에 올리지 말 것):
  KIS_APP_KEY, KIS_APP_SECRET, KIS_CANO(계좌번호 앞 8자리), KIS_ACNT_PRDT_CD(뒤 2자리, 기본 01)
사용: python3 kis_holdings.py        # 출력 holdings_kis.json 에는 종목코드·이름·수량만 들어간다(금액 없음)
결과 파일을 Claude 대화에 첨부하거나 코드·이름만 붙여 넣으면 보유종목으로 점검한다. 저장소(공개)에는 올리지 않는다.
※ 이 스크립트는 클라우드 환경에서 실제 호출을 시험하지 못했다(접속 불가). 처음 실행할 때 응답 오류가 나면 메시지를 알려 달라.
※ 미래에셋 등 다른 증권사 계좌는 이 API 로 조회되지 않는다."""
import os,sys,json,time,urllib.request,urllib.error
BASE='https://openapi.koreainvestment.com:9443'
KEY=os.environ['KIS_APP_KEY'];SECRET=os.environ['KIS_APP_SECRET']
CANO=os.environ['KIS_CANO'];PRDT=os.environ.get('KIS_ACNT_PRDT_CD','01')
TOKEN_FILE=os.path.expanduser('~/.kis_token.json')   # 토큰 발급은 분당 1회 제한이라 재사용
def req(method,path,headers=None,body=None,params=None):
    url=BASE+path+(('?'+urllib.parse.urlencode(params)) if params else '')
    data=json.dumps(body).encode() if body is not None else None
    h={'content-type':'application/json; charset=utf-8'};h.update(headers or {})
    r=urllib.request.Request(url,data=data,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=30) as resp: return json.load(resp),dict(resp.headers)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
import urllib.parse
def token():
    try:
        t=json.load(open(TOKEN_FILE))
        if t.get('key')==KEY[:8] and t['exp']>time.time()+300: return t['token']
    except Exception: pass
    d,_=req('POST','/oauth2/tokenP',body=dict(grant_type='client_credentials',appkey=KEY,appsecret=SECRET))
    tok=d['access_token']
    json.dump(dict(key=KEY[:8],token=tok,exp=time.time()+int(d.get('expires_in',86400))),open(TOKEN_FILE,'w'));os.chmod(TOKEN_FILE,0o600)
    return tok
def balance():
    tok=token();out=[];fk=nk='';cont=''
    for _ in range(20):
        h={'authorization':f'Bearer {tok}','appkey':KEY,'appsecret':SECRET,'tr_id':'TTTC8434R','custtype':'P','tr_cont':cont}
        p=dict(CANO=CANO,ACNT_PRDT_CD=PRDT,AFHR_FLPR_YN='N',OFL_YN='',INQR_DVSN='02',UNPR_DVSN='01',FUND_STTL_ICLD_YN='N',FNCG_AMT_AUTO_RDPT_YN='N',PRCS_DVSN='00',CTX_AREA_FK100=fk,CTX_AREA_NK100=nk)
        d,hd=req('GET','/uapi/domestic-stock/v1/trading/inquire-balance',headers=h,params=p)
        if d.get('rt_cd')!='0': sys.exit(f"조회 실패: {d.get('msg_cd')} {d.get('msg1')}")
        out+=d.get('output1',[])
        if hd.get('tr_cont') in('M','F'):
            cont='N';fk=d.get('ctx_area_fk100','');nk=d.get('ctx_area_nk100','');time.sleep(0.3)
        else: break
    return out
if __name__=='__main__':
    rows=[dict(code=x['pdno'],name=x['prdt_name'],group='보유',qty=int(x['hldg_qty'])) for x in balance() if int(x.get('hldg_qty','0') or 0)>0]
    json.dump(rows,open('holdings_kis.json','w'),ensure_ascii=False,indent=1)
    print(len(rows),'종목:',', '.join(f"{r['name']}({r['code']})" for r in rows))
