# Consulting Agent

**컨설팅급 리서치 자동화 시스템** — Claude Code 커스텀 에이전트 기반.

기업 또는 산업 주제가 주어지면 팩트시트 확보 → 가설 수립 → 프레임워크 설계 → 데이터 수집·검증 → 인사이트 도출 → 보고서 생성까지 전 과정을 에이전트 팀이 오케스트레이션한다.

- **도메인 독립 설계** — 도메인 프로파일만 교체하면 바이오, SaaS, 반도체, 제조업 등 어떤 산업이든 동일 파이프라인으로 리서치 가능
- **한국 + 글로벌** — DART, SEC EDGAR, Yahoo Finance, TDnet/EDINET 통합
- **자가발전** — 리서치마다 실수 패턴, 소스 접근성, 벤치마크를 자동 축적하여 다음 리서치 품질 향상

---

## Quick Start

### 1. 사전 요건

| 항목 | 요건 | 비고 |
|------|------|------|
| Claude Code CLI | [설치 가이드](https://docs.anthropic.com/en/docs/claude-code) | `npm install -g @anthropic-ai/claude-code` |
| Claude 구독 | Pro 또는 Max | Pro로 Quick/Standard 가능. Deep 리서치(대량 에이전트 병렬)에는 Max 권장 |
| Node.js | 18+ | MCP 서버 실행에 필요 |
| Python | 3.8+ | 품질 검증 스크립트에 필요 |

### 2. 설치

```bash
git clone https://github.com/koobch/consulting-agent.git
cd consulting-agent
claude
```

### 3. 대화형 설정

Claude Code 세션 안에서:

```
/setup
```

`/setup`이 아래를 **한 단계씩** 안내합니다:

1. 사전 요건 체크 (Node.js, Python)
2. Python 의존성 설치
3. 환경 파일 생성 (`~/.research-orchestrator.env`)
4. API 키 발급 및 설정 (DART, Exa, Firecrawl, Brave Search)
5. MCP 서버 등록
6. 도메인 프로파일 설정 (산업 선택)
7. 도메인 특화 API 자동 리서치 및 추가

각 단계는 건너뛸 수 있으며, 나중에 `/setup`을 다시 실행해도 됩니다.

### 4. 설정 확인

```
/setup-check
```

현재 설정 상태를 테이블로 출력합니다. 누락된 항목이 있으면 해결 방법을 안내합니다.

---

## 리서치 시작하기

### 기본 사용

```
{대상 기업} 리서치 시작해
```

이것만으로도 `research-pm`이 리서치 유형/깊이를 판단하고 워크플로우를 시작합니다.

하지만 **요청이 구체적일수록 결과 품질이 높아집니다.** 아래 요소를 포함하면 PM이 더 정확한 리서치 플랜을 세울 수 있습니다.

### 더 나은 리서치 요청 작성법

| 요소 | 설명 | 예시 |
|------|------|------|
| **대상** | 분석할 기업 또는 산업 | "A사", "국내 B2B SaaS 시장" |
| **목적** | 리서치 결과로 어떤 의사결정을 하려는지 | "신사업 진출 판단", "투자 검토", "경쟁 대응 전략" |
| **비교 대상** | 벤치마크/경쟁사가 있다면 명시 | "B사, C사와 비교", "글로벌 Top 5 대비" |
| **깊이** | Quick / Standard / Deep | 기본값은 Standard |
| **초점 영역** | 특별히 깊게 봐야 할 부분 | "해외 매출 비중 변화", "M&A 히스토리" |
| **제약/맥락** | 알고 있는 배경 정보 | "최근 대표이사 교체", "작년 적자 전환" |
| **산출물** | 원하는 결과물 형태 | "경영진 보고용 슬라이드", "내부 브리핑 문서" |

### 요청 예시

**간단한 요청** (PM이 구체화 질문을 추가로 함):
```
A사 전략 리서치해줘
```

**구체적인 요청** (바로 리서치 플랜 수립):
```
A사 전략 리서치를 Deep으로 해줘.

- 목적: A사의 해외 시장 진출 전략 수립을 위한 기초 리서치
- 비교 대상: B사, C사, D사 (해외 매출 비중 높은 동종 기업)
- 초점: 해외 매출 비중 변화 추이, 진출 시장별 성과, 현지화 전략
- 맥락: A사는 국내 매출 비중 85%로, 해외 확장이 중기 전략 과제
- 산출물: C-level 보고용 슬라이드 + 상세 보고서
```

**재무 중심 요청**:
```
A사 vs B사 재무 비교 분석.
최근 3년 매출 성장률, 영업이익률, ROE 비교.
A사 밸류에이션이 적정한지 Peer 멀티플 기준으로 평가해줘.
```

### 리서치 깊이 레벨

| 레벨 | 용도 | 소스 수 | 사용자 체크포인트 | 보고서 |
|------|------|--------|-----------------|--------|
| **Quick** | 빠른 현황 파악, 내부 브리핑 | 2~3/카테고리 | 팩트시트 승인만 | 5~10p |
| **Standard** | 정기 리서치, 일반 의사결정 | 5~8/카테고리 | 3곳 (팩트시트, 프레임워크, 데이터) | 15~25p |
| **Deep** | C-level 보고, 전략 의사결정 | 10+/카테고리 | 4곳 + 최종 보고서 리뷰 | 25~40p (Docs+Slides) |

### 인터랙션 모드

리서치 시작 시 PM이 인터랙션 모드를 묻습니다:

| 모드 | 동작 | 적합한 상황 |
|------|------|-----------|
| **Discussion** | 모든 단계에서 디스커션 | 분석에 현업 관점을 깊이 반영하고 싶을 때 |
| **Hybrid** (기본) | 주요 체크포인트에서 리뷰 + 선택적 디스커션 | 대부분의 리서치 |
| **Auto** | 최종 보고서만 리뷰 | 빠른 턴어라운드가 필요할 때 |

진행 중 언제든 모드 변경 가능합니다.

### 개별 에이전트 직접 호출

전체 워크플로우 대신 특정 에이전트만 사용할 수도 있습니다:

```bash
# 가설 수립만
claude "A사의 신사업 진출 가설을 수립해. 현재 포트폴리오는 X, Y, Z이고 해외 매출 비중은 15%" --agent hypothesis-builder

# 팩트체크만
claude "이 보고서의 수치와 출처를 검증해" --agent fact-checker

# 재무 비교 분석만
claude "A사 vs B사 최근 3년 재무 비교. DART 별도 기준으로" --agent financial-analyst

# 밸류에이션만
claude "A사 DCF + Peer 멀티플 밸류에이션. 할인율 10%, 성장률 시나리오 3개" --agent valuation-analyst
```

---

## 워크플로우

```
Phase 0.5    Phase 1      Phase 2         Phase 3            Phase 4        Phase 5
팩트시트  →  가설 수립  →  프레임워크  →  데이터 수집+검증  →  인사이트  →  보고서
    ↑                        ↑              ↑                                  ↑
 사용자 승인 #1         승인 #2         승인 #3                          최종 리뷰
```

각 Phase 사이에 **에이전트 간 크로스 리뷰**(디스커션 프로토콜)가 자동으로 실행됩니다.

| Phase | 주 에이전트 | 크로스 리뷰 | 산출물 |
|-------|-----------|------------|--------|
| 0.5 팩트시트 | data-researcher | — | `00-company-factsheet.md` |
| 1 가설 | hypothesis-builder | fact-checker 검증 | `01-hypotheses.md` |
| 2 프레임워크 | framework-designer | data-researcher 수집가능성 확인 | `02-framework.md` |
| 3 데이터 | data-researcher | fact-checker 실시간 검증 | `03-data-{topic}.md` |
| 4 인사이트 | insight-synthesizer | fact-checker + financial-analyst | `05-insights.md` |
| 5 보고서 | report-writer | fact-checker 수치 정합성 | `06-report-docs.md`, `06-report-slides.md` |

---

## 에이전트 아키텍처

```
[사용자] → [research-pm] 오케스트레이터
              ├── hypothesis-builder     가설 수립 (팩트시트 기반, MECE)
              ├── framework-designer     분석 프레임워크 설계 (가설-데이터 매핑)
              ├── data-researcher        데이터 수집 (병렬, DART+SEC+Yahoo+웹)
              ├── fact-checker           실시간 팩트체크 + 종합 검증 + 출처 검증
              ├── insight-synthesizer    인사이트 도출 (So What 테스트, 시나리오 분석)
              ├── report-writer          보고서 생성 (Google Docs + Slides)
              ├── financial-analyst      재무 분석 (Peer 비교, 멀티플)
              └── valuation-analyst      밸류에이션 (DCF, 멀티플, SOTP)
```

---

## 도메인 프로파일 시스템

도메인별 산업 지식을 분리하여 에이전트 코드 수정 없이 산업을 교체할 수 있습니다.

```
knowledge/
├── domain-profile-schema.md          # 스키마 정의 (공통, 바이오/SaaS/반도체 등 예시 포함)
├── domain/
│   ├── domain-profile.md             # 현재 도메인 — 산업 개요, KPI, 경쟁 비교 축
│   ├── industry-metrics.md           # 벤치마크, 시장 규모 (리서치 시 자동 축적)
│   ├── product-lifecycle-models.md   # 매출 커브, 수명주기 패턴 (리서치 시 자동 축적)
│   └── data-sources-domain.md        # 도메인 특화 데이터 소스 + API
```

새 도메인 설정: `/setup` 실행 → 도메인 선택 → 프로파일 자동 생성 → 도메인 API 자동 리서치.

---

## API / MCP 설정

> `/setup`으로 자동 설정됩니다. 수동 설정이 필요한 경우에만 아래를 참조하세요.

### 필수

| 항목 | 유형 | 무료 | 발급 URL | 용도 |
|------|------|------|---------|------|
| DART Open API | API Key | 무료 | https://opendart.fss.or.kr | 한국 기업 공시/재무 |
| Exa | MCP Server | 월 1,000건 무료 | https://exa.ai | 시맨틱 검색 (기업 리서치) |
| Firecrawl | MCP Server | 월 500건 무료 | https://firecrawl.dev | JS 렌더링 웹 크롤링 |
| Brave Search | MCP Server | 월 2,000건 무료 | https://brave.com/search/api/ | 범용 웹 검색 |
| Fetch | MCP Server | 키 불필요 | — | 웹 페이지 마크다운 변환 |

### 선택

| 항목 | 무료 | 발급 URL | 용도 |
|------|------|---------|------|
| FRED API | 무료 | https://fred.stlouisfed.org/docs/api/api_key.html | 미국 경제 지표 (GDP, CPI, 환율) |
| ECOS API | 무료 | https://ecos.bok.or.kr/api/ | 한국 경제 통계 (환율, 금리) |
| NewsAPI | 무료 (100건/일) | https://newsapi.org/register | 글로벌 뉴스 검색 |

> 도메인 특화 API는 `/setup` 실행 시 Claude가 자동 리서치하여 추가합니다.

### 1차 소스 (공시 API)

| 지역 | 시스템 | 대상 |
|------|--------|------|
| **한국** | DART Open API | 한국 기업 공시, 재무제표, 직원현황 |
| **미국** | SEC EDGAR (키 불필요) | 미국 상장 기업 10-K/10-Q |
| **글로벌** | Yahoo Finance (키 불필요) | 전 세계 주가, 재무 요약, 멀티플 |
| **일본** | TDnet/EDINET | 일본 상장 기업 결산 자료 |
| **홍콩** | HKEX | 홍콩 상장 기업 공시 |

### MCP 서버 수동 설치

```bash
claude mcp add exa -e EXA_API_KEY=<key> -- npx -y exa-mcp-server
claude mcp add firecrawl -e FIRECRAWL_API_KEY=<key> -- npx -y firecrawl-mcp
claude mcp add brave-search -e BRAVE_API_KEY=<key> -- npx -y @anthropic/brave-search-mcp
claude mcp add fetch -- npx -y @anthropic/fetch-mcp
```

---

## 핵심 메커니즘

### 실시간 검증 루프

데이터를 수집한 후 사후 팩트체크하는 것이 아니라, **수집과 동시에 검증**합니다.

```
[data-researcher] → 데이터 배치 수집
      ↓
[fact-checker] 실시간 검증 (교차 검증, 엔터티 라벨, 출처)
      ↓
  PASS → 다음 배치  |  FAIL → 재수집 (최대 2회) → 사용자 에스컬레이션
```

### 디스커션 프로토콜 (Cross-Agent Review)

| 단계 | 주 에이전트 | 리뷰 에이전트 | 검증 내용 |
|------|-----------|-------------|----------|
| 가설 | hypothesis-builder | fact-checker | 팩트시트 정합성 |
| 프레임워크 | framework-designer | data-researcher | 데이터 수집 가능성 |
| 데이터 | data-researcher | insight-synthesizer | 데이터 충분성, 가설 매핑 |
| 인사이트 | insight-synthesizer | fact-checker + financial-analyst | 논리 체인, 반론, 시장 데이터 |
| 보고서 | report-writer | fact-checker | 수치 정합성, 출처 추적성, 서술-테이블 일치 |

### 자가발전 시스템

리서치 품질을 프로젝트마다 향상시키는 피드백 루프:
- **실수 패턴(EP)** 자동 기록 → 다음 리서치에서 사전 경고
- **데이터 소스 접근성 로그** → 차단된 소스 자동 우회
- **벤치마크 갭** → 실측값과 추정값 차이를 다음 리서치에 반영

---

## 품질 기준

- **Ground Truth 우선** — 분석 전 팩트시트(제품 포트폴리오, 채널/플랫폼, 재무) 반드시 확보
- **출처 명시** — 모든 데이터에 출처 URL + [S##] 인덱스
- **교차 검증** — 핵심 수치 최소 2개 독립 출처
- **엔터티 분리** — 그룹(연결)과 자회사(별도) 데이터 혼용 금지
- **MECE 구조** — 분석 프레임워크 전체 상호배타적·전체포괄적
- **So What 테스트** — 모든 인사이트에 실행 가능한 시사점 포함
- **피라미드 구조** — 보고서는 결론 먼저, 근거는 아래로 전개

---

## 산출물 변환 (Google Docs/Slides)

리서치 보고서는 마크다운으로 생성되며, Google Workspace로 변환할 수 있습니다.

1. [script.google.com](https://script.google.com) 에서 새 프로젝트 생성
2. `scripts/` 폴더의 `.gs` 코드 붙여넣기
3. 마크다운 내용 입력 → 함수 실행 → Google Drive에 문서 생성

| 스크립트 | 용도 |
|---------|------|
| `convert-all.gs` | Docs + Slides 올인원 변환 |
| `markdown-to-google-docs.gs` | 상세 보고서 → Google Docs |
| `markdown-to-google-slides.gs` | 경영진 보고서 → Google Slides |

---

## 디렉토리 구조

```
consulting-agent/
├── .claude/
│   ├── agents/              # 커스텀 에이전트 8종 정의
│   └── commands/            # /setup, /setup-check 스킬
├── knowledge/               # 지식베이스 (에이전트가 참조)
│   ├── domain-profile-schema.md  # 도메인 프로파일 스키마
│   ├── domain/              # 현재 도메인 프로파일 (산업별 교체)
│   ├── consulting-frameworks.md  # 컨설팅 프레임워크 라이브러리
│   ├── data-sources.md      # 범용 데이터 소스 가이드
│   ├── shared-rules.md      # SSOT — API 스펙, 엔터티 규칙, 공통 규칙
│   └── self-improvement-log.md   # 자가발전 로그 (EP, 소스 접근성)
├── templates/               # 팩트시트, 출처 인덱스, 품질 체크리스트
├── scripts/                 # 품질 검증 + Google Workspace 변환
├── output/{project}/        # 리서치 산출물 (프로젝트별)
├── CLAUDE.md                # 프로젝트 컨텍스트 및 품질 기준
├── requirements.txt
└── README.md
```

---

## License

MIT
