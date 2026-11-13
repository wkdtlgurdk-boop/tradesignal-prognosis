"""반도체 분류 공용 모듈. 우선순위: 테마분석(data.json) > 수동 목록 > KSIC(261*, 29271).
반환 (분류, 근거): 분류 = '반도체'(제외 대상) / '경계'(애매, 제외 안 함) / ''(해당 없음)"""
import json
SEMI_MANUAL={'주성엔지니어링','심텍','심텍홀딩스','대덕전자','티엘비','해성디에스','티씨케이','샘씨엔에스','티에프이','와이씨','디아이','한솔아이원스','리노공업','인텍플러스','아스플로','케이씨텍','엠케이전자','에스앤에스텍'}
BORDER={'파크시스템스','한양이엔지','엘티씨','상아프론테크','한선엔지니어링','디케이티','PS일렉트로닉스','LIG아큐버','태성','SFA','디아이티','코리아써키트','나노신소재'}
NOT_SEMI={'신성이엔지'}
def make(ksic_path=None,data_path=None):
    KS={c:i for c,i,n in json.load(open(ksic_path))} if ksic_path else {}
    TH={}
    if data_path:
        for r in json.load(open(data_path))['rows']:
            L=TH.setdefault(r['code'],[]); L.extend(t for t in r.get('themes',[]) if t not in L)
    def classify(code,name):
        k=KS.get(code,''); ts=TH.get(code)
        if ts: return ('반도체' if any('반도체' in t for t in ts) else ''),'테마분석: '+', '.join(ts)
        if name in NOT_SEMI: return '','업종코드상 반도체이나 클린룸·태양광 중심이라 제외 대상 아님'
        if name in SEMI_MANUAL: return '반도체','소부장(수동 분류)'
        if name in BORDER: return '경계','반도체 비중 애매(수동 분류, 제외 안 함)'
        if k.startswith('261'): return '반도체',f'KSIC {k} 반도체 제조업'
        if k=='29271': return '반도체',f'KSIC {k} 반도체 제조용 기계'
        return '',''
    return classify
