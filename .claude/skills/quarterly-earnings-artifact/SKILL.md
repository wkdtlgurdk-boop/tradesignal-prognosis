---
name: quarterly-earnings-artifact
description: 분기 실적 시즌에 「N분기 실적상승 종목」 아티팩트(시총 2,000억↑ 중 YoY·QoQ 통과 종목을 다섯 기준·PER 구간별로 고르고 정렬하는 페이지)를 새로 만들거나 갱신할 때 쓴다. "다음 분기 실적 나왔어 아티팩트 또 만들어줘", "N분기 실적상승 종목 정리", "실적상승 종목 아티팩트 갱신" 같은 요청에 해당한다. 보유·관심 종목 점검 아티팩트(개인 정보)와는 다른 작업이다.
---

# 분기 실적상승 종목 아티팩트 만들기

시장 전체(코스피·코스닥, 시총 2,000억원 이상)에서 그 분기 **매출·영업이익이 전년 동기 또는 직전 분기 대비 20% 이상 오른 종목**을 모아, 다섯 기준(YoY·QoQ·TTM·컨센서스·차트)과 PER 구간으로 고르고 정렬하는 Data 유형 아티팩트를 만든다. 기준의 정의와 계산식은 저장소 루트 `CLAUDE.md`(1번 정의, 8번)가 원본이다. 이 문서는 **순서와 함정**만 적는다.

**이 아티팩트에는 개인 정보(보유·관심종목, 수량, 계좌)를 절대 넣지 않는다.** 저장소는 공개이고 아티팩트는 외부 공유될 수 있다.

## 0. 준비

- 분기 결정: 오늘 날짜로 판단(5월 중순 1분기, 8월 중순 2분기, 11월 중순 3분기). 마감일이 주말이면 다음 월요일에 제출분이 몰린다(3분기 2026은 11/16).
- 환경 변수 `DART_API_KEY`, 네트워크 허용: `opendart.fss.or.kr`, `m.stock.naver.com`, `wcomp.fnguide.com`. 막히면 `read_documentation`(environment.network)로 확인하고, **FnGuide는 사용자가 이용을 직접 지시한 경우에만** 쓴다(없으면 2027E 열은 비운다).
- 도구는 모두 `T=/home/user/tradesignal-prognosis/실적발표/tools`. 작업은 scratchpad의 새 폴더에서 하고, 스크립트는 **경로로 실행**한다(`python3 -I` 금지). 오래 걸리는 단계는 백그라운드로 돌리고 기다린다.
- 1Q/4Q는 직전 분기 산출 방식이 달라 `fin.py` 수정이 필요하다(`CLAUDE.md` 3번). 먼저 사용자에게 알린다.

## 1. 접수분(pool)별 실적 데이터 만들기

접수일 구간마다 폴더 하나를 만들어 `CLAUDE.md` 4번의 1~10단계를 돌린다(마감 직후 몰린 날은 하루만 따로: `collect.py 20261116 20261116 A003`). 폴더마다:

```
collect → mcap → fin → retry → fill → analyze → ksic → ttm → ttm_final → consensus → chart_day → eval_day
```

결과로 폴더에 `analysis.json`, `eval_day.json`(다섯 기준 지표)이 생긴다. 이후 단계가 이 두 파일을 쓴다.
- 마감일에 몰린 날은 DART 재무 API가 비어 있어 `fill.py`(원문 파싱, 6개 병렬, `fill_cache.json`)가 오래 걸린다. 끊겨도 같은 명령으로 이어진다.
- `chart_day.py`는 권리락(하루 ±30%) 이전 시세를 버린다. `consensus.py`의 인자는 분기말 `YYYYMM`.

## 2. 데이터 파일 만들기

한 폴더에서(앞쪽 pool이 우선: 늦은 날의 확정치):

```bash
python3 $T/build_stocks.py base --pool 늦은접수분폴더:'11/16 접수' --pool 이른접수분폴더:'11/9~13 접수' --out stocks_base.json
python3 $T/per_fetch.py stocks_base.json     # 네이버 PER·PBR(참고용) -> per_all.json
python3 $T/fng_fetch.py stocks_base.json     # FnGuide 2027E PER -> per_fng.json (컨센서스 있는 기업만)
python3 $T/per_ttm.py stocks_base.json       # 최근 4분기 합산 순이익·시총 -> per_ttm.json (176곳 약 5분)
python3 $T/build_stocks.py final --base stocks_base.json --out stocks.json
```

- `base`는 **스크리닝 대상(analysis.json의 YoY|QoQ 해당)과 종목 집합이 정확히 같은지** 스스로 검사하고 다르면 중단한다. 보유종목을 빼거나 관심종목을 끼워 넣으면 공개 결과와 대조해 개인 목록이 추정된다. 이 검사를 우회하지 않는다.
- `final`은 민감 문자열(보유·관심·경로·계좌 등)이 들어 있으면 중단한다.
- 검증: `per_ttm`의 PER을 네이버 PER이 이미 최신 분기 기준인 종목과 비교해 ±3% 안인지 본다. FnGuide 2027E PER은 `시총 ÷ 컨센서스 지배순이익`과 중앙값 비율이 1에 가까운지 본다.
- 순이익 0 이하이거나 직전 연도 재무가 없는 신규 상장은 PER 없음으로 남긴다(제외하지 않는다).

## 3. 아티팩트 만들기 또는 갱신

**처음 만들 때** (Data 유형):
1. `Artifact` publish: `type_url`=Data 유형(`quickstart` intent `other`가 알려 준다), `title`=`N분기 실적상승 종목`, `auto_open: "after_first_write"`, 파일 없음. 돌아온 지침(Data 유형)을 따른다(`artifact-type/reference/design-defaults.md`, `one-writer.md`, `sources.md`를 읽는다).
2. `stocks.json`을 `Artifact` publish `asset:true`, `url`, `file_path`로 올려 `/_blob/<id>`를 받는다.
3. 페이지 렌더: `python3 $T/render_page.py $T/per_page.html page_doc.json --quarter 3분기 --asof 2026-11-18 --today 2026-11-21` (`--asof`는 시총·컨센서스·차트 기준일, `--today`는 정리일).
4. `ArtifactData` batch로 문서 3개를 쓴다(`edit: {via:"claude", at:<UTC>}` 포함):
   - `dash/meta` = `{title:"N분기 실적상승 종목", lang:"ko"}`
   - `datasets/stocks` = `{title, description, source:{kind:"file", url:"/_blob/<id>", name:"stocks.json", format:"json"}, updated:{at,by:"Claude"}}`
   - `files/index.html` = `page_doc.json` (`{text, edit}`)

**갱신할 때**(같은 아티팩트): 새 `stocks.json`을 올리고 `datasets/stocks`의 `source.url`을 바꾼 뒤(`update`, `if_version`), 필요하면 페이지 문서를 다시 렌더해 `files/index.html`을 덮어쓴다. **덮어쓰기 전에 저장된 `text`가 내가 마지막에 올린 것과 같은지 확인**하고(다르면 사람이 고친 것이다), 이전 asset은 지운다.

## 4. 확인

- 페이지를 쓴 직후 `data/users/me`의 `check`, `runs`, `page`를 읽는다. 열어 본 화면이 없으면 기록이 없을 수 있고, 그건 통과가 아니다. 그렇게 말한다.
- 걸렸던 것: ① 표에 보이는 값은 데이터 값과 글자 그대로 같아야 한다(`2026.06`을 `26.06`으로 줄이면 불일치). ② 산점도 라벨이 서로 겹치면 실패(`labels_overlap`): 점 이름은 충돌을 피해 놓고 못 놓으면 생략, 축 제목은 맨 위 눈금보다 위쪽 여백에 둔다.
- 페이지 계산 로직은 node로 `dash.calc` 함수만 따로 돌려 개수·순위가 `eval_day.json`과 일치하는지 본다(이번 분기 방식: 11/16 접수분 92곳 통과 개수·종합 점수 전부 일치).

## 5. 외부 공유 전 점검

공유(share)는 사용자가 Share 메뉴에서 직접 한다(이 도구로는 못 바꾼다). 공유 요청이 오면 먼저:
1. 데이터 종목 집합 == 스크리닝 대상 집합(base 단계가 검사).
2. 데이터 파일·페이지·모든 문서를 훑어 개인 정보(이름, 이메일, 보유·관심, 계좌, 키), 실행 환경 경로가 없는지 확인한다.
3. 페이지 하단에 투자 권유가 아니라는 안내와 출처(DART·네이버증권·FnGuide)가 있는지 본다(템플릿에 들어 있다).
4. 링크를 가진 사람은 첨부 데이터 파일과 코드 설명을 모두 볼 수 있다고 알린다. FnGuide 데이터의 외부 공개 약관은 사용자가 판단한다.
5. 갤러리 이름은 이 도구로 못 바꾼다고 알린다.

## 6. 마무리

- 저장소에는 **코드·템플릿만** 커밋·푸시한다. 종목 목록·보유 정보·결과 파일은 올리지 않는다.
- 절차를 고쳤으면 이 파일과 `CLAUDE.md` 8번을 같이 갱신한다.
- 사용자에게는 짧게 보고한다: 접수분별 종목 수, PER 구간별 수, 다섯 기준 4개 이상 통과 종목, 한계(컨센서스 조회 시점, 원문 파싱 건수, 화면 검증 여부).
