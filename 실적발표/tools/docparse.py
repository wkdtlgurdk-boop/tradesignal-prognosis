import os,re,io,json,zipfile,time,urllib.request,urllib.parse,html
K=os.environ['DART_API_KEY']
UN={'원':1,'천원':1e3,'백만원':1e6,'십억원':1e9,'억원':1e8}
def fetch(rcept):
    for i in range(4):
        try:
            b=urllib.request.urlopen("https://opendart.fss.or.kr/api/document.xml?"+urllib.parse.urlencode(dict(crtfc_key=K,rcept_no=rcept)),timeout=90).read()
            z=zipfile.ZipFile(io.BytesIO(b));return max((z.read(n) for n in z.namelist()),key=len).decode('utf-8','ignore')
        except Exception: time.sleep(3)
def cells(tr):
    return [re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',c))).strip() for c in re.findall(r'<T[DHE][^>]*>(.*?)</T[DHE]>',tr,re.S)]
def tonum(s):
    s=s.replace(',','').replace('△','-').replace(' ','')
    neg=s.startswith('(') and s.endswith(')')
    s=s.strip('()')
    try: v=float(s)
    except: return None
    return -v if neg else v
REV=['매출액','수익(매출액)','영업수익','매출','순매출액','수익']
OP=['영업이익','영업손실','영업이익(손실)','영업손익','영업이익(영업손실)']
def parse(t):
    if not t: return None
    # statement section: prefer 연결 손익계산서, else 손익계산서 (별도)
    secs=[(m.start(),re.sub(r'<[^>]+>','',m.group(0))) for m in re.finditer(r'<TITLE[^>]*>[^<]*(?:포괄)?손익계산서[^<]*</TITLE>',t)]
    cons=[s for s in secs if '연결' in s[1]]; sep=[s for s in secs if '연결' not in s[1] and '재무제표' not in s[1].replace('손익계산서','')]
    for fsname,L in(('CFS',cons),('OFS',secs)):
        for pos,title in L:
            nxt=t.find('<TITLE',pos+10)
            seg=t[pos:nxt if nxt>0 else pos+400000]
            unit=1e6
            m=re.search(r'단위\s*:\s*([가-힣]+)',seg)
            if m and m.group(1) in UN: unit=UN[m.group(1)]
            res={}
            for tr in re.findall(r'<TR[^>]*>(.*?)</TR>',seg,re.S):
                c=cells(tr)
                if not c: continue
                lab=re.sub(r'\(주[^)]*\)|\*|<주[^>]*>','',c[0]); lab=re.sub(r'[\sⅠ-Ⅹ\.\d]','',lab)
                lab=re.sub(r'^[IVX]+\.?','',lab)
                nums=[tonum(x) for x in c[1:] if tonum(x) is not None]
                for key,names in(('rev',REV),('op',OP)):
                    if key in res: continue
                    if lab in names and len(nums)>=2: res[key]=nums
            if 'rev' in res or 'op' in res: return fsname,unit,res
    return None
