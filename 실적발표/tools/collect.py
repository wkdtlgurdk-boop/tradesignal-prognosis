"""이번 주 접수된 분기/반기/사업보고서 목록 수집 -> filings.json
사용: python3 collect.py 20261109 20261114 A003     (A003 분기보고서 / A002 반기보고서 / A001 사업보고서)"""
import os,sys,json,urllib.request,urllib.parse
K=os.environ['DART_API_KEY'];bgn,end,ty=sys.argv[1:4]
rows=[]
for pg in range(1,40):
    q=urllib.parse.urlencode(dict(crtfc_key=K,bgn_de=bgn,end_de=end,pblntf_detail_ty=ty,page_count=100,page_no=pg))
    r=json.load(urllib.request.urlopen("https://opendart.fss.or.kr/api/list.json?"+q,timeout=30))
    if r['status']!='000': print(r['status'],r.get('message'));break
    rows+=r['list']
    if pg>=int(r['total_page']):break
json.dump(rows,open('filings.json','w'),ensure_ascii=False)
L=[x for x in rows if x['stock_code'].strip() and x['corp_cls'] in('Y','K')]
print('전체',len(rows),'상장(코스피·코스닥)',len({x['stock_code'] for x in L}))
