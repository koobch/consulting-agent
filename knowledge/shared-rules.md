# 공통 규칙 (Shared Rules) — 모든 에이전트 참조

> 이 파일은 여러 에이전트에서 공통으로 사용하는 API 스펙, 엔터티 규칙, 기업 조회표의 **단일 진실 소스(SSOT)**이다.
> 에이전트 파일에 동일 내용을 복제하지 말고, `knowledge/shared-rules.md 참조`로 대체할 것.

---

## 1. DART Open API

- **Base URL**: `https://opendart.fss.or.kr`
- **API Key**: 환경변수 `DART_API_KEY` 사용. 하드코딩 금지.
  - CLI에서 확인: `echo $DART_API_KEY`
  - 미설정 시 PM에게 에스컬레이션
- **일일 한도**: 10,000건 (에이전트 배분: data-researcher 60%, financial-analyst 30%, fact-checker 10%)

### 핵심 엔드포인트

| 용도 | 엔드포인트 | 주요 파라미터 |
|------|-----------|-------------|
| 고유번호 목록 | `GET /api/corpCode.xml` | `crtfc_key` (전체 기업 목록 ZIP) |
| 공시 검색 | `GET /api/list.json` | `corp_code`, `bgn_de`, `end_de`, `pblntf_ty` |
| 단일회사 재무제표 | `GET /api/fnlttSinglAcnt.json` | `corp_code`, `bsns_year`, `reprt_code`, `fs_div` |
| 다중회사 재무제표 | `GET /api/fnlttMultiAcnt.json` | `corp_code` (콤마 구분), `bsns_year`, `reprt_code` |
| 직원 현황 | `GET /api/empSttus.json` | `corp_code`, `bsns_year`, `reprt_code` |
| 배당 정보 | `GET /api/alotMatter.json` | `corp_code`, `bsns_year`, `reprt_code` |

### 파라미터 코드

| 파라미터 | 코드 | 설명 |
|---------|------|------|
| reprt_code | `11011` | 사업보고서 |
| reprt_code | `11012` | 반기보고서 |
| reprt_code | `11013` | 1분기보고서 |
| reprt_code | `11014` | 3분기보고서 |
| fs_div | `OFS` | 별도/개별 재무제표 |
| fs_div | `CFS` | 연결 재무제표 |

### 사업보고서 본문 심화 파싱

API 재무제표 외에 사업보고서 **본문**에서만 확인 가능한 데이터:

| 섹션 | 추출 항목 | 활용 |
|------|----------|------|
| II. 사업의 내용 | 부문별 매출 비중, 주요 제품 현황 | 제품별 매출 기여도, 포트폴리오 분석 |
| III. 재무에 관한 사항 | 5개년 요약 재무제표 | CAGR, 장기 추세 |
| VIII. 임원 및 직원 | 직군별 인원, 평균 근속, 평균 연봉 | 인력 효율 분석 |
| IX. 계열회사 | 자회사 목록, 지분율 | 엔터티 구조 파악 |

**파싱 절차:**
1. `/api/list.json`으로 사업보고서 rcept_no 확보 (pblntf_ty=A)
2. `https://dart.fss.or.kr/dsaf001/main.do?rcept_no={rcept_no}`로 본문 접근
3. 필요 섹션을 WebFetch로 추출
4. 핵심 수치를 구조화하여 분석에 활용

---

## 2. SEC EDGAR (미국 상장사)

- **API Key 불필요**
- **User-Agent 필수**: `User-Agent: ResearchOrchestrator research@example.com`
- **Rate Limit**: 초당 10건. 429 응답 시 10초 대기 후 재시도 (최대 3회)
- **CIK 패딩**: URL에 CIK 사용 시 **10자리 제로패딩** (`CIK0000712515`)

### 핵심 엔드포인트

| 용도 | URL |
|------|-----|
| Company Facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json` |
| Company Concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json` |
| Submissions | `https://data.sec.gov/submissions/CIK{cik_padded}.json` |
| Full-Text Search | `https://efts.sec.gov/LATEST/search-index?q={query}&dateRange=custom&startdt={date}&enddt={date}` |

### 주요 XBRL 태그

| 지표 | 태그 |
|------|------|
| Revenue | `us-gaap/Revenues` 또는 `us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax` |
| Operating Income | `us-gaap/OperatingIncomeLoss` |
| Net Income | `us-gaap/NetIncomeLoss` |
| Total Assets | `us-gaap/Assets` |
| Employees | `dei/EntityNumberOfEmployees` |

### Filing 유형

| Filing | 내용 | 주기 |
|--------|------|------|
| 10-K | 연간 보고서 | 연 1회 |
| 10-Q | 분기 보고서 | 분기 |
| 8-K | 수시 공시 | 수시 |
| DEF 14A | 주주총회 위임장 | 연 1회 |

---

## 3. Yahoo Finance (글로벌 주가/재무)

**접근 우선순위** (순서대로 시도):
1. API 호출 (비공식, 무료, 키 불필요):
   - Quote: `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1y`
   - Financial Data: `https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=financialData,incomeStatementHistory,balanceSheetHistory`
   - Key Statistics: `https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics`
2. WebFetch 직접 접근 (API 차단 시):
   - `https://finance.yahoo.com/quote/{ticker}/financials/`
   - `https://finance.yahoo.com/quote/{ticker}/key-statistics/`
3. 대안 소스 (Yahoo 전체 차단 시):
   - Google Finance: `https://www.google.com/finance/quote/{ticker}:{exchange}`
   - 네이버 금융 (한국 상장사)
   - SEC EDGAR (미국 상장사 재무 원본)

### 수집 항목

| 항목 | 용도 |
|------|------|
| 시가총액 | 기업 규모 비교 |
| Revenue (TTM) | 연간 매출 (최근 4분기 합산) |
| Operating Margin | 영업이익률 |
| P/E, EV/EBITDA | 멀티플 Peer 비교 |
| 52주 최고/최저 | 주가 추이 |

---

## 4. 일본/홍콩 상장사 공시

### 일본 — TDnet / EDINET
- **TDnet**: `https://www.release.tdnet.info/` (적시 공시 — 결산 단신)
- **EDINET API**: `https://disclosure.edinet-fsa.go.jp/api/v2/documents.json?date={YYYY-MM-DD}&type=2`
- 결산 단신(決算短信)에서 매출, 영업이익, 사업 부문별 실적 추출
- Yahoo Finance Japan: `https://finance.yahoo.co.jp/quote/{ticker}.T`

### 홍콩 — HKEX
- **HKEX 공시**: `https://www.hkexnews.hk/` (Tencent 등)

---

## 5. 기업 조회표

리서치 대상 기업의 corp_code(DART), CIK(SEC), Ticker는 리서치 시작 시 조회한다.

### 조회 방법
| 시스템 | 조회 방법 |
|--------|----------|
| DART | `/api/corpCode.xml`로 전체 기업 목록 ZIP 다운로드 → 기업명으로 검색 |
| SEC EDGAR | `https://www.sec.gov/cgi-bin/browse-edgar?company={name}&CIK=&type=10-K&action=getcompany` |
| TDnet/EDINET | 기업명 또는 증권코드로 검색 |
| HKEX | `https://www.hkexnews.hk/`에서 기업명 검색 |

⚠️ corp_code/CIK는 변동 가능. 리서치 시작 전 최신 확인.

---

## 6. 엔터티 분리 규칙 — 반드시 준수

### 원칙
**모회사(그룹)와 자회사(스튜디오)의 데이터를 절대 혼용하지 않는다.**

### 적용 규칙
1. **분석 대상 엔터티를 먼저 명확히 정의**: 그룹 모회사 vs 개발 자회사는 별개 엔터티
2. **재무 데이터는 해당 엔터티의 별도(OFS) 재무제표 사용**: 자회사 분석 시 그룹 연결(CFS) 사용 금지
3. **데이터 출력 시 엔터티 라벨 필수**: 모든 수치에 `[그룹]` 또는 `[별도]` 라벨 부여
4. **혼동 가능 지표 명시적 분리**:
   - 매출, 영업이익, 영업이익률 → 반드시 엔터티별 분리
   - 직원 수 → 해당 법인 기준 DART 데이터 사용
   - 해외 매출 비중 → 그룹 vs 자회사 구분
   - 파이프라인 → 해당 스튜디오 담당분만 카운트
5. **그룹 데이터는 맥락으로만 사용**: "그룹 매출 X조 중 자회사 기여분 Y억 원" 형태

### 위반 사례 (절대 금지)
- ❌ "A그룹의 영업이익률은 12.4%이다" → 그룹인지 자회사인지 불명확
- ❌ "579명으로 8종을 개발" → 어느 법인의 579명인지 불명확
- ✅ "A사[별도]의 2024 영업이익률은 38.7%이며, A그룹[연결]은 12.4%이다"
- ✅ "A사는 647명(DART 2024.12.31 기준)으로 8종을 개발 중"

### 해외 기업 Peer 비교 시 주의
1. **회계 기준 차이**: US-GAAP(미국) vs K-IFRS(한국) vs J-GAAP(일본) — 비교 시 명시
2. **회계연도 차이**: 기업별 결산월이 다름 — Peer 비교 시 회계연도 기준 명시 필수
3. **통화 환산**: 원문 통화 기재 + KRW 환산 병기, 환율 기준일 명시
4. **세그먼트 분리**: 해외 대기업의 사업부 분리가 필요한 경우 (예: 대기업의 특정 사업부만 분석 시) 해당 사업부 재무만 추출
5. **SBC 조정**: US-GAAP에서 Stock-Based Compensation이 영업비용에 포함 → 한국 기업과 비교 시 조정 필요

---

## 7. API 에러 대응

| 상황 | 대응 |
|------|------|
| DART 429 (Rate Limit) | 10초 대기 후 재시도 (최대 3회) |
| DART 인증 실패 | PM에게 에스컬레이션 — API Key 만료/오류 가능성 |
| SEC EDGAR 429 | 10초 대기 후 재시도 (최대 3회) |
| SEC EDGAR 서버 오류 | 30분 후 재시도 또는 Yahoo Finance로 보조 수집 |
| Yahoo Finance 차단 | WebFetch → Google Finance → SEC EDGAR 순서 |

---

## 8. 추가 데이터 API

### §8-1. Steam Web API (게임 데이터)

> **도메인 특화 API**: 게임 산업 리서치 시에만 사용. domain-profile.md의 도메인이 "게임"인 경우 활성화.

- **Base URL**: `https://api.steampowered.com`
- **인증**: API Key 필요 (무료, https://steamcommunity.com/dev/apikey 에서 발급)
  - 환경변수 `STEAM_API_KEY` 사용
- **Rate Limit**: 명시적 제한 없으나 초당 1~2건 권장

#### 주요 엔드포인트
| 용도 | URL | 비고 |
|------|-----|------|
| 앱 상세 | `https://store.steampowered.com/api/appdetails?appids={appid}` | Key 불필요 |
| 동시접속 | `ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}` | Key 필요 |
| 앱 목록 | `ISteamApps/GetAppList/v2/` | Key 불필요 |
| 리뷰 | `https://store.steampowered.com/appreviews/{appid}?json=1&language=all` | Key 불필요 |

#### 활용
- PC 게임 동시접속자 추이 (SteamDB 보조)
- 리뷰 긍정률/총 리뷰 수 — 유저 반응 정량 지표
- 가격 정책, DLC 목록 — 수익화 모델 확인

### §8-2. IGDB API (글로벌 게임 메타데이터)

> **도메인 특화 API**: 게임 산업 리서치 시에만 사용. domain-profile.md의 도메인이 "게임"인 경우 활성화.

- **Base URL**: `https://api.igdb.com/v4`
- **인증**: Twitch Developer Portal에서 Client ID + Client Secret 발급
  - OAuth2 토큰: `POST https://id.twitch.tv/oauth2/token?client_id={id}&client_secret={secret}&grant_type=client_credentials`
  - 헤더: `Client-ID: {id}`, `Authorization: Bearer {token}`
- **Rate Limit**: 4건/초

#### 주요 엔드포인트
| 용도 | 엔드포인트 | 비고 |
|------|-----------|------|
| 게임 검색 | `POST /games` | Body: `search "게임명"; fields *;` |
| 회사 정보 | `POST /companies` | Body: `where name = "회사명"; fields *;` |
| 플랫폼 | `POST /platforms` | 게임-플랫폼 매핑 확인 |
| 장르 | `POST /genres` | 장르 분류 표준화 |

#### 활용
- 게임 메타데이터 표준화 (장르, 플랫폼, 출시일)
- 개발사/퍼블리셔 관계 확인 (EP-015 제품 귀속)
- 글로벌 게임 DB 기반 포트폴리오 교차 확인

### §8-3. FRED API (미국 매크로 경제지표)

- **Base URL**: `https://api.stlouisfed.org/fred`
- **인증**: API Key 필요 (무료, https://fred.stlouisfed.org/docs/api/api_key.html)
  - 환경변수 `FRED_API_KEY` 사용
- **Rate Limit**: 120건/분
- **응답 형식**: `&file_type=json`

#### 주요 시리즈 ID
| 지표 | Series ID | 용도 |
|------|-----------|------|
| 미국 GDP | `GDP` | 매크로 환경 |
| CPI (소비자물가) | `CPIAUCSL` | 인플레이션 |
| 환율 USD/KRW | `DEXKOUS` | 통화 환산 기준 |
| 실업률 | `UNRATE` | 소비 여력 |
| 개인소비지출 | `PCE` | 엔터테인먼트 소비 |

#### 사용 예시
```
GET https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={key}&file_type=json&observation_start=2023-01-01
```

### §8-4. 한국은행 ECOS API (한국 매크로 경제지표)

- **Base URL**: `https://ecos.bok.or.kr/api`
- **인증**: API Key 필요 (무료, ECOS 회원가입 후 발급)
  - 환경변수 `ECOS_API_KEY` 사용
- **Rate Limit**: 일 500건 (무료)

#### 호출 형식
```
GET /{서비스명}/{인증키}/{요청유형}/{언어}/{요청시작건수}/{요청종료건수}/{통계표코드}/{주기}/{검색시작일자}/{검색종료일자}/{통계항목코드1}
```

#### 주요 통계표
| 지표 | 통계표코드 | 항목코드 | 용도 |
|------|-----------|---------|------|
| GDP 성장률 | `200Y001` | `10111` | 매크로 환경 |
| 소비자물가지수 | `901Y009` | `0` | 인플레이션 |
| 원/달러 환율 | `731Y001` | `0000001` | 통화 환산 |
| 가계소비 | `301Y013` | — | 엔터테인먼트 지출 |

### §8-5. Google Trends (검색 트렌드)

- **접근 방법**: `pytrends` 라이브러리 (비공식 API)
  - `pip install pytrends`
- **인증**: 불필요
- **Rate Limit**: 과도한 요청 시 429. 요청 간격 10~30초 권장

#### 활용
```python
from pytrends.request import TrendReq
pytrends = TrendReq(hl='ko', tz=540)
pytrends.build_payload(['기업A', '기업B'], timeframe='today 12-m', geo='KR')
data = pytrends.interest_over_time()
```

- 기업/제품 간 검색 관심도 비교 (상대적 인기도)
- 지역별 관심도 — 시장 진출 우선순위
- 시계열 트렌드 — 출시/발표 전후 관심도 변화
- **주의**: 절대값이 아닌 상대적 지수(0~100). 비교 분석에만 사용

### §8-6. EDINET API (일본 상장사 공시 — 상세)

- **Base URL**: `https://api.edinet-fsa.go.jp/api/v2`
- **인증**: 불필요 (Subscription Key 선택적)
- **Rate Limit**: 명시적 제한 없으나 초당 1건 권장

#### 주요 엔드포인트
| 용도 | URL | 비고 |
|------|-----|------|
| 서류 목록 | `GET /documents.json?date={YYYY-MM-DD}&type=2` | 유가증권보고서 등 |
| 서류 다운로드 | `GET /documents/{docID}?type=1` | ZIP (XBRL) |
| 서류 다운로드 | `GET /documents/{docID}?type=2` | PDF |

#### 활용
- TDnet 결산 단신 보완 — 유가증권보고서 상세 재무
- 일본 상장사의 세그먼트별 실적 추출
- 기존 §4 EDINET 참조를 보완하는 상세 스펙

### §8-7. NewsAPI (글로벌 뉴스 검색)

- **Base URL**: `https://newsapi.org/v2`
- **인증**: API Key 필요 (무료 tier: 100건/일, 1개월 과거까지)
  - 환경변수 `NEWSAPI_KEY` 사용
- **Rate Limit**: 무료 100건/일

#### 주요 엔드포인트
| 용도 | URL | 비고 |
|------|-----|------|
| 전체 검색 | `GET /everything?q={query}&apiKey={key}` | 과거 1개월 |
| 헤드라인 | `GET /top-headlines?category=technology&apiKey={key}` | 현재 뉴스 |

#### 파라미터
- `q`: 검색어 (AND/OR/NOT 지원)
- `sources`: 소스 제한 (예: `bloomberg,reuters`)
- `language`: `en`, `ko` 등
- `sortBy`: `publishedAt`, `relevancy`, `popularity`
- `from`, `to`: 날짜 범위

#### 활용
- 기업/산업 관련 최신 뉴스 일괄 수집
- 경쟁사 동향 모니터링
- M&A, IPO, 신제품 발표 등 이벤트 탐지
- **한계**: 무료 tier는 과거 1개월만 검색 가능. 장기 뉴스는 Exa/Brave Search 활용

---

## 9. 데이터 TTL 정책 (리서치 재사용)

이전 프로젝트에서 수집한 데이터를 새 리서치에서 재사용할 때 적용하는 유효기간(TTL) 정책.

### TTL 기준표

| 데이터 유형 | TTL | 근거 | 만료 시 처리 |
|------------|-----|------|------------|
| 재무 공시 (DART/SEC) | 90일 (분기) | 분기보고서 발행 주기 | 재수집 필수 |
| 시장 규모/전망 | 180일 (6개월) | 리서치 리포트 발행 주기 | 재수집 필수, 참고용 유지 |
| 제품/서비스 포트폴리오 | 30일 | 변동 빈번 | 재수집 필수 |
| 주가/멀티플 | 7일 | 시장 변동성 | 재수집 필수 |
| 매크로 지표 | 30일 | 월간 발표 | 재수집 필수 |
| 팩트시트 (기업 기초 정보) | 90일 | 기업 기초 정보 안정적 | 재사용 가능, 변동 항목만 갱신 |
| 경쟁사 팩트시트 | 90일 | 동일 | 재사용 가능, 변동 항목만 갱신 |
| 사용자 제공 데이터 [U##] | 무기한 | 사용자가 직접 판단 | 사용자 확인 후 결정 |

### TTL 판정 규칙
1. **TTL 내**: 데이터 재사용 가능 (출처에 "이전 프로젝트 재사용" 명시)
2. **TTL 만료**: 데이터는 "참고용"으로만 표시, 보고서 출처로 직접 인용 불가. 재수집 필수
3. **TTL 기준일**: 데이터 수집 시점 (보고서 작성 시점이 아닌, 원본 데이터를 가져온 날짜)

### 재사용 체크 로직 (research-pm.md Step 0에서 실행)
```
1. 새 리서치 시작 시 output/ 하위 기존 프로젝트 스캔
2. 동일/유사 기업 팩트시트가 TTL 내이면 재사용 제안
3. 사용자 승인 시 팩트시트 복사 → Phase 0.5 단축
4. TTL 만료 데이터는 "참고용"으로만 표시, 재수집 필수
```
