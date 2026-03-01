# Consulting Agent

**컨설팅급 리서치 자동화 시스템** — Claude Code 커스텀 에이전트 기반.
주제가 주어지면 가설 수립부터 보고서 생성까지 전 과정을 오케스트레이션한다.

**도메인 독립 설계**: 도메인 프로파일만 교체하면 게임, 바이오, SaaS, 반도체 등 어떤 산업이든 동일 파이프라인으로 리서치 가능.
**한국 + 글로벌** 기업 리서치 지원 (DART, SEC EDGAR, Yahoo Finance, TDnet 통합).

---

## Quick Start

### 1. 사전 요건
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) 설치 + Claude 구독 (Pro/Max 모두 지원. Pro는 사용량 한도가 낮으므로 Deep 리서치 시 Max 권장)
- Node.js 18+, Python 3.8+

### 2. 설치
```bash
git clone https://github.com/koobch/consulting-agent.git
cd consulting-agent
claude
```

### 3. 대화형 설정
Claude Code 안에서 실행:
```
/setup
```

`/setup` 이 API 키 발급, MCP 서버 설치, 도메인 프로파일 선택, 검증까지 한 단계씩 안내합니다.

### 4. 설정 확인
```
/setup-check
```
현재 설정 상태를 테이블로 출력합니다.

### 5. 리서치 시작
```
{대상 기업} 전략 리서치 시작해
```
`research-pm` 에이전트가 전체 워크플로우를 오케스트레이션합니다.

---

## 워크플로우

```
팩트시트 확보 → 가설 수립 → 프레임워크 설계 → 데이터 수집+실시간 검증 → 종합 팩트체크 → 인사이트 도출 → 보고서 작성
     ↑                                              ↑
  사용자 승인 #1                              사용자 승인 #2, #3
```

### 리서치 깊이 레벨
| 레벨 | 용도 | 소스 수 | 사용자 게이트 | 보고서 분량 |
|------|------|--------|-------------|-----------|
| **Quick** | 빠른 현황 파악 | 2~3/카테고리 | 팩트시트만 | 5~10p |
| **Standard** | 일반 리서치 | 5~8/카테고리 | 3곳 | 15~25p |
| **Deep** | C-level 보고 | 10+/카테고리 | 4곳 | 25~40p |

---

## 에이전트 아키텍처

```
[사용자] → [research-pm] 오케스트레이터
              ├── hypothesis-builder     가설 수립 (팩트시트 기반)
              ├── framework-designer     프레임워크/MECE 분해
              ├── data-researcher        데이터 수집 (병렬, 다중소스, DART+SEC+Yahoo)
              ├── fact-checker           팩트체크/실시간 검증/출처 검증
              ├── insight-synthesizer    인사이트 도출 (So What 테스트)
              ├── report-writer          보고서 생성 (Docs/Slides)
              ├── financial-analyst      재무 분석 (DART+SEC EDGAR+Yahoo Finance)
              └── valuation-analyst      밸류에이션 (DCF/멀티플/SOTP)
```

---

## 도메인 프로파일 시스템

도메인별 산업 지식을 분리하여 에이전트 코드 수정 없이 산업을 교체할 수 있습니다.

```
knowledge/
├── domain-profile-schema.md          # 스키마 정의 (공통)
├── domain/
│   ├── domain-profile.md             # 현재 도메인 — 산업 개요, 밸류체인, 핵심 KPI
│   ├── industry-metrics.md           # 벤치마크, 시장 규모, 경쟁 지표
│   ├── product-lifecycle-models.md   # 제품 수명주기 모델 (매출 커브 등)
│   └── data-sources-domain.md        # 도메인 특화 데이터 소스
```

새 도메인 설정: `/setup` 실행 → 도메인 선택 단계에서 템플릿 생성.

---

## API / MCP 설정 레퍼런스

`/setup`으로 자동 설정되지만, 수동 설정이 필요한 경우 아래를 참조합니다.

### 필수

| 항목 | 유형 | 무료 | 발급 URL | 용도 |
|------|------|------|---------|------|
| DART Open API | API Key | ✅ | https://opendart.fss.or.kr | 한국 기업 공시/재무 |
| Exa | MCP Server | ✅ (월 1,000) | https://exa.ai | 시맨틱 검색 |
| Firecrawl | MCP Server | ✅ (월 500) | https://firecrawl.dev | 웹 크롤링 (JS 렌더링) |
| Brave Search | MCP Server | ✅ (월 2,000) | https://brave.com/search/api/ | 웹 검색 |
| Fetch | MCP Server | ✅ (키 불필요) | — | 웹 페이지 가져오기 |

### 선택 (공통 + 도메인별)

| 항목 | 무료 | 발급 URL | 용도 |
|------|------|---------|------|
| FRED API | ✅ | https://fred.stlouisfed.org/docs/api/api_key.html | 미국 경제 지표 |
| ECOS API | ✅ | https://ecos.bok.or.kr/api/ | 한국 경제 통계 |
| NewsAPI | ✅ | https://newsapi.org/register | 뉴스 검색 |

> 도메인 특화 API는 `/setup` 실행 시 Step 8.5에서 자동 리서치되어 추가됩니다.

### 1차 소스 (공시 API — 키 불필요 또는 별도)
| 지역 | 시스템 | API | 대상 |
|------|--------|-----|------|
| **한국** | DART Open API | `opendart.fss.or.kr` | 한국 기업 공시 |
| **미국** | SEC EDGAR | `data.sec.gov` (키 불필요) | 미국 상장 기업 |
| **글로벌** | Yahoo Finance | `query2.finance.yahoo.com` (키 불필요) | 전 세계 주가/재무 |
| **일본** | TDnet/EDINET | `disclosure.edinet-fsa.go.jp` | 일본 상장 기업 |
| **홍콩** | HKEX | `hkexnews.hk` | 홍콩 상장 기업 |

### MCP 서버 수동 설치 커맨드
```bash
claude mcp add exa -e EXA_API_KEY=<key> -- npx -y exa-mcp-server
claude mcp add firecrawl -e FIRECRAWL_API_KEY=<key> -- npx -y firecrawl-mcp
claude mcp add brave-search -e BRAVE_API_KEY=<key> -- npx -y @anthropic/brave-search-mcp
claude mcp add fetch -- npx -y @anthropic/fetch-mcp
```

---

## 디렉토리 구조

```
consulting-agent/
├── .claude/
│   ├── agents/              # 커스텀 에이전트 정의
│   └── commands/            # 스킬 (/setup, /setup-check)
├── knowledge/               # 지식베이스 (에이전트가 참조)
│   ├── domain-profile-schema.md  # 도메인 프로파일 스키마
│   ├── domain/              # 현재 도메인 프로파일 (산업별 교체)
│   ├── consulting-frameworks.md
│   ├── data-sources.md
│   ├── shared-rules.md      # SSOT — API 스펙, 공통 규칙
│   └── self-improvement-log.md
├── templates/               # 표준 양식 및 체크리스트
├── scripts/                 # 검증 스크립트 + Google Workspace 변환
├── output/{project}/        # 리서치 산출물 (프로젝트별)
├── CLAUDE.md                # 프로젝트 컨텍스트 및 품질 기준
├── requirements.txt         # Python 의존성
└── README.md
```

---

## 핵심 메커니즘

### 실시간 검증 루프
```
[data-researcher] → 데이터 배치 수집
      ↓
[fact-checker] 실시간 검증
      ↓
  PASS → 다음 배치  |  FAIL → 재수집 (최대 2회) → 사용자 에스컬레이션
```

### 디스커션 프로토콜 (Cross-Agent Review)
각 에이전트 작업 완료 후, 다른 에이전트가 크로스 리뷰하여 논리/사실 부족분을 보강:

| 단계 | 주 에이전트 | 리뷰 에이전트 | 검증 내용 |
|------|-----------|-------------|----------|
| 가설 | hypothesis-builder | fact-checker | 팩트시트 정합성 |
| 프레임워크 | framework-designer | data-researcher | 데이터 수집 가능성 |
| 데이터 | data-researcher | insight-synthesizer | 데이터 충분성 |
| 인사이트 | insight-synthesizer | fact-checker | 논리 체인, 반론 |
| 보고서 | report-writer | fact-checker | 수치 정합성, 출처 |

### 자가발전 시스템
리서치 품질을 프로젝트마다 향상시키는 피드백 루프. 실수 패턴(EP), 소스 접근성, 벤치마크 갭을 자동 기록하고 다음 리서치에 반영.

---

## 품질 기준

- **Ground Truth 우선**: 분석 전 팩트시트(제품 포트폴리오, 채널/플랫폼, 재무) 반드시 확보
- **출처 명시**: 모든 데이터에 출처 URL + [S##] 인덱스
- **교차 검증**: 핵심 수치 최소 2개 독립 출처
- **실시간 검증**: 수집과 동시에 팩트체크 루프 운영
- **MECE 구조**: 분석 프레임워크 전체 MECE 원칙 적용
- **So What 테스트**: 모든 인사이트에 실행 가능한 시사점 포함

---

## 사용법

### 전체 리서치 (PM 오케스트레이션)
```
{대상 기업} 전략 리서치 시작해
```

### 개별 에이전트 호출
```bash
claude "A사 시장 진입 가설 수립해" --agent hypothesis-builder
claude "이 보고서 팩트체크해" --agent fact-checker
claude "A사 vs B사 재무 비교 분석해" --agent financial-analyst
```

### Google Docs/Slides 변환
1. [script.google.com](https://script.google.com) 에서 새 프로젝트 생성
2. `scripts/` 폴더의 `.gs` 코드 붙여넣기
3. 마크다운 내용 입력 → 함수 실행 → Google Drive에 문서 생성

---

## License

MIT
