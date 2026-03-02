# Consulting Agent — Project Instructions

## 프로젝트 개요
컨설팅급 리서치 오케스트레이션 시스템.
주제가 주어지면 가설 수립 → 프레임워크 설계 → 데이터 수집 → 팩트체크 → 인사이트 도출 → **사고 루프(Thinking Loop: Why 수직 검증 + 대안/레드팀 수평 도전)** → 보고서 작성까지 전 과정을 에이전트 기반으로 수행한다.

**도메인 독립적 설계**: `knowledge/domain/` 디렉토리에 도메인 프로파일을 배치하면 게임, 바이오, SaaS, 반도체 등 어떤 산업이든 동일한 파이프라인으로 리서치 가능. 도메인 프로파일 스키마는 `knowledge/domain-profile-schema.md` 참조.

## 에이전트 아키텍처

### 오케스트레이션 구조
```
[사용자] → [research-pm] (오케스트레이터)
                │
                ├── [hypothesis-builder]      가설 수립
                ├── [framework-designer]      프레임워크 설계 (First-Principles)
                ├── [data-researcher]         데이터 수집 (병렬 가능)
                ├── [fact-checker]            팩트체크/출처 검증
                ├── [insight-synthesizer]     인사이트 도출
                ├── [financial-analyst]       재무 분석 (필요 시)
                ├── [valuation-analyst]       밸류에이션 (필요 시)
                │
                ├── 사고 루프 (Thinking Loop) ─────────────────┐
                │   ├── [logic-prober]        수직: Why Chain   │
                │   ├── [strategic-challenger] 수평: 대안/레드팀 │
                │   └── [insight-synthesizer]  반영/보강        │
                │                          (수렴까지 최대 2회) ─┘
                │
                ├── [report-writer]           보고서 생성 (Docs/Slides)
                └── 품질 보증 ──────────────────────────────────┐
                    ├── [report-auditor]      읽기 전용 감사     │
                    ├── [report-fixer]        최소 수정          │
                    └── [qa-orchestrator]     자동 QA 루프       │
                                           (수렴까지 반복) ────┘
```

### 에이전트 역할 요약

| 분류 | 에이전트 | 핵심 역할 |
|------|---------|----------|
| **사고** | logic-prober | 수직 검증 — "왜 이 결론인가?" 재귀적 Why Chain |
| **사고** | strategic-challenger | 수평 도전 — "다른 방법은?", "실패하면?", "경쟁사 대응은?" |
| **사고** | insight-synthesizer | 패턴 인식, So What 도출, 역량 검증, 사고 루프 결과 통합 |
| **설계** | hypothesis-builder | 가설 수립, 가설-데이터 매핑표 |
| **설계** | framework-designer | First-Principles 기반 프레임워크 설계 |
| **수집/검증** | data-researcher | 데이터 수집 (Ground Truth, 가설 기반) |
| **수집/검증** | fact-checker | 팩트체크, 출처 검증, 실시간 + 종합 검증 |
| **분석** | financial-analyst | 재무 분석, Peer 비교, 투자 시나리오 |
| **분석** | valuation-analyst | DCF, 멀티플, SOTP 밸류에이션 |
| **보고서** | report-writer | 보고서 생성 (Docs + Slides) |
| **품질** | report-auditor, report-fixer, qa-orchestrator | 자동 QA 루프 |
| **관리** | research-pm | 전체 오케스트레이션, 품질 게이트, 에스컬레이션 |

### 워크플로우 시퀀스

#### Phase 0.5: 대상 기업 팩트시트 확보 — 최우선
1. `data-researcher`가 Ground Truth 모드로 대상 기업의 **객관적 사실**을 1차 소스에서 직접 확보
   - 현재 서비스 중인 **전체** 제품/서비스 목록 (공식 사이트, domain-profile의 확인 소스에서 직접 확인)
   - 각 제품의 **실제 지원 채널/플랫폼** (확인 소스에서 직접 확인, 추측 금지)
   - DART API로 **재무·직원 데이터** 직접 조회 (한국 기업)
   - 과거 포트폴리오, 종료/중단 제품
   - **역량 이력 및 내부 역량** (EP-013): 전체 제품 이력, 카테고리별/채널·플랫폼별 경험, 성공/실패 패턴, 핵심 기술 스택
     - ⚠️ 10년+ 전 / 전신 회사 제품은 "레거시/연혁"으로 분리, 현재 역량으로 인용 금지 (EP-014)
     - ⚠️ 그룹 내 자회사 간 제품 귀속 확인 필수 — 유통 주체 ≠ 개발·생산 주체 (EP-015)
   - **DART 분기보고서 활용**: 분기별 매출·영업이익 추이로 제품 출시 효과 간접 검증
2. 사용자에게 팩트시트 검토 요청 → **승인 후 다음 단계 진행**
3. 팩트시트 미확보 시 가설 수립 및 분석 진행 금지

#### Phase 1: 문제 정의 및 가설 수립
1. `research-pm`이 사용자 요청을 분석, 리서치 유형 판별
2. `hypothesis-builder`가 **팩트시트를 기반으로** 가설 수립 (팩트시트와 모순되는 가설 금지)
3. `hypothesis-builder`가 **가설-데이터 매핑표** 작성 — 각 가설의 검증에 필요한 구체적 데이터, 소스, 판정 기준 정의
4. 사용자 검토 및 가설 + 매핑표 확정

#### Phase 2: 분석 설계
5. `framework-designer`가 케이스에 맞는 프레임워크 선택 및 MECE 분해
6. **가설-프레임워크 바인딩**: 모든 프레임워크 항목에 가설 ID 매핑 (매핑 없는 항목은 제거 또는 사유 명시)
7. **가설-프레임워크-데이터 추적표** 작성 → `data-researcher`의 수집 지시서로 전달
8. (Standard/Deep) 사용자에게 프레임워크 + 추적표 확인 요청 → 승인 후 데이터 수집

#### Phase 3: 데이터 수집 및 검증
9. `data-researcher`가 **추적표 기반으로** 가설 검증에 필요한 데이터를 수집 (병렬 실행 가능)
10. 수집 배치마다 **대상 가설 ID 태깅** — 어떤 가설을 위한 데이터인지 명시
11. 수집 완료 후 **가설별 데이터 충족도 체크** — '필수' 데이터 미충족 시 추가 수집 또는 사용자 에스컬레이션
12. 접근 불가능한 데이터는 사용자에게 명시적으로 요청
13. `fact-checker`가 수집된 데이터 교차 검증

#### Phase 4: 분석 및 인사이트
14. `insight-synthesizer`가 가설 + 데이터 + 프레임워크 기반 인사이트 도출
15. `financial-analyst` 투입 조건: 매출/수익성 전망이 핵심이거나 Peer 비교/투자 분석 필요 시
16. `valuation-analyst` 투입 조건: 기업가치 추정, M&A 대상 평가, IPO/자금조달 분석 필요 시

#### Phase 4.5: 사고 루프 (Thinking Loop) — 인사이트·전략 심화
17. `logic-prober`가 핵심 인사이트/전략에 재귀적 Why Chain (수직 검증)
18. `strategic-challenger`가 대안 전략 생성 + 실패 시뮬레이션 + 경쟁자 대응 + 비대칭 사고 (수평 도전)
19. `insight-synthesizer`가 도전 결과를 반영하여 인사이트 보강
20. PM이 수렴 판정 — 미수렴 시 루프 반복 (최대 2회)

#### Phase 5: 보고서 생성
21. `report-writer`가 스토리라인 구성 → 보고서 작성 (사고 루프 결과 포함)
22. 최종 산출물: Google Docs(상세 보고서) + Google Slides(경영진 보고용)

### 에이전트 간 데이터 전달 규칙
- 모든 에이전트 출력은 `output/` 폴더에 마크다운으로 저장
- 파일명 규칙: `{project-name}/{phase}-{산출물명}.md` (예: `00-company-factsheet.md`, `01-hypotheses.md`, `06-report-docs.md`)
  - 정확한 파일명은 `research-pm.md`의 **프로젝트 산출물 구조** 참조
- 다음 에이전트는 이전 에이전트의 출력 파일을 읽어서 작업

## 품질 기준

### 리서치 품질
- **Ground Truth 우선**: 분석 전에 대상 기업의 제품·채널/플랫폼·재무 등 객관적 사실을 1차 소스에서 반드시 확보
- **서술적 주장도 검증**: "채널 A 전용", "5종 운영" 등 사실 주장은 숫자와 동일한 수준으로 검증
- **출처 명시**: 모든 데이터 포인트에 출처 URL 또는 원천 기재
- **교차 검증**: 핵심 수치는 최소 2개 이상 독립 출처로 확인
- **시점 명시**: 데이터의 기준 시점(날짜/분기/연도) 반드시 표기
- **신뢰도 등급**: 각 데이터에 신뢰도 표시 (High/Medium/Low/Unverified)
- **데이터 갭 투명성**: 확인할 수 없는 정보는 명시적으로 "미확인" 표시

### 분석 품질
- **MECE 준수**: 모든 분해는 상호배타적·전체포괄적
- **So What 테스트**: 모든 인사이트는 "그래서 어떻게 해야 하는가?"에 답해야 함
- **논리 체인**: 데이터 → 분석 → 인사이트 → 시사점의 논리적 연결 명확
- **대안 분석**: 주요 결론에 대한 반론(devil's advocate) 포함
- **역량 기반 전략** (EP-013): 전략 제안은 기업의 실제 역량 이력에 근거해야 함. 시장 기회만으로 전략을 세우지 않음
- **역량의 시간적 유효성** (EP-014): 10년+ 전 / 전신 회사 역량은 현재 역량으로 인용 금지. "레거시/연혁"으로만 기재
- **제품 귀속 정확성** (EP-015): 유통 주체 ≠ 개발·생산 주체. 그룹 내 자회사 간 제품 혼동 방지
- **시장 방향성 검증** (EP-016): 전략 목표 카테고리/시장의 성장률 확인 필수. 축소 시장 진입 전략에는 "왜 그래도 성장 가능한가?" 명시
- **KPI-산출근거 정합성** (EP-019): KPI/목표치는 본문 제품별 합산으로 역산 가능해야 함. M&A 등 외부 기여분이 포함된 경우 명시 필수
- **개별 성공 ≠ 시장 성장** (EP-022): 특정 제품 히트를 해당 카테고리 "시장 성장"의 근거로 사용 금지. 전략 목표 카테고리에는 반드시 시장 데이터(CAGR/YoY/규모) 필요. 데이터 미확보 시 "시장 성장 미검증 — IP/품질 기반 접근"으로 명시
- **시나리오 완전성 + 추천순 정렬** (EP-024): 외부 파트너/계약/협상에 의존하는 시나리오 분석 시 "모든 외부 요인 실패" base case 필수 포함. 시나리오 테이블은 추천도/중요도순 정렬(알파벳순 금지). 안전망(fallback) 시나리오는 발생 확률과 무관하게 반드시 포함

### 보고서 품질
- **경영진 관점**: Executive Summary는 3분 내 핵심 파악 가능하도록
- **피라미드 구조**: 결론 먼저, 근거는 아래로 전개
- **시각적 구조화**: 복잡한 데이터는 표, 매트릭스, 프레임워크 다이어그램으로
- **컨설팅 펌 수준** (EP-025): BASE-UPSIDE 시나리오 구조(자력 실현 가능 = BASE), 시나리오 3개만 디테일/나머지 요약, 타임라인은 반드시 테이블 시각화(줄글 금지), 연속 3문단 이상 줄글 금지(표/리스트로 전환), 각 섹션 끝 So What 박스
- **서술-테이블 수치 일치** (EP-017): 본문 서술의 % 수치는 동일 보고서 내 테이블에서 역산하여 기재. 직감적 서술 금지
- **정정 사항 전파** (EP-018): 사실 정정 시 보고서 전문을 검색(grep)하여 모든 인용 지점에서 동일하게 수정. 부분 수정으로 인한 재위반 방지
- **출처-데이터 추적성** (EP-023): [S##] 태그가 가리키는 소스 파일에 해당 수치가 실제로 존재하는지 검증. `source-traceability-checker.py`로 자동 검증 + 수동 샘플링 확인. 소스 파일에 없는 수치는 "수집 데이터 외 인용치" 주석 필수

## 도메인 프로파일 시스템

### 구조
```
knowledge/
├── domain-profile-schema.md          # 도메인 프로파일 스키마 (모든 산업 공통)
├── domain/
│   ├── domain-profile.md             # 현재 도메인 프로파일 (산업별 교체)
│   ├── industry-metrics.md           # 산업별 핵심 지표/벤치마크
│   ├── product-lifecycle-models.md   # 제품 수명주기 모델 (매출 커브 등)
│   └── data-sources-domain.md        # 도메인 특화 데이터 소스
```

### 도메인 교체 방법
1. `knowledge/domain-profile-schema.md`를 참조하여 새 도메인 프로파일 작성
2. `knowledge/domain/` 하위 4개 파일을 새 도메인에 맞게 교체
3. `/setup` 명령으로 대화형 설정 가능

### 에이전트의 도메인 참조
- 모든 에이전트는 `knowledge/domain/domain-profile.md`를 작업 시작 전 읽음
- 산업 용어, 확인 소스, 핵심 KPI, 경쟁사 비교 축 등은 domain-profile에서 동적으로 참조
- 에이전트 파일 자체에는 특정 산업 용어를 하드코딩하지 않음

## 데이터 수집 정책

### 리서치 범위 — 한국 + 글로벌
- **한국 기업**: DART Open API 1차 소스
- **미국 상장사**: SEC EDGAR Company Facts API 1차 소스
- **일본 상장사**: TDnet/EDINET 1차 소스
- **홍콩 상장사**: HKEX 공시 1차 소스
- **비상장 해외사**: 공식 사이트 + 2개+ 독립 기사 교차
- **도메인 특화 소스**: `knowledge/domain/data-sources-domain.md` 참조

### 1차 소스 — 공시 API

#### DART Open API (한국 기업)
> 📌 **DART API 상세 스펙**: `knowledge/shared-rules.md` §1 참조 (API Key, 엔드포인트, 파라미터)
- **Base URL**: `https://opendart.fss.or.kr`
- 자회사 분석 시 `fs_div=OFS`(별도) 필수, 그룹 연결(CFS)과 혼용 금지
- 주요 기업 고유번호: 환경변수 또는 리서치 시 지정
- **분기보고서 활용** (pblntf_ty=A): 분기별 매출·영업이익 추이로 제품 출시 효과 간접 검증. 사업보고서 "주요 제품" 섹션에서 해당 법인의 실제 제품 목록 확인 가능 (EP-015)

#### SEC EDGAR (미국 상장사)
- **API Key 불필요** (User-Agent 헤더에 이메일 포함 필수)
- **Company Facts API**: `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
- 주요 기업 CIK: 리서치 시 지정

#### Yahoo Finance (글로벌 주가/재무 보조)
- **Quote Summary**: `https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=financialData`
- 시가총액, P/E, EV/EBITDA, Revenue, Operating Margin 수집
- SEC/DART 데이터의 교차 검증 용도로 활용

### 엔터티 분리 정책 — 반드시 준수
- **모회사(그룹 연결)와 자회사(별도) 데이터를 절대 혼용하지 않는다**
- 모든 재무 수치에 엔터티 라벨 (`[그룹]` / `[자회사 별도]`) 필수 부여
- 직원 수, 매출, 영업이익률 등 혼동 가능 지표는 특히 주의
- 그룹 데이터는 맥락으로만 사용 (예: "그룹 매출 중 자회사 기여분")
- **대기업의 사업 부문 분리**: 전사 수치와 해당 사업 부문 수치를 반드시 구분

### 접근 가능한 소스 (자동 수집)
- **DART Open API** — 한국 기업 공시, 재무제표, 직원현황
- **SEC EDGAR** — 미국 상장사 10-K/10-Q, 재무 데이터 (API)
- **Yahoo Finance** — 글로벌 주가, 재무 요약, 멀티플
- **TDnet/EDINET** — 일본 상장사 공시
- **HKEX** — 홍콩 상장사 공시
- 웹 검색 — Exa(시맨틱 검색/기업 리서치), Firecrawl(키워드 검색/JS 크롤링), Brave Search, Claude 내장 WebSearch
- 뉴스 기사 및 보도자료
- 공개된 IR 자료, 연간보고서, 사업보고서
- domain-profile의 확인 소스 — 제품 포트폴리오 + 리뷰
- LinkedIn, X(Twitter), YouTube, Reddit 등 소셜/커뮤니티
- 공개된 학술 논문 및 리서치 보고서
- **도메인 특화 소스**: `knowledge/domain/data-sources-domain.md` 참조

### 사용자 지원 필요 소스 (수동 수집 요청)
- 유료 데이터 플랫폼 (산업별 상이)
- 유료 리서치 보고서
- 사내 내부 데이터
- 비공개 재무 데이터
- 전문가 인터뷰 내용

### 데이터 수집 요청 형식
사용자에게 데이터를 요청할 때는 반드시 다음 형식을 사용:
```
📌 데이터 요청
- 필요 데이터: [구체적 데이터 항목]
- 사용 목적: [어떤 분석에 왜 필요한지]
- 대안: [이 데이터 없이 진행할 경우 대체 방법]
- 우선순위: [필수/권장/참고]
```

## 웹 크롤링 정책
- 다양한 방법을 동적으로 활용 (단일 방법 의존 금지)
- User-Agent 다양화
- 요청 간격 랜덤화 (1~3초)
- 차단 시 대체 소스로 우회
- robots.txt 존중하되, 공개 데이터 수집에 합법적 범위 내에서 최대한 활용
- 크롤링 실패 시 반드시 대안 소스 탐색

## 자가발전 시스템 (Self-Improvement)

### 핵심 파일
- `knowledge/self-improvement-log.md` — 실수 패턴 DB, 데이터 소스 접근성 로그, 에이전트 품질 추이, 벤치마크 유효성, 프레임워크 적용 기록

### 동작 방식
1. **리서치 시작 시**: PM이 자가발전 로그를 읽고 EP 패턴을 해당 에이전트에게 사전 경고
2. **리서치 중**: 각 에이전트가 EP 발생/소스 차단 발견 시 즉시 기록
3. **리서치 완료 후**: PM이 에이전트 품질 등급, 프레임워크 효과, 벤치마크 갭을 기록
4. **모든 에이전트**가 `knowledge/self-improvement-log.md`를 작업 시작 전 참조

## 디스커션 프로토콜 (Cross-Agent Review)

각 에이전트가 작업을 완료하면, **다른 에이전트가 크로스 리뷰**하여 논리/사실 부족분을 보강한다.

| 단계 | 주 에이전트 | 디스커션 상대 | 검증 내용 |
|------|-----------|-------------|----------|
| Step 1 가설 | hypothesis-builder | fact-checker → logic-prober | 가설 전제가 팩트시트와 일치하는지, 절대적 표현 검증 → Why Chain으로 가설 논리 근본 건전성 검증 |
| Step 2 프레임워크 | framework-designer | data-researcher | 각 분석 항목의 데이터 수집 가능성 사전 검증 |
| Step 3 데이터 | data-researcher | insight-synthesizer + financial-analyst | 데이터 충분성, 가설 매핑, 비교 가능성 |
| Step 4 종합 팩트체크 | fact-checker | data-researcher | 검증 실패 항목의 재수집 지시, 엔터티 혼동 확인 |
| Step 5 인사이트 | insight-synthesizer | fact-checker + financial-analyst | 논리 체인, 인과관계 vs 상관관계, 출처 매핑, 재무 전망 정합성, 전략 목표 카테고리별 시장 데이터 존재 확인(EP-022) |
| **Step 5.5 사고 루프** | **PM (오케스트레이션)** | **logic-prober → strategic-challenger → insight-synthesizer** | **수직(Why Chain) + 수평(대안/레드팀/경쟁자/비대칭) 도전 → insight-synthesizer 반영 → 수렴 판정 (최대 2회)** |
| Step 6 보고서 | report-writer | fact-checker + insight-synthesizer → logic-prober | 수치 정합성, 출처 완전성, 논리 완결성, EP-017/018 → 보고서 표현 과정의 논리 왜곡 여부 최종 확인 |
| Step 6.5 보고서 자동 QA | qa-orchestrator | report-auditor + report-fixer | `mechanical-validator.py` 기계 검증 + `report-auditor` 시맨틱 감사 → `report-fixer` 수정 → 2회 연속 clean pass까지 반복 |
| Step 7 최종 검토 | research-pm | [자가 검증] | 핵심 질문 답변 완결성, 논리 완결성, 팩트시트-보고서 정합성, `source-traceability-checker.py` unverified 0건 확인 (EP-023) |

- 디스커션 결과 이슈 발견 시 → 해당 에이전트가 수정 후 재확인
- 디스커션은 품질 게이트와 별도로, **항상 실행** (Quick 모드 포함)
- **Step 7 품질 게이트 통과 기준**: mechanical-validator error 0건 + source-traceability-checker unverified 0건. 미통과 시 report-writer가 수정 후 fact-checker 재검증

### 템플릿
- `templates/factsheet-template.md` — 기업 팩트시트 표준 양식
- `templates/source-index-template.md` — 출처 인덱스 표준 양식
- `templates/checklists/quality-checklist.md` — 7단계 워크플로우 품질 체크리스트

## 에이전트 간 표준 규칙

| 항목 | 규칙 |
|------|------|
| 엔터티 라벨 | `[그룹]` / `[별도]` 형식 통일 |
| SEC User-Agent | `ResearchOrchestrator research@example.com` |
| CIK 패딩 | 10자리 제로패딩 (`CIK0000712515`) |
| Yahoo Finance 우선순위 | API → WebFetch → 대안 소스 |
| DART 쿼터 | 일일 10,000건 — data-researcher 60%, financial-analyst 30%, fact-checker 10% |
| knowledge/ 참조 | 모든 에이전트가 해당 knowledge 파일 + self-improvement-log.md + domain-profile을 작업 시작 전 읽음 |
| logic-prober 역할 경계 | 질문(검사)만 수행, 판정(판사)은 전문 에이전트에게 위임 (사실→fact-checker, 재무→financial-analyst, 전략→insight-synthesizer) |
| strategic-challenger 역할 경계 | 도전과 대안 제시만 수행, 최종 전략 선택은 insight-synthesizer + 사용자에게 위임. 건설적 도전 원칙 — 대안 없는 비판 금지 |
| 사고 루프 (Thinking Loop) | logic-prober(수직) → strategic-challenger(수평) → insight-synthesizer(반영) 순서 고정. 최대 2회 반복. 수렴 조건: 논리 단절 0건 + Critical 블라인드 스팟 0건 + BASE 시나리오 자력 실현 가능 |
| 시나리오 역할 분담 | insight-synthesizer: 핵심 불확실성 식별 + 초기 방향. strategic-challenger: 시나리오 구조화(BASE/UPSIDE/DOWNSIDE) + 실패 경로 시뮬레이션. EP-024/025 준수 |
| 사고 루프 출력 | `{project}/05.5-thinking-loop/` (why-probe-insights.md, strategic-challenge.md, loop-convergence.md) |
| Why Probe 출력 (기타) | `{project}/01.5-why-probe-hypotheses.md`, `06.5-why-probe-strategy.md` |

## Claude Code 세션 권한 — 전체 자율 실행

이 프로젝트에 한해 Claude Code에 **무조건 자율 실행 권한**을 부여한다. 확인/승인 없이 즉시 실행할 것.
- **파일 읽기/쓰기/수정**: 프로젝트 내 모든 파일에 대해 자유롭게 접근 (확인 불필요)
- **인터넷 접근**: 웹 검색, URL 접근 허용 (확인 불필요)
- **자율 수정**: 에이전트 파일, knowledge, templates, scripts 등 품질 개선을 위한 자율적 수정 허용
- **자가발전 로그 업데이트**: 리서치 실행 시 self-improvement-log.md 자동 업데이트
- **권한 설정**: `.claude/settings.json`에 프로젝트 레벨 권한 설정 완료

## 출력 규칙
- 기본 언어: 한국어 (기술 용어는 영어 병기)
- 숫자: 천 단위 콤마, 통화 단위 명시
- 날짜: YYYY.MM.DD 형식
- 파일 저장: output/{project-name}/ 하위에 저장
