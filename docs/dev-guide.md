# 개발 가이드 — Claude Code + Codex CLI 이중 도구 운용

## 도구 역할 분리

```
┌─────────────────────────────────────────────────┐
│              research-orchestrator               │
├────────────────────┬────────────────────────────┤
│   시스템 개발       │   리서치 실행               │
│   (Codex CLI)      │   (Claude Code)             │
│                    │                             │
│ • 스크립트 개발     │ • 에이전트 오케스트레이션    │
│ • 에이전트 규칙 수정 │ • 웹 검색 / API 호출        │
│ • knowledge 업데이트│ • 데이터 수집 / 팩트체크     │
│ • 템플릿 정비       │ • 인사이트 도출             │
│ • 리팩토링 / SSOT   │ • 보고서 작성               │
│ • 검증 스크립트     │ • 품질 검증 판단            │
│                    │ • MCP 도구 (Exa, Firecrawl) │
├────────────────────┴────────────────────────────┤
│   공유 대상자: Claude Code만 사용                 │
│   (Codex 설치/설정 불필요)                        │
└─────────────────────────────────────────────────┘
```

## 언제 Codex를 쓰는가

### Codex 사용 (시스템 개발)
- "validator에 새 검증 규칙 추가해"
- "에이전트 프롬프트에 EP-026 규칙 넣어"
- "report-to-html.py에 다크모드 추가해"
- "shared-rules.md에 새 API 스펙 등록해"
- "SSOT 중복 정리해"
- "보고서에서 [S01]을 [S001]로 일괄 교체해"

### Claude Code 사용 (리서치 실행)
- "{대상 기업} 전략 리서치 시작해"
- "{주제} 전략 분석해"
- "이 데이터 팩트체크해"
- "인사이트 도출해"
- "보고서 초안 써"
- "이 보고서 품질 검증해서 수정해"

### 판단 기준
> **"이 작업에 인터넷 접근이나 전략적 판단이 필요한가?"**
> - Yes → Claude Code
> - No → Codex (또는 Claude Code)

## Codex CLI 사용법

```bash
# 프로젝트 디렉토리에서 실행
cd ~/research-orchestrator

# 기본 실행 (suggest 모드 — 변경 전 확인)
codex "mechanical-validator.py에 테이블 셀 내 줄바꿈 검증 규칙 추가해"

# auto-edit 모드 (자동 편집, 실행 전 확인)
codex --approval-mode auto-edit "shared-rules.md에 FRED API 스펙 추가해"

# full-auto 모드 (완전 자동 — 신뢰하는 작업에만)
codex --approval-mode full-auto "output 내 모든 보고서에서 ~를 –로 일괄 교체해"
```

## 공유 대상자용 안내

이 시스템을 공유받은 사용자는 **Claude Code만 필요**합니다.

### 필요 조건
1. Claude Code CLI 설치
2. Anthropic API Key (또는 Claude Max 구독)
3. MCP 서버 설정 (Exa, Firecrawl, Brave Search)

### 불필요
- Codex CLI
- OpenAI API Key
- AGENTS.md (Codex 전용 — 있어도 무해)

### 시작 방법
```bash
cd ~/research-orchestrator
claude
# → "A사 전략 리서치 시작해" 등으로 리서치 실행
```

## 개발 워크플로우 예시

### 1. 새 EP 규칙 추가 (Codex)
```bash
codex "EP-026 '시장 규모 출처 2개 필수' 규칙을 추가해.
self-improvement-log.md에 기록하고,
data-researcher.md와 fact-checker.md에 검증 로직 반영해."
```

### 2. 검증 스크립트 기능 추가 (Codex)
```bash
codex "mechanical-validator.py에 '동일 보고서 내 수치 불일치' 검증 추가해.
같은 데이터 포인트가 다른 섹션에서 다른 값으로 나오면 error."
```

### 3. 리서치 실행 (Claude Code)
```bash
claude
# → research-pm 에이전트가 워크플로우 오케스트레이션
```

### 4. 리서치 후 시스템 개선 (Codex)
```bash
# 리서치 중 발견된 문제를 시스템에 반영
codex "리서치에서 발견된 문제: 타임라인이 줄글로 나옴.
report-writer.md에 '타임라인은 반드시 테이블' 규칙 추가해."
```
