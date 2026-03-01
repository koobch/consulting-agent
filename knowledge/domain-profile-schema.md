# 도메인 프로파일 스키마 (Domain Profile Schema)

> **목적**: `/setup` 시 생성되는 `knowledge/domain/domain-profile.md`의 각 필드 정의와 도메인별 예시를 제공한다.
> **참조 에이전트**: 전체 — 모든 에이전트가 domain-profile.md를 해석할 때 이 스키마를 참조한다.

---

## 1. 스키마 정의

### 기본 정보

| 필드 | 설명 | 필수 |
|------|------|------|
| **도메인** | 리서치 대상 산업. 예: 게임, 바이오/제약, SaaS/핀테크, 반도체 | ✅ |
| **분석 대상 기업 유형** | 대상 기업의 일반적 분류. 예: 게임 개발사, CRO, B2B SaaS | ✅ |
| **제품/서비스 통칭** | 해당 산업에서 주요 산출물을 부르는 용어. 예: 게임/타이틀, 파이프라인 약물, 금융 상품 | ✅ |

### 제품/서비스 확인 소스

| 필드 | 설명 | 필수 |
|------|------|------|
| **공식 확인 채널** | 제품/서비스의 존재와 상태를 1차 소스에서 확인하는 경로 | ✅ |
| **확인 방법** | 각 채널에서 정보를 확인하는 구체적 절차 | ✅ |

### 수익 모델 분류

| 필드 | 설명 | 필수 |
|------|------|------|
| **모델 목록** | 해당 산업의 주요 수익화 방식 | ✅ |
| **수익 인식 특이사항** | 도메인별 매출 인식의 특이점 (회계 처리, 인식 시점 등) | 선택 |

### 핵심 성과 지표

| 필드 | 설명 | 필수 |
|------|------|------|
| **KPI** | 해당 산업에서 기업/제품 성과를 측정하는 핵심 지표 | ✅ |
| **벤치마크 범위** | 각 KPI의 건전 범위. 첫 리서치 후 자동 보완 | 선택 |

### 경쟁사 비교 축

| 필드 | 설명 | 필수 |
|------|------|------|
| **분류 기준** | 기업 간 비교 시 사용하는 주요 분류 축 | ✅ |

### 규제 기관 및 도메인 데이터 소스

| 필드 | 설명 | 필수 |
|------|------|------|
| **규제기관** | 해당 산업의 주요 규제/인허가 기관 | 선택 |
| **특화 데이터** | 도메인 전용 데이터베이스, 리서치 플랫폼 | 선택 |

### 도메인 특화 주의사항

| 필드 | 설명 | 필수 |
|------|------|------|
| **귀속 혼동 패턴** | 해당 산업에서 자주 발생하는 귀속/주체 혼동 | 선택 |
| **지표 함정** | 수치 해석 시 주의해야 할 도메인 특화 함정 | 선택 |

---

## 2. 도메인별 예시

### 예시 1: 게임 산업

```markdown
# 도메인 프로파일

## 기본 정보
- 도메인: 게임 산업
- 분석 대상 기업 유형: 게임 개발사
- 제품/서비스 통칭: 게임 (타이틀)

## 제품/서비스 확인 소스
- 공식 확인 채널: App Store, Google Play, Steam, PlayStation Store, Xbox Store, Nintendo eShop
- 확인 방법: 각 스토어 페이지에서 게임명 검색 → 지원 플랫폼, 가격, 출시일 직접 확인

## 수익 모델 분류
- 모델 목록: F2P (Free-to-Play, IAP 기반), B2P (Buy-to-Play, 패키지 판매), B2P+DLC, GaaS (Games-as-a-Service, 시즌 패스/배틀패스), 구독 (Game Pass 등)
- 수익 인식 특이사항: 퍼블리셔-개발사 배분 구조 (스토어 매출 ≠ 개발사 매출). F2P는 지속형 매출, B2P는 Front-loaded 매출 커브

## 핵심 성과 지표
- KPI: DAU, MAU, ARPU, ARPPU, 리텐션(D1/D7/D30), 과금율, LTV, CPI, ROAS
- 벤치마크 범위: DAU/MAU 점착도 20-50%, D1 리텐션 35-45%, ARPU $0.5-3/월 (모바일)

## 경쟁사 비교 축
- 분류 기준: 장르 (RPG/전략/캐주얼/FPS), 플랫폼 (모바일/PC/콘솔), 수익화 모델 (F2P/B2P), IP 유형 (자체/라이선스)

## 규제 기관 및 도메인 데이터 소스
- 규제기관: 게임물관리위원회 (한국), ESRB (미국), PEGI (유럽), CERO (일본)
- 특화 데이터: SteamDB, Sensor Tower, data.ai, Newzoo, AppMagic, VGChartz

## 도메인 특화 주의사항
- 귀속 혼동 패턴: 퍼블리셔 ≠ 개발사 (스토어 표기는 퍼블리셔 기준, 실제 개발사 별도 확인 필요)
- 지표 함정: 스토어 매출(Gross) ≠ 개발사 인식 매출(Net). B2P 첫 주 매출을 연간화하면 과대 추정
```

### 예시 2: 바이오/제약

```markdown
# 도메인 프로파일

## 기본 정보
- 도메인: 바이오/제약
- 분석 대상 기업 유형: 제약사, 바이오텍, CRO (위탁연구기관)
- 제품/서비스 통칭: 파이프라인 (신약 후보물질), 의약품

## 제품/서비스 확인 소스
- 공식 확인 채널: ClinicalTrials.gov, FDA Orange Book, EMA 의약품 DB, MFDS (식약처) 의약품 통합정보시스템
- 확인 방법: ClinicalTrials.gov에서 기업명 검색 → 임상 단계(Phase I/II/III), 적응증, 진행 상태 확인. FDA Orange Book에서 승인 의약품 목록 확인

## 수익 모델 분류
- 모델 목록: 의약품 판매 (처방약/OTC), 기술이전 (License-out, Milestone + Royalty), 위탁생산 (CDMO), 위탁연구 (CRO 서비스), 바이오시밀러
- 수익 인식 특이사항: 기술이전 계약금(Upfront) vs 마일스톤(Milestone) vs 로열티(Royalty) 분리 인식. 임상 실패 시 파이프라인 가치 급감. 특허 만료(Patent Cliff) → 제네릭 진입으로 매출 급감

## 핵심 성과 지표
- KPI: 파이프라인 개수 (단계별), 임상 성공률 (Phase별), FDA 승인율, 매출 상위 약물(Blockbuster) 비중, R&D 비용/매출 비율, 특허 잔여 기간
- 벤치마크 범위: Phase I→II 성공률 약 52%, Phase II→III 약 29%, Phase III→승인 약 58% (전체 IND→승인 약 7-11%)

## 경쟁사 비교 축
- 분류 기준: 치료영역 (Therapeutic Area: 종양/면역/CNS/대사), 개발단계 (전임상/Phase I-III/시판), 기술 플랫폼 (항체/세포치료/유전자치료/저분자), 파이프라인 깊이(Depth)와 폭(Breadth)

## 규제 기관 및 도메인 데이터 소스
- 규제기관: FDA (미국), EMA (유럽), MFDS/식약처 (한국), PMDA (일본)
- 특화 데이터: PubMed, DrugBank, Cortellis, Evaluate Pharma, GlobalData, BioMedTracker

## 도메인 특화 주의사항
- 귀속 혼동 패턴: CRO(위탁연구) ≠ 스폰서(의뢰사). 기술이전 계약에서 Licensor ≠ Licensee
- 지표 함정: rNPV(위험보정 순현재가치)와 DCF 혼동. 임상 Phase별 할인율 미적용. "Phase III 진입"이 승인을 보장하지 않음
```

### 예시 3: SaaS / 핀테크

```markdown
# 도메인 프로파일

## 기본 정보
- 도메인: SaaS / 핀테크
- 분석 대상 기업 유형: B2B SaaS, B2C 핀테크, 네오뱅크, 결제 플랫폼
- 제품/서비스 통칭: SaaS 제품, 금융 서비스/상품

## 제품/서비스 확인 소스
- 공식 확인 채널: 기업 공식 사이트 (Products 페이지), G2/Capterra (B2B SaaS 리뷰), App Store/Google Play (B2C), Crunchbase (기업 정보)
- 확인 방법: 공식 사이트에서 가격 플랜 확인 (Free/Starter/Enterprise). G2에서 경쟁 제품 포지셔닝 확인

## 수익 모델 분류
- 모델 목록: 구독(Subscription, MRR/ARR), 거래 수수료(Transaction Fee), 이자 수익(Net Interest Income), 프리미엄(Freemium), 사용량 기반(Usage-based), 라이선스(Perpetual License)
- 수익 인식 특이사항: ARR vs Revenue(GAAP) 차이. Deferred Revenue(선수수익) 처리. 거래량 기반 매출은 계절성 영향

## 핵심 성과 지표
- KPI: ARR, MRR, NRR(Net Revenue Retention), GRR(Gross Revenue Retention), CAC, LTV, CAC Payback Period, Rule of 40 (성장률+이익률), Magic Number
- 벤치마크 범위: NRR 110-130%(우수), GRR 85-95%(건전), CAC Payback 12-18개월, Rule of 40 > 40%

## 경쟁사 비교 축
- 분류 기준: 고객군 (SMB/Mid-Market/Enterprise), 기능 영역 (CRM/ERP/HR/결제/대출), 배포 방식 (Cloud-native/Hybrid/On-prem), 가격 모델 (Per-seat/Usage/Flat)

## 규제 기관 및 도메인 데이터 소스
- 규제기관: 금융감독원 (한국), SEC/OCC/CFPB (미국), FCA (영국), BaFin (독일)
- 특화 데이터: PitchBook, CB Insights, SaaStr Benchmarks, Bessemer Cloud Index, KeyBanc SaaS Survey

## 도메인 특화 주의사항
- 귀속 혼동 패턴: Platform vs Product (마켓플레이스의 GMV ≠ 자사 매출). 결제 대행사(PG)의 거래액 ≠ 매출
- 지표 함정: ARR ≠ GAAP Revenue. Bookings ≠ Revenue. Non-GAAP 이익률로 과대 표시 주의
```

### 예시 4: 제조업 / 반도체

```markdown
# 도메인 프로파일

## 기본 정보
- 도메인: 제조업 / 반도체
- 분석 대상 기업 유형: 팹리스(Fabless), 파운드리(Foundry), IDM(Integrated Device Manufacturer), 장비/소재
- 제품/서비스 통칭: 반도체 칩, 모듈, 장비

## 제품/서비스 확인 소스
- 공식 확인 채널: 기업 Product Portfolio 페이지, Distributor 사이트 (Digi-Key/Mouser/Arrow), 기술 Datasheet
- 확인 방법: 공식 사이트에서 제품 라인업 확인. 기술 노드(nm), 패키징, 주요 고객사 파악

## 수익 모델 분류
- 모델 목록: 제품 판매(칩/모듈), 파운드리 위탁생산(Wafer Revenue), IP 라이선스(ARM 모델), 설계 서비스(ASIC Design Service), 유지보수/기술지원
- 수익 인식 특이사항: 반도체 사이클(호황/불황) 영향 큼. 장기 공급 계약(LTA) vs 스팟 가격 차이. 재고 평가(FIFO/가중평균) 영향

## 핵심 성과 지표
- KPI: 매출 성장률, Gross Margin, 가동률(Utilization), 웨이퍼 출하량, ASP(Average Selling Price), Design Win 수, 기술 노드 전환율, R&D 투자율
- 벤치마크 범위: 팹리스 Gross Margin 50-65%, 파운드리 45-55%, IDM 40-55%, R&D/Revenue 15-25%

## 경쟁사 비교 축
- 분류 기준: 제품 유형(로직/메모리/아날로그/전력), 기술 노드(선단/성숙), 고객 산업(모바일/서버/자동차/IoT), 사업 모델(팹리스/파운드리/IDM)

## 규제 기관 및 도메인 데이터 소스
- 규제기관: 산업통상자원부 (한국), BIS/CHIPS Act (미국), 경제산업성 (일본)
- 특화 데이터: IC Insights, WSTS, TrendForce, Gartner Semiconductor, SEMI

## 도메인 특화 주의사항
- 귀속 혼동 패턴: 설계 주체(팹리스) ≠ 생산 주체(파운드리). 모듈 업체 ≠ 칩 설계사. 수탁생산 매출 ≠ 자사 제품 매출
- 지표 함정: 웨이퍼 출하량 증가 ≠ 매출 성장(ASP 하락 가능). 가동률이 높아도 수율(Yield)이 낮으면 실질 매출 감소. 환율 변동이 수출 비중 높은 기업에 큰 영향
```

---

## 3. 에이전트 활용 가이드

| 에이전트 | domain-profile 활용 방법 |
|---------|------------------------|
| **data-researcher** | "제품/서비스 확인 소스"를 Ground Truth 프로토콜의 1차 확인 채널로 사용 |
| **hypothesis-builder** | "핵심 성과 지표"와 "경쟁사 비교 축"을 가설 수립의 차원으로 활용 |
| **framework-designer** | "경쟁사 비교 축"을 MECE 분해의 1차 분류 기준으로 사용 |
| **financial-analyst** | "수익 모델 분류"와 "수익 인식 특이사항"을 재무 분석의 전제로 사용 |
| **fact-checker** | "귀속 혼동 패턴"과 "지표 함정"을 Level 0 검증의 도메인 특화 체크리스트로 사용 |
| **insight-synthesizer** | "핵심 성과 지표"로 전략 제안의 KPI를 설정. "지표 함정"으로 분석 오류 방지 |
| **report-writer** | "제품/서비스 통칭"으로 용어 통일. "수익 모델 분류"로 보고서 내 수익 구조 설명 |
| **valuation-analyst** | "수익 모델 분류"와 "핵심 성과 지표"로 밸류에이션 드라이버 설정 |

### domain-profile 파일 없을 때의 동작

에이전트가 `knowledge/domain/domain-profile.md`를 읽으려 했으나 파일이 없는 경우:
1. 사용자에게 `/setup` 실행을 권고
2. 급한 경우 범용 기본값으로 진행 가능 (단, "도메인 프로파일 미설정 — 범용 기준 적용" 명시)
3. 리서치 중 도메인 정보가 축적되면 자동으로 domain-profile.md 생성 제안

---

## 4. 도메인 지식 축적 흐름

```
/setup 실행 → domain-profile.md 생성 (기본 정보만)
     ↓
첫 리서치 Phase 0.5 (팩트시트)
     ↓
data-researcher/financial-analyst가 벤치마크 발견
     ↓
domain/industry-metrics.md에 기록
     ↓
리서치 완료 후 research-pm이 domain knowledge harvest
     ↓
domain/product-lifecycle-models.md에 수익/라이프사이클 패턴 기록
     ↓
다음 리서치에서 축적된 도메인 지식 재사용
```

> **갱신 주기**: 매 리서치 완료 후 research-pm이 domain knowledge harvest 실행. 새로운 벤치마크, 패턴, 데이터 소스가 발견되면 해당 파일에 추가.
