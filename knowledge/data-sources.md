# 데이터 소스 가이드

> 도메인 특화 데이터 소스는 `knowledge/domain/data-sources-domain.md`를 참조하세요.

## 기업 재무 데이터
| 소스 | 접근성 | 주요 데이터 |
|------|--------|-----------|
| DART (한국 공시) | 무료 | 사업보고서, 분기보고서, 감사보고서 |
| KIND (한국거래소) | 무료 | 공시, 기업 개요 |
| 네이버 금융 | 무료 | 주가, 재무제표, 투자 지표 |
| Yahoo Finance | 무료 | 글로벌 주가, 재무제표 |
| SEC EDGAR (미국 공시) | 무료 | 10-K, 10-Q, 8-K |
| TDnet (일본 공시) | 무료 | 결산 자료, 적시 공시 |

## API 기반 데이터 소스 (shared-rules.md §8 상세 참조)
| 소스 | 유형 | 접근성 | 주요 데이터 | 우선순위 |
|------|------|--------|-----------|---------|
| FRED API | 매크로 경제 | 무료 (Key 필요) | 미국 GDP, CPI, 환율, 소비지출 | 매크로 분석 시 |
| 한국은행 ECOS API | 매크로 경제 | 무료 (Key 필요) | 한국 GDP, CPI, 환율, 가계소비 | 한국 매크로 분석 시 |
| Google Trends | 검색 트렌드 | 무료 (pytrends) | 상대적 검색 관심도, 지역별 인기도 | 시장 관심도 비교 |
| EDINET API | 일본 공시 | 무료 (Key 선택적) | 유가증권보고서, 세그먼트 실적 | 일본 기업 심화 분석 시 |
| NewsAPI | 글로벌 뉴스 | 무료 (100건/일) | 뉴스 검색, 이벤트 탐지 | 최신 동향 수집 보조 |

## 범용 시장 데이터
| 소스 | 접근성 | 주요 데이터 |
|------|--------|-----------|
| Statista | 유료 (일부 공개) | 범용 산업 통계, 시장 규모, 전망 |
| 한국은행 경제 통계 | 무료 | 국내 GDP, 물가, 금리, 산업별 생산지수 |
| World Bank Open Data | 무료 | 글로벌 GDP, 인구, 산업 지표, 국가별 비교 |

## 전문가 의견 및 분석
| 소스 | 접근성 | 주요 데이터 |
|------|--------|-----------|
| LinkedIn | 무료 (로그인 필요) | 업계 전문가 게시글, 분석 |
| X (Twitter) | 무료 | 업계 인사이더, 빠른 뉴스 |
| Substack | 무료/유료 | 전문가 뉴스레터 |

## 뉴스 및 미디어
| 소스 | 접근성 | 주요 데이터 |
|------|--------|-----------|
| Bloomberg | 유료 (일부 무료) | 기업/산업 뉴스, 재무 분석 |
| Reuters | 유료 (일부 무료) | 기업/산업 뉴스, 글로벌 이슈 |

## 검색 팁

### 시장 규모 데이터
```
"[산업명] market size 2025 2026"
"[산업명] 시장 규모"
"[산업명] market report" filetype:pdf
"[키워드]" site:statista.com OR site:worldbank.org
```

### 기업 재무 데이터
```
"[회사명] 사업보고서 2025" site:dart.fss.or.kr
"[회사명] earnings Q4 2025"
"[회사명] IR presentation" filetype:pdf
"[회사명] annual report 2025"
```

### 전문가 의견
```
"[주제]" site:linkedin.com/pulse
"[주제]" site:substack.com
"[주제] analysis" site:medium.com
"[주제]" from:[전문가핸들] site:x.com
```

### 제품/기업 반응
```
"[제품명/기업명]" site:reddit.com
"[제품명/기업명] review"
"[기업명] 평가" site:blind.com OR site:glassdoor.com
```
