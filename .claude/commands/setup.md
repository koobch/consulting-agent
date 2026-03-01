# /setup — Research Orchestrator 대화형 설정 마법사

사용자의 환경에 Research Orchestrator를 설치·설정한다.
**한 번에 하나의 단계만** 진행하고, 각 단계별 검증 후 다음으로 넘어간다.

아래 플로우를 정확히 따라 실행하라.

---

## Step 0: 사전 요건 체크

다음 명령어를 실행하여 사전 요건을 확인한다:

```bash
node --version 2>/dev/null || echo "NOT_FOUND"
python3 --version 2>/dev/null || echo "NOT_FOUND"
```

**판정**:
- Node.js 18+ 필요 (MCP 서버 실행에 필요)
- Python 3.8+ 필요 (검증 스크립트 실행에 필요)
- 누락 시 설치 방법 안내 후 재확인

결과를 사용자에게 보여주고, 실패 항목이 있으면 설치 안내 후 계속 진행할지 묻는다.

---

## Step 1: Python 의존성 설치

```bash
pip3 install -r requirements.txt
```

**WHY**: `mechanical-validator.py`, `source-traceability-checker.py` 등 품질 검증 스크립트에 `markdown` 패키지가 필요하다.

**VERIFY**:
```bash
python3 -c "import markdown; print('OK:', markdown.version)"
```

---

## Step 2: 환경 파일 생성

`~/.research-orchestrator.env` 파일을 생성하고 shell에서 자동 로드되도록 설정한다.

1. 파일이 이미 존재하는지 확인:
```bash
test -f ~/.research-orchestrator.env && echo "EXISTS" || echo "NOT_FOUND"
```

2. 파일이 없으면 빈 템플릿 생성:
```bash
cat > ~/.research-orchestrator.env << 'ENVEOF'
# Research Orchestrator — API Keys
# 이 파일은 ~/.zshrc에서 자동 source됩니다.
# 발급받은 키를 아래에 입력하세요.

# [필수] DART Open API (한국 기업 공시)
# export DART_API_KEY="your-key-here"

# [필수 — MCP] Exa (시맨틱 검색)
# export EXA_API_KEY="your-key-here"

# [필수 — MCP] Firecrawl (웹 크롤링)
# export FIRECRAWL_API_KEY="your-key-here"

# [필수 — MCP] Brave Search (웹 검색)
# export BRAVE_API_KEY="your-key-here"

# [선택 — 공통] FRED API (미국 경제 지표)
# export FRED_API_KEY="your-key-here"

# [선택 — 공통] ECOS API (한국은행 경제 통계)
# export ECOS_API_KEY="your-key-here"

# [선택 — 공통] NewsAPI (뉴스 검색)
# export NEWSAPI_KEY="your-key-here"

# [선택 — 도메인 특화] Step 8.5에서 리서치된 API 키를 아래에 추가
ENVEOF
```

3. `~/.zshrc`에 자동 로드 설정 (중복 방지):
```bash
grep -q 'research-orchestrator.env' ~/.zshrc 2>/dev/null || echo '
# Research Orchestrator
[ -f ~/.research-orchestrator.env ] && source ~/.research-orchestrator.env' >> ~/.zshrc
```

**사용자에게 안내**: "API 키 파일이 생성되었습니다. 이제 하나씩 API 키를 발급받아 설정하겠습니다."

---

## Step 3: DART Open API Key (필수, 무료)

**WHY**: 한국 기업의 재무제표, 직원현황, 사업보고서 등 공시 데이터를 조회하는 핵심 API.

**HOW**:
1. https://opendart.fss.or.kr 접속
2. 회원가입 (무료)
3. [인증키 신청] → 즉시 발급
4. 발급받은 키를 알려주세요

사용자가 키를 입력하면:
1. `~/.research-orchestrator.env`에서 DART_API_KEY 줄의 주석을 해제하고 키를 입력
2. 검증:
```bash
source ~/.research-orchestrator.env && curl -s "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=${DART_API_KEY}" -o /tmp/dart_test.xml && head -c 200 /tmp/dart_test.xml
```
- 정상: XML 응답 (zip 바이너리)
- 실패: `"인증키가 유효하지 않습니다"` 메시지

**SKIP**: 건너뛰면 한국 기업의 DART 공시 데이터(재무제표, 직원현황)를 자동 조회할 수 없음. 웹 검색으로 대체하나 정확도/속도가 떨어짐.

---

## Step 4: MCP — Exa (필수)

**WHY**: 시맨틱 검색 엔진. 기업 리서치, 경쟁사 분석, 업계 동향 수집에 사용. 키워드 매칭이 아닌 의미 기반 검색으로 더 관련성 높은 결과를 제공.

**HOW**:
1. https://exa.ai 접속
2. 회원가입 → Dashboard → API Keys
3. 무료 크레딧 제공 (월 1,000회)
4. 발급받은 키를 알려주세요

사용자가 키를 입력하면:
1. `~/.research-orchestrator.env`에 EXA_API_KEY 설정
2. MCP 서버 등록:
```bash
claude mcp add exa -e EXA_API_KEY=${EXA_API_KEY} -- npx -y exa-mcp-server
```
3. 검증 — Claude Code를 재시작해야 MCP 서버가 활성화됨을 안내

**SKIP**: 건너뛰면 시맨틱 검색 기능 사용 불가. Brave Search + WebSearch로 부분 대체 가능하나 기업 리서치 품질이 하락함.

---

## Step 5: MCP — Firecrawl (필수)

**WHY**: 자바스크립트 렌더링이 필요한 동적 웹페이지를 크롤링. 앱스토어, IR 페이지 등 SPA 사이트의 데이터 수집에 필수.

**HOW**:
1. https://firecrawl.dev 접속
2. 회원가입 → Dashboard → API Keys
3. 무료 플랜: 월 500 크레딧
4. 발급받은 키를 알려주세요

사용자가 키를 입력하면:
1. `~/.research-orchestrator.env`에 FIRECRAWL_API_KEY 설정
2. MCP 서버 등록:
```bash
claude mcp add firecrawl -e FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY} -- npx -y firecrawl-mcp
```

**SKIP**: 건너뛰면 JS 렌더링이 필요한 페이지 크롤링 불가. 정적 페이지만 접근 가능.

---

## Step 6: MCP — Brave Search (필수)

**WHY**: 범용 웹 검색 엔진. 뉴스, 기사, 블로그 등 광범위한 웹 소스 검색에 사용.

**HOW**:
1. https://brave.com/search/api/ 접속
2. "Get Started" → 회원가입
3. Free 플랜: 월 2,000 쿼리
4. 발급받은 키를 알려주세요

사용자가 키를 입력하면:
1. `~/.research-orchestrator.env`에 BRAVE_API_KEY 설정
2. MCP 서버 등록:
```bash
claude mcp add brave-search -e BRAVE_API_KEY=${BRAVE_API_KEY} -- npx -y @anthropic/brave-search-mcp
```

**SKIP**: 건너뛰면 Brave Search MCP 사용 불가. Claude 내장 WebSearch로 대체 가능하나 검색 결과 다양성이 감소.

---

## Step 7: MCP — Fetch (키 불필요, 자동)

**WHY**: 웹 페이지를 마크다운으로 변환하여 가져오는 범용 도구. API 키 불필요.

자동으로 설치:
```bash
claude mcp add fetch -- npx -y @anthropic/fetch-mcp
```

사용자에게 설치 완료를 알린다.

---

## Step 8: 도메인 프로파일 설정

**WHY**: Research Orchestrator는 도메인 독립적으로 설계되어 있다. 어떤 산업을 리서치할지 도메인 프로파일을 설정해야 에이전트가 산업 맥락을 이해한다.

AskUserQuestion 도구를 사용하여 사용자에게 도메인을 선택하게 한다:

| 옵션 | 설명 |
|------|------|
| **직접 입력** | 산업명 입력 (게임, 바이오, SaaS, 반도체 등) — 도메인 프로파일 스키마 기반으로 생성 |

### 도메인 설정 절차
1. 사용자에게 산업명을 입력받는다
2. `knowledge/domain-profile-schema.md`를 읽어 스키마를 확인한다
3. 해당 산업에 맞는 4개 파일의 초안을 `knowledge/domain/`에 생성한다
4. 사용자에게 검토/수정 요청

**SKIP**: 건너뛰면 도메인 프로파일 없이 진행. 에이전트가 산업 맥락을 이해하지 못해 리서치 품질이 저하됨.

---

## Step 8.5: 도메인 특화 API 리서치 및 추가

**WHY**: 도메인마다 유용한 공개 API가 다르다. Claude가 웹 리서치를 통해 해당 도메인에서 활용 가능한 무료/저비용 공개 API를 탐색하고, 프로젝트에 자동 통합한다.

### 실행 조건
- Step 8에서 도메인 프로파일이 설정된 경우에만 실행
- 도메인이 SKIP된 경우 이 단계도 SKIP

### 리서치 절차

1. **웹 리서치 실행**: WebSearch를 사용하여 해당 도메인의 공개 API를 탐색한다.
   - 검색 쿼리 예시:
     - `"{도메인} public API free data"`
     - `"{도메인} industry data API 2025 2026"`
     - `"{도메인} open data API developer"`
   - 최소 3~5개 검색 수행

2. **API 후보 선별 기준**:
   | 기준 | 필수/권장 | 설명 |
   |------|----------|------|
   | 무료 또는 Freemium | 필수 | 무료 tier가 있어야 함 |
   | REST API 또는 공개 데이터 | 필수 | 프로그래밍 방식으로 접근 가능 |
   | 리서치 관련성 | 필수 | 기업 분석/시장 분석에 실질적으로 유용 |
   | 문서화 수준 | 권장 | API 문서가 공개되어 있어야 함 |
   | 안정성 | 권장 | 공식 기관 또는 확립된 서비스 |

3. **발견한 API를 사용자에게 제시**: 테이블 형태로 정리
   ```
   | API | 제공자 | 무료 여부 | 주요 데이터 | 리서치 활용 |
   |-----|--------|----------|-----------|-----------|
   ```
   사용자가 추가할 API를 선택하게 한다 (multiSelect).

4. **선택된 API를 프로젝트에 통합**:
   - `knowledge/shared-rules.md` §8에 도메인 특화 API 섹션 추가 (엔드포인트, 인증 방식, 활용법)
   - `knowledge/domain/data-sources-domain.md`에 API 정보 기록
   - API Key가 필요한 경우 `~/.research-orchestrator.env`에 환경변수 템플릿 추가
   - `README.md`의 선택 API 테이블에 추가

5. **사용자에게 API Key 발급 안내**: 키가 필요한 API에 대해 발급 URL과 절차를 안내하고, 키 입력 시 env 파일에 설정

### 리서치 결과가 없는 경우
- "해당 도메인에서 리서치에 적합한 무료 공개 API를 찾지 못했습니다. 리서치 실행 중 새로운 소스를 발견하면 자동으로 추가합니다." 안내 후 다음 단계로 진행

---

## Step 9: Optional APIs

AskUserQuestion 도구를 사용하여 사용자에게 선택적 API 설정 여부를 묻는다.

선택 가능한 공통 API 목록:
| API | 용도 | 무료 여부 | 발급 URL |
|-----|------|----------|---------|
| **FRED API** | 미국 연방준비은행 경제 지표 (금리, GDP, CPI) | 무료 | https://fred.stlouisfed.org/docs/api/api_key.html |
| **ECOS API** | 한국은행 경제 통계 (환율, 금리) | 무료 | https://ecos.bok.or.kr/api/ |
| **NewsAPI** | 글로벌 뉴스 검색 (72,000+ 소스) | 무료(개발자) | https://newsapi.org/register |

도메인 특화 API:
> Step 8.5에서 리서치된 API가 여기 표시된다. `knowledge/domain/data-sources-domain.md` 참조.

사용자가 선택한 API에 대해서만 발급 안내 → 키 입력 → env 파일 업데이트를 진행한다.
건너뛰기를 선택하면 바로 Step 10으로 이동.

---

## Step 10: 최종 상태 요약

설정 완료 후 아래 형식의 상태 테이블을 출력한다:

```
## Research Orchestrator — 설정 완료

| 구분 | 항목 | 상태 | 비고 |
|------|------|------|------|
| 사전 요건 | Node.js | ✅ v{version} | |
| 사전 요건 | Python 3 | ✅ v{version} | |
| 의존성 | markdown 패키지 | ✅ | |
| 환경 | ~/.research-orchestrator.env | ✅ 생성됨 | |
| 환경 | ~/.zshrc 자동 로드 | ✅ 설정됨 | |
| 도메인 | 도메인 프로파일 | ✅ {산업명} / ⏭️ | knowledge/domain/ |
| 필수 API | DART Open API | ✅/⏭️ | |
| 필수 MCP | Exa | ✅/⏭️ | |
| 필수 MCP | Firecrawl | ✅/⏭️ | |
| 필수 MCP | Brave Search | ✅/⏭️ | |
| 필수 MCP | Fetch | ✅ 자동 설치 | 키 불필요 |
| 선택 API | FRED | ✅/⏭️/— | |
| 선택 API | ECOS | ✅/⏭️/— | |
| 선택 API | NewsAPI | ✅/⏭️/— | |
| 도메인 API | (Step 8.5 리서치 결과) | ✅/⏭️/— | 도메인별 상이 |
```

범례: ✅ 설정 완료 / ⏭️ 건너뜀 / — 미선택

**마무리 안내**:
- MCP 서버를 활성화하려면 Claude Code를 재시작하세요 (`/exit` → `claude`)
- 나중에 설정 상태를 확인하려면 `/setup-check` 를 실행하세요
- 리서치를 시작하려면: `research-pm` 에이전트에게 리서치 주제를 요청하세요
