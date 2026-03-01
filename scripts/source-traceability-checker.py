#!/usr/bin/env python3
"""
출처-데이터 추적성 검증기 (Source-Data Traceability Checker)

보고서의 [S##] 출처 태그가 실제 소스 파일의 데이터와 매칭되는지 검증.
"가짜 출처 태그" — 태그는 있지만 소스 파일에 해당 수치가 없는 경우 — 를 탐지.

사용법:
    python scripts/source-traceability-checker.py <보고서 파일> <소스 파일 디렉토리>
    python scripts/source-traceability-checker.py reports/netmarble-neo-strategy/08_5year_growth_strategy.md reports/netmarble-neo-strategy/

출력:
    stdout: JSON {total_claims, verified, unverified, details: [...]}
    종료 코드: 0=all verified, 1=unverified found, 2=error

EP-023: 출처-데이터 추적성 갭 방지
"""

import sys
import re
import json
from pathlib import Path


# ── 설정 ──

# 수치 추출 패턴: 보고서 라인에서 검증 대상 수치를 추출
NUMBER_PATTERNS = [
    # 한국어 금액: 1,210억, 468억 등
    re.compile(r'([\d,]+)\s*억'),
    # 범위 퍼센트: 68-73%, 85-90% 등 (단순 퍼센트보다 먼저 매칭해야 함)
    re.compile(r'(\d+(?:\.\d+)?\s*[–\-~]\s*\d+(?:\.\d+)?)\s*%'),
    # 퍼센트: 38.7%, +69% 등 (범위가 아닌 단일 퍼센트, 음수는 YoY 패턴에서 처리)
    re.compile(r'(?<!\d[–\-~])(\d+(?:\.\d+)?)\s*%'),
    # 달러: $27B, $70M, $3.2B
    re.compile(r'\$\s*([\d.]+)\s*[BMK]'),
    # 만 단위: 1,737만, 647명
    re.compile(r'([\d,]+)\s*만'),
    re.compile(r'([\d,]+)\s*명'),
    # CAGR 수치: CAGR 8.7%, CAGR 7-10%
    re.compile(r'CAGR\s*(\d+(?:\.\d+)?(?:\s*[–\-]\s*\d+(?:\.\d+)?)?)'),
    # YoY 수치: YoY +69%, YoY -11%
    re.compile(r'YoY\s*([+-]?\d+(?:\.\d+)?)'),
]

# 검증 제외 패턴 (이 패턴이 있는 라인은 검증 스킵)
SKIP_PATTERNS = [
    re.compile(r'^\s*#'),           # 헤딩
    re.compile(r'^\s*\|[\s\-:]+\|'), # 테이블 구분선
    re.compile(r'^\s*$'),           # 빈 줄
    re.compile(r'^\s*>.*작성일'),    # 메타 정보
    re.compile(r'^\s*>.*rev\.'),     # 버전 정보
]

# 수치 정규화: 쉼표 제거, 소수점 유지
def normalize_number(s):
    """수치 문자열 정규화 — 쉼표 제거"""
    return s.replace(",", "").strip()


def extract_source_map_from_report(lines):
    """보고서 부록의 출처 인덱스 테이블에서 S##/U## → 파일명 리스트 매핑 추출.

    복수 파일 지원: | S01 | a.md, b.md | 형태에서 모든 .md 파일을 리스트로 저장.
    [U##] 태그(사용자 제공 데이터)도 동일하게 처리.
    """
    source_map = {}
    in_source_index = False

    for line in lines:
        if '출처 인덱스' in line and '#' in line:
            in_source_index = True
            continue

        if in_source_index and line.strip().startswith('|'):
            # | S01 | file.md | 또는 | U01 | file.md | 형태 파싱
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]

            if len(cells) >= 2:
                sid_match = re.match(r'([SU])(\d+)', cells[0])
                if sid_match:
                    prefix = sid_match.group(1)
                    sid = f"{prefix}{sid_match.group(2).zfill(2)}"
                    # 파일명 추출: .md로 끝나는 모든 부분 찾기 (복수 파일 지원)
                    for cell in cells[1:]:
                        md_matches = re.findall(r'[\w\-]+\.md', cell)
                        if md_matches:
                            source_map[sid] = md_matches  # 리스트로 저장
                            break

        # 출처 인덱스 섹션 이후 다른 ## 헤딩이 나오면 종료
        if in_source_index and line.strip().startswith('## ') and '출처' not in line:
            break

    return source_map


def extract_claims(lines):
    """보고서에서 [S##] 또는 [U##] 태그가 있는 라인의 수치를 추출.

    멀티 소스 지원: [S01][S03] 또는 [S01][U01] 형태의 경우, 해당 라인의
    모든 소스 ID를 하나의 클레임에 묶어서 반환한다. 검증 시 어느 한 소스에라도
    수치가 있으면 해당 수치는 verified로 처리된다.
    [U##] 태그는 사용자 제공 데이터를 나타내며, [S##]과 동일하게 검증된다.
    """
    claims = []
    source_pattern = re.compile(r'\[([SU])(\d+)\]')
    in_code_block = False

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 제외 패턴 체크
        skip = False
        for sp in SKIP_PATTERNS:
            if sp.match(line):
                skip = True
                break
        if skip:
            continue

        # [S##] 또는 [U##] 태그 찾기
        source_matches = source_pattern.findall(line)
        if not source_matches:
            continue

        # 이 라인에서 수치 추출 (span 기반 중복 제거)
        numbers = []
        matched_spans = []  # 이미 매칭된 문자 위치 범위 추적
        for pattern in NUMBER_PATTERNS:
            for match in pattern.finditer(line):
                # 현재 매칭이 이전에 매칭된 범위와 겹치면 스킵 (범위 패턴 우선)
                span = match.span()
                overlap = False
                for prev_start, prev_end in matched_spans:
                    if span[0] < prev_end and span[1] > prev_start:
                        overlap = True
                        break
                if overlap:
                    continue
                matched_spans.append(span)
                num_str = normalize_number(match.group(1) if match.lastindex else match.group(0))
                numbers.append(num_str)

        if not numbers:
            continue

        # 소스 ID 목록을 정규화하여 하나의 클레임으로 묶음
        # source_matches는 [('S', '01'), ('U', '02')] 형태의 튜플 리스트
        unique_sids = sorted(set(f"{prefix}{sid_num.zfill(2)}" for prefix, sid_num in source_matches))
        claims.append({
            "line": i,
            "source_ids": unique_sids,
            "numbers": numbers,
            "text": line.strip()[:120],
        })

    return claims


def _number_exists_in_content(num, content):
    """수치가 소스 파일 콘텐츠에 word-boundary 기준으로 존재하는지 확인.

    매칭 전략:
    1. 정확 매칭 (exact): 원본 수치가 소스에 그대로 존재
    2. 쉼표 정규화: "1,210"과 "1210" 상호 매칭
    3. 범위 대시 정규화: "7–10"(en-dash)은 "7-10"(hyphen), "7~10"(물결표)과 매칭
    4. 소수점 정밀도: "38.7" → 정확 매칭 우선, "38"만으로는 매칭 불가 (false positive 방지)
    5. 단위 변환: "1210억" ↔ "12.1조", "1210억" ↔ "121,000만" 등
    6. word-boundary 매칭: "38"이 "381"에 잘못 매칭되지 않도록 방지
    """
    # 범위 패턴 처리: "7–10" → 대시/물결표 변형 모두 검색
    range_match = re.match(r'^(\d+(?:\.\d+)?)\s*[–\-~]\s*(\d+(?:\.\d+)?)$', num)
    if range_match:
        lo, hi = range_match.group(1), range_match.group(2)
        # 가능한 구분자: en-dash(–), hyphen(-), 물결표(~)
        for sep in ['–', '-', '~', '—']:
            # 구분자 양옆에 공백이 있을 수도 있음
            for spacing in ['', ' ', '\\s*']:
                if spacing == '\\s*':
                    pattern = rf'(?<![0-9,.]){re.escape(lo)}\s*[–\-~—]\s*{re.escape(hi)}(?![0-9,.])'
                    if re.search(pattern, content):
                        return True
                else:
                    variant = f"{lo}{spacing}{sep}{spacing}{hi}"
                    # word-boundary 검색
                    pattern = rf'(?<![0-9,.]){re.escape(variant)}(?![0-9,.])'
                    if re.search(pattern, content):
                        return True
        return False

    # 일반 수치에 대한 검색 변형 생성
    search_variants = [num]  # 원본: "1210"

    # 쉼표가 없는 정수 → 쉼표 추가 변형: "1210" → "1,210"
    if num.replace('.', '').isdigit() and '.' not in num:
        try:
            search_variants.append(f"{int(num):,}")
        except ValueError:
            pass

    # 쉼표가 있는 수 → 쉼표 제거 변형: "1,210" → "1210"
    if ',' in num:
        search_variants.append(num.replace(',', ''))

    # 소수점 있는 수치: 정확 매칭 우선 (false positive 방지)
    # "38.7"은 "38.7"로 매칭해야지, "38"만으로 매칭하면 안 됨
    # 단, 소스에 "38.7"이 없고 "38.7%"가 있을 수 있으므로 원본 매칭은 유지
    # 정수부만 매칭은 제거 — "38.7" → "38"은 false positive 위험

    # 한국어 금액 단위 변환 매칭
    # "1210" (억 맥락) → 소스에 "12.1조" 또는 "121,000만" 등으로 있을 수 있음
    clean_num = num.replace(',', '')
    if clean_num.replace('.', '').isdigit():
        try:
            val = float(clean_num)
            # 억 → 조 변환: 10000억 = 1조, 1210억 = 1.21조 → "1.21"+"조" 검색
            if val >= 100:  # 100억 이상일 때 조 단위 변환 시도
                jo_val = val / 10000
                if jo_val >= 0.1:
                    jo_str = f"{jo_val:.1f}".rstrip('0').rstrip('.')
                    search_variants.append(jo_str)  # "1.21" 등
            # 억 → 만 변환: 1210억 = 121000만 → "121000"+"만" 검색
            if val == int(val):
                man_val = int(val) * 10000
                search_variants.append(str(man_val))
                search_variants.append(f"{man_val:,}")
        except (ValueError, OverflowError):
            pass

    # 중복 제거
    search_variants = list(dict.fromkeys(search_variants))

    for variant in search_variants:
        # word-boundary 매칭: 숫자/콤마/소수점으로 둘러싸이지 않은 경우만 매칭
        # 예: "38.7"은 "38.7%"에 매칭되고, "38"은 "381"에 매칭되지 않음
        pattern = rf'(?<![0-9,.]){re.escape(variant)}(?![0-9,.])'
        if re.search(pattern, content):
            return True

    return False


def verify_claim_in_source(claim, source_file_path):
    """소스 파일에서 클레임의 수치가 존재하는지 확인"""
    if not source_file_path.exists():
        return {
            "status": "source_missing",
            "message": f"소스 파일 없음: {source_file_path.name}"
        }

    content = source_file_path.read_text(encoding='utf-8')

    found = []
    not_found = []

    for num in claim["numbers"]:
        if _number_exists_in_content(num, content):
            found.append(num)
        else:
            not_found.append(num)

    if not not_found:
        return {"status": "verified", "found": found}
    elif found:
        return {"status": "partial", "found": found, "not_found": not_found}
    else:
        return {"status": "unverified", "not_found": not_found}


def verify_claim_multi_source(claim, source_map, src_dir):
    """멀티 소스 검증: 클레임의 수치가 여러 소스 중 하나라도 존재하면 verified.

    [S01][S03] 형태의 멀티 소스 태그에서, 각 수치가 S01 또는 S03 중
    어느 한 쪽에라도 있으면 해당 수치를 found로 처리한다.
    """
    source_ids = claim["source_ids"]

    # 매핑되지 않은 소스 ID 확인
    unmapped_sids = [sid for sid in source_ids if sid not in source_map]
    mapped_sids = [sid for sid in source_ids if sid in source_map]

    if not mapped_sids:
        return {
            "status": "unmapped",
            "message": f"출처 ID {', '.join(unmapped_sids)}이 매핑에 없음",
            "source_files": [],
        }

    # 매핑된 소스 파일들의 콘텐츠를 모두 로드 (복수 파일 지원)
    source_contents = {}  # sid → 합산된 content
    source_files = {}     # sid → filename 리스트
    missing_sids = []

    for sid in mapped_sids:
        filenames = source_map[sid]
        # source_map 값이 리스트가 아닌 경우 호환성 처리
        if isinstance(filenames, str):
            filenames = [filenames]
        source_files[sid] = filenames
        combined_content = ""
        any_found = False
        for fname in filenames:
            source_file = src_dir / fname
            if source_file.exists():
                combined_content += source_file.read_text(encoding='utf-8') + "\n"
                any_found = True
        if any_found:
            source_contents[sid] = combined_content
        else:
            missing_sids.append(sid)

    if not source_contents:
        all_files = []
        for sid in mapped_sids:
            fnames = source_map[sid] if isinstance(source_map[sid], list) else [source_map[sid]]
            all_files.extend(fnames)
        return {
            "status": "source_missing",
            "message": f"소스 파일 없음: {', '.join(all_files)}",
            "source_files": all_files,
        }

    # 각 수치에 대해 어느 소스에서든 존재하는지 확인
    found = []
    not_found = []

    for num in claim["numbers"]:
        matched = False
        for sid, content in source_contents.items():
            if _number_exists_in_content(num, content):
                matched = True
                break
        if matched:
            found.append(num)
        else:
            not_found.append(num)

    # source_files 값을 평탄화 (리스트의 리스트 → 단일 리스트)
    flat_files = []
    for fnames in source_files.values():
        if isinstance(fnames, list):
            flat_files.extend(fnames)
        else:
            flat_files.append(fnames)
    result = {"source_files": list(set(flat_files))}

    if unmapped_sids:
        result["unmapped_sources"] = unmapped_sids
    if missing_sids:
        missing_files = []
        for sid in missing_sids:
            fnames = source_map[sid] if isinstance(source_map[sid], list) else [source_map[sid]]
            missing_files.extend(fnames)
        result["missing_sources"] = missing_files

    if not not_found:
        result["status"] = "verified"
        result["found"] = found
    elif found:
        result["status"] = "partial"
        result["found"] = found
        result["not_found"] = not_found
    else:
        result["status"] = "unverified"
        result["not_found"] = not_found

    return result


def run_traceability_check(report_path, source_dir):
    """전체 추적성 검증 실행"""
    report = Path(report_path)
    src_dir = Path(source_dir)

    if not report.exists():
        return {"error": f"보고서 파일 없음: {report_path}"}

    content = report.read_text(encoding='utf-8')
    lines = content.split('\n')

    # 1. 출처 인덱스 매핑 추출 (부록에서)
    source_map = extract_source_map_from_report(lines)
    if not source_map:
        # 부록 출처 인덱스 파싱 실패 시 에러 메시지 출력 후 종료
        return {
            "error": (
                "부록에서 출처 인덱스를 찾을 수 없습니다. "
                "보고서에 '## 부록: 출처 인덱스' 섹션이 있는지 확인하세요. "
                "형식: | S01 | filename.md | 설명 |"
            )
        }
    map_source = "appendix"

    # 2. 클레임 추출 (멀티 소스 태그를 하나의 클레임으로 묶음)
    claims = extract_claims(lines)

    # 3. 각 클레임 검증 (멀티 소스 통합 검증)
    results = []
    verified_count = 0
    unverified_count = 0
    partial_count = 0
    skipped_count = 0

    for claim in claims:
        verification = verify_claim_multi_source(claim, source_map, src_dir)

        results.append({
            **claim,
            "verification": verification,
        })

        if verification["status"] == "verified":
            verified_count += 1
        elif verification["status"] == "partial":
            partial_count += 1
        elif verification["status"] == "unverified":
            unverified_count += 1
        else:
            skipped_count += 1

    # 4. 결과 집계
    output = {
        "report": str(report_path),
        "source_directory": str(source_dir),
        "source_map_origin": map_source,
        "source_map": source_map,
        "summary": {
            "total_claims": len(claims),
            "verified": verified_count,
            "partial": partial_count,
            "unverified": unverified_count,
            "skipped": skipped_count,
        },
        "unverified_details": [
            r for r in results
            if r.get("verification", {}).get("status") in ("unverified", "partial", "unmapped", "source_missing")
        ],
    }

    return output


def main():
    if len(sys.argv) < 3:
        print("사용법: python scripts/source-traceability-checker.py <보고서 파일> <소스 파일 디렉토리>", file=sys.stderr)
        print("예시:   python scripts/source-traceability-checker.py reports/netmarble-neo-strategy/08_5year_growth_strategy.md reports/netmarble-neo-strategy/", file=sys.stderr)
        sys.exit(2)

    report_path = sys.argv[1]
    source_dir = sys.argv[2]

    result = run_traceability_check(report_path, source_dir)

    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(2)

    # JSON 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 결과 요약 stderr 출력
    s = result["summary"]
    print(f"\n=== 추적성 검증 요약 ===", file=sys.stderr)
    print(f"총 클레임: {s['total_claims']}건", file=sys.stderr)
    print(f"  검증됨(verified): {s['verified']}건", file=sys.stderr)
    print(f"  부분(partial): {s['partial']}건", file=sys.stderr)
    print(f"  미검증(unverified): {s['unverified']}건", file=sys.stderr)
    print(f"  스킵(skipped): {s['skipped']}건", file=sys.stderr)

    # partial/unverified 상세 출력
    if s["partial"] > 0 or s["unverified"] > 0:
        print(f"\n--- 미검증/부분검증 상세 ---", file=sys.stderr)
        for detail in result.get("unverified_details", []):
            v = detail.get("verification", {})
            status = v.get("status", "unknown")
            line = detail.get("line", "?")
            text = detail.get("text", "")[:80]
            not_found = v.get("not_found", [])
            source_files = v.get("source_files", [])
            print(f"  L{line} [{status}] {text}", file=sys.stderr)
            if not_found:
                print(f"    미매칭 수치: {', '.join(not_found)}", file=sys.stderr)
            if source_files:
                print(f"    검색 소스: {', '.join(source_files)}", file=sys.stderr)

    # 종료 코드
    sys.exit(0 if s["unverified"] == 0 and s["partial"] == 0 else 1)


if __name__ == "__main__":
    main()
