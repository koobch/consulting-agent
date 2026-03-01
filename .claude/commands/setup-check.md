# /setup-check — Research Orchestrator 설정 상태 진단

질문 없이 현재 설정 상태를 진단하고 테이블로 출력한다.

---

## 실행할 검증 항목

아래 명령어들을 실행하여 상태를 수집한다. 모든 검증을 한 번에 실행하고, 결과를 테이블로 정리한다.

### 1. 사전 요건
```bash
node --version 2>/dev/null || echo "NOT_INSTALLED"
python3 --version 2>/dev/null || echo "NOT_INSTALLED"
```

### 2. Python 의존성
```bash
python3 -c "import markdown; print(markdown.version)" 2>/dev/null || echo "NOT_INSTALLED"
```

### 3. 환경 파일
```bash
test -f ~/.research-orchestrator.env && echo "EXISTS" || echo "NOT_FOUND"
grep -q 'research-orchestrator.env' ~/.zshrc 2>/dev/null && echo "AUTOLOAD_OK" || echo "AUTOLOAD_MISSING"
```

### 4. 도메인 프로파일 확인
```bash
# 도메인 프로파일 파일 존재 여부 확인
for f in domain-profile.md industry-metrics.md product-lifecycle-models.md data-sources-domain.md; do
  test -f "knowledge/domain/$f" && echo "domain:$f=EXISTS" || echo "domain:$f=NOT_FOUND"
done

# 도메인명 추출 (domain-profile.md 첫 줄에서)
head -5 knowledge/domain/domain-profile.md 2>/dev/null | grep -o '도메인:.*' || echo "domain_name=UNKNOWN"
```

### 5. API 키 확인 (키 값 자체는 출력하지 않고, 설정 여부만 확인)
```bash
source ~/.research-orchestrator.env 2>/dev/null

# 필수
[ -n "$DART_API_KEY" ] && echo "DART_API_KEY=SET" || echo "DART_API_KEY=UNSET"
[ -n "$EXA_API_KEY" ] && echo "EXA_API_KEY=SET" || echo "EXA_API_KEY=UNSET"
[ -n "$FIRECRAWL_API_KEY" ] && echo "FIRECRAWL_API_KEY=SET" || echo "FIRECRAWL_API_KEY=UNSET"
[ -n "$BRAVE_API_KEY" ] && echo "BRAVE_API_KEY=SET" || echo "BRAVE_API_KEY=UNSET"

# 선택
[ -n "$STEAM_API_KEY" ] && echo "STEAM_API_KEY=SET" || echo "STEAM_API_KEY=UNSET"
[ -n "$FRED_API_KEY" ] && echo "FRED_API_KEY=SET" || echo "FRED_API_KEY=UNSET"
[ -n "$ECOS_API_KEY" ] && echo "ECOS_API_KEY=SET" || echo "ECOS_API_KEY=UNSET"
[ -n "$NEWSAPI_KEY" ] && echo "NEWSAPI_KEY=SET" || echo "NEWSAPI_KEY=UNSET"
[ -n "$IGDB_CLIENT_ID" ] && echo "IGDB_CLIENT_ID=SET" || echo "IGDB_CLIENT_ID=UNSET"
```

### 6. MCP 서버 확인
```bash
# Claude Code MCP 설정 파일 확인
cat ~/.claude/settings.json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    mcps = data.get('mcpServers', {})
    for name in ['exa', 'firecrawl', 'brave-search', 'fetch']:
        status = 'REGISTERED' if name in mcps else 'NOT_REGISTERED'
        print(f'{name}={status}')
except:
    print('MCP_CONFIG_ERROR')
" 2>/dev/null || echo "MCP_CONFIG_ERROR"
```

### 7. 프로젝트 레벨 MCP 확인
```bash
cat .claude/settings.json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    mcps = data.get('mcpServers', {})
    for name in ['exa', 'firecrawl', 'brave-search', 'fetch']:
        status = 'REGISTERED' if name in mcps else 'NOT_REGISTERED'
        print(f'project:{name}={status}')
except:
    pass
" 2>/dev/null
```

---

## 출력 형식

수집한 결과를 아래 형식으로 출력한다:

```
## Research Orchestrator — 설정 상태 진단

| 구분 | 항목 | 상태 | 비고 |
|------|------|------|------|
| 사전 요건 | Node.js | ✅ v22.x / ❌ 미설치 | MCP 서버 실행에 필요 |
| 사전 요건 | Python 3 | ✅ v3.x / ❌ 미설치 | 검증 스크립트에 필요 |
| 의존성 | markdown 패키지 | ✅ v3.x / ❌ 미설치 | `pip3 install -r requirements.txt` |
| 환경 | ~/.research-orchestrator.env | ✅ / ❌ | API 키 저장 파일 |
| 환경 | ~/.zshrc 자동 로드 | ✅ / ❌ | shell 시작 시 env 자동 로드 |
| 도메인 | 도메인 프로파일 | ✅ {산업명} / ❌ 미설정 | knowledge/domain/ |
| 도메인 | 파일 완전성 | ✅ 4/4 / ⚠️ N/4 | 4개 파일 필요 |
| 필수 API | DART Open API | ✅ 설정됨 / ❌ 미설정 | 한국 기업 공시 |
| 필수 MCP | Exa | ✅ 등록+키 / ⚠️ 등록만 / ❌ | 시맨틱 검색 |
| 필수 MCP | Firecrawl | ✅ 등록+키 / ⚠️ 등록만 / ❌ | 웹 크롤링 |
| 필수 MCP | Brave Search | ✅ 등록+키 / ⚠️ 등록만 / ❌ | 웹 검색 |
| 필수 MCP | Fetch | ✅ 등록됨 / ❌ | 키 불필요 |
| 선택 API | FRED | ✅ / — 미설정 | 미국 경제 지표 |
| 선택 API | ECOS | ✅ / — 미설정 | 한국 경제 통계 |
| 선택 API | NewsAPI | ✅ / — 미설정 | 뉴스 검색 |
| 도메인 API | Steam | ✅ / — 미설정 | 게임 도메인 |
| 도메인 API | IGDB | ✅ / — 미설정 | 게임 도메인 |
```

**미설정 항목이 있으면** 하단에 안내:
- 필수 항목 미설정: "`/setup` 을 실행하여 설정을 완료하세요."
- 선택 항목만 미설정: "선택 API는 미설정이어도 핵심 기능에 지장 없습니다."
