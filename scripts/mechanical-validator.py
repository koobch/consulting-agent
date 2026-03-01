#!/usr/bin/env python3
"""
보고서 기계적 검증 스크립트 (Mechanical Validator)

마크다운 보고서에 대해 정규식/산술 기반 기계 검증 14개 항목을 수행.
이슈 발견 시 JSON으로 출력하고 종료 코드 1을 반환.

사용법:
    python scripts/mechanical-validator.py <마크다운 파일 경로>
    python scripts/mechanical-validator.py reports/netmarble-neo-strategy/08_5year_growth_strategy.md

출력:
    stdout: JSON {total_issues, by_severity, issues: [{line, issue_type, severity, description}]}
    종료 코드: 0=clean, 1=issues found, 2=error
"""

import sys
import re
import json
from pathlib import Path


# ── 설정 ──

# 검증 3: 비표준 문자 금지 목록
BANNED_CHARS = [
    "❌", "🔴", "🟡", "🟢", "🔵", "⭐", "🏆", "🎯", "🚀", "💡", "🔑",
    "📊", "📈", "📉", "🎮", "💰", "🤖", "🎲", "👉", "👆", "👇",
    "✨", "💪", "🏅", "🥇", "🥈", "🥉", "💎",
]

# 검증 7: 내부 용어 금지 목록
INTERNAL_TERMS = [
    "사용자",         # → "경영진", "독자", 또는 구체적 대상으로 변경
    "도전적 시나리오",  # → "공격적 시나리오", "상한 시나리오"
    "보수적 시나리오",  # 맥락에 따라 허용 가능하지만 경고
    "에이전트",       # 리서치 시스템 내부 용어
    "팩트시트",       # 내부 프로세스 용어 (보고서에 노출 부적절)
    "디스커션",       # 내부 프로세스 용어
    "품질 게이트",     # 내부 프로세스 용어
    "에스컬레이션",    # 내부 프로세스 용어 (보고서에서는 "보고" 등으로)
]

# 검증 7에서 허용하는 맥락 (이 패턴 안에 있으면 무시)
INTERNAL_TERMS_WHITELIST_CONTEXTS = [
    r">\s*\*\*",     # 인용 블록 내 볼드 텍스트 (메타 정보)
    r"^>",           # 인용 블록
    r"<!--",         # HTML 주석
]


def validate_ep_references(lines):
    """검증 1: EP-xxx 참조 잔여"""
    issues = []
    # EP-xxx 패턴: EP 다음에 하이픈, 3자리 숫자
    pattern = re.compile(r'EP-\d{3}')
    for i, line in enumerate(lines, 1):
        # 인용 블록(>) 내부의 EP 참조도 포함
        # 단, 주석(<!--)이나 코드 블록(```) 내부는 제외
        matches = pattern.findall(line)
        if matches:
            for match in matches:
                issues.append({
                    "line": i,
                    "issue_type": "ep_reference",
                    "severity": "error",
                    "description": f"내부 EP 참조 잔여: {match}. 최종 보고서에는 EP 코드가 노출되면 안 됩니다."
                })
    return issues


def validate_strikethrough(lines):
    """검증 2: 취소선 잔존"""
    issues = []
    pattern = re.compile(r'~~.+?~~')
    for i, line in enumerate(lines, 1):
        matches = pattern.findall(line)
        if matches:
            for match in matches:
                issues.append({
                    "line": i,
                    "issue_type": "strikethrough",
                    "severity": "error",
                    "description": f"취소선 잔존: '{match}'. 최종 보고서에 취소선은 부적합합니다."
                })
    return issues


def validate_banned_chars(lines):
    """검증 3: 비표준 문자 (이모지 등)"""
    issues = []
    # 허용 이모지: ⚠️(주의 표기), ■□(불릿), ★☆(별점), ●(타임라인)
    # 코드 블록 내부는 제외
    in_code_block = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for char in BANNED_CHARS:
            if char in line:
                issues.append({
                    "line": i,
                    "issue_type": "banned_char",
                    "severity": "warning",
                    "description": f"비표준 문자 발견: '{char}'. 보고서에서 이모지 사용은 지양합니다."
                })
    return issues


def validate_table_arithmetic(lines):
    """검증 4: 테이블 산술 (합계행 역산 검증)"""
    issues = []
    tables = _extract_tables(lines)

    for table in tables:
        header_line, header, rows = table["header_line"], table["header"], table["rows"]

        # 숫자 열(column) 식별
        numeric_cols = _identify_numeric_columns(header, rows)

        # 합계 행 찾기
        for row_info in rows:
            row_line, row = row_info["line"], row_info["cells"]
            first_cell = row[0].strip().replace("**", "").strip()
            if first_cell in ["합계", "합 계", "소계", "총계", "Total", "TOTAL", "Sum"]:
                # 이 행의 각 숫자 열에 대해 합산 검증
                for col_idx in numeric_cols:
                    if col_idx >= len(row):
                        continue
                    expected_sum = 0
                    has_values = False
                    for data_row in rows:
                        if data_row == row_info:
                            continue
                        if col_idx >= len(data_row["cells"]):
                            continue
                        val = _parse_number(data_row["cells"][col_idx])
                        if val is not None:
                            expected_sum += val
                            has_values = True

                    if not has_values:
                        continue

                    actual_sum = _parse_number(row[col_idx])
                    if actual_sum is not None and abs(actual_sum - expected_sum) > 0.5:
                        col_name = header[col_idx].strip() if col_idx < len(header) else f"열{col_idx}"
                        issues.append({
                            "line": row_line,
                            "issue_type": "table_arithmetic",
                            "severity": "error",
                            "description": f"테이블 합계 불일치 (열: {col_name}): 기재값={actual_sum}, 계산값={expected_sum}"
                        })
    return issues


def validate_cross_reference_consistency(lines):
    """검증 5: CAGR 등 교차참조 일관성 — 동일 대상에 대해 다른 수치가 기재된 경우"""
    issues = []
    # CAGR 수치 수집
    cagr_pattern = re.compile(r'CAGR\s*[:\s]*(\d+(?:\.\d+)?)\s*%')
    cagr_values = {}  # {수치: [line numbers]}

    for i, line in enumerate(lines, 1):
        matches = cagr_pattern.finditer(line)
        for m in matches:
            val = m.group(1)
            cagr_values.setdefault(val, []).append(i)

    # "목표 CAGR"이라는 맥락에서 다른 값이 있으면 이슈
    target_cagr_pattern = re.compile(r'목표\s*CAGR[^0-9]*(\d+(?:\.\d+)?)\s*%')
    target_values = set()
    for i, line in enumerate(lines, 1):
        m = target_cagr_pattern.search(line)
        if m:
            target_values.add(m.group(1))

    if len(target_values) > 1:
        issues.append({
            "line": 0,
            "issue_type": "cross_reference",
            "severity": "error",
            "description": f"목표 CAGR 수치 불일치: {', '.join(target_values)}% — 보고서 전체에서 동일 대상에 다른 수치가 사용됨"
        })

    # 기준 매출 교차 확인
    base_revenue_pattern = re.compile(r'(?:기준\s*매출|2024.*매출)[^0-9]*([0-9,]+)\s*억')
    base_values = set()
    for i, line in enumerate(lines, 1):
        m = base_revenue_pattern.search(line)
        if m:
            val = m.group(1).replace(",", "")
            base_values.add(val)

    if len(base_values) > 1:
        issues.append({
            "line": 0,
            "issue_type": "cross_reference",
            "severity": "error",
            "description": f"기준 매출 수치 불일치: {', '.join(base_values)}억원 — 보고서 내에서 다른 기준 매출이 사용됨"
        })

    return issues


def validate_entity_labels(lines):
    """검증 6: 엔터티 라벨 누락 — 억원 근처에 [별도]/[그룹] 유무"""
    issues = []
    # "N억원" 또는 "N억 원" 패턴에서 근처에 [별도]/[그룹]/[네오 별도] 등이 없으면 경고
    revenue_pattern = re.compile(r'(\d{2,})\s*억\s*원?')
    label_pattern = re.compile(r'\[(별도|그룹|네오\s*별도|OFS|CFS)\]')

    in_code_block = False
    # 테이블 범위 감지: 현재 행이 테이블 내부인 경우 테이블 시작~끝까지 컨텍스트 확장
    table_ranges = _get_table_ranges(lines)

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if revenue_pattern.search(line):
            # 테이블 내부인 경우: 테이블 전체 + 테이블 위 10행까지를 컨텍스트로 확장
            table_context = _get_table_context_for_line(i - 1, table_ranges)
            if table_context:
                context_start = max(0, table_context[0] - 10)
                context_end = min(len(lines), table_context[1] + 1)
            else:
                # 테이블 밖: 섹션 헤딩까지 거슬러 올라감 (최대 30행)
                context_start = max(0, i - 31)
                # 가장 가까운 ## 헤딩 찾기
                for k in range(i - 2, max(0, i - 31) - 1, -1):
                    if lines[k].strip().startswith('#'):
                        context_start = k
                        break
                context_end = min(len(lines), i + 5)

            context = "\n".join(lines[context_start:context_end])

            if not label_pattern.search(context):
                matches = revenue_pattern.finditer(line)
                for m in matches:
                    val = int(m.group(1))
                    # 50억 이상인 경우만 체크 (소규모 금액은 맥락이 명확할 수 있음)
                    if val >= 50:
                        issues.append({
                            "line": i,
                            "issue_type": "entity_label_missing",
                            "severity": "warning",
                            "description": f"엔터티 라벨 누락 가능: '{m.group(0)}' 근처에 [별도]/[그룹] 라벨이 없습니다."
                        })
    return issues


def _get_table_ranges(lines):
    """마크다운 테이블의 시작~끝 행 인덱스 범위 반환"""
    ranges = []
    i = 0
    while i < len(lines):
        if '|' in lines[i] and i + 1 < len(lines) and re.match(r'\s*\|[\s\-:]+\|', lines[i + 1]):
            start = i
            j = i + 2
            while j < len(lines) and '|' in lines[j] and lines[j].strip().startswith('|'):
                j += 1
            ranges.append((start, j - 1))
            i = j
        else:
            i += 1
    return ranges


def _get_table_context_for_line(line_idx, table_ranges):
    """주어진 행이 테이블 내부인 경우 해당 테이블의 (start, end) 반환"""
    for start, end in table_ranges:
        if start <= line_idx <= end:
            return (start, end)
    return None


def validate_internal_terms(lines):
    """검증 7: 내부 용어 잔여"""
    issues = []
    in_code_block = False

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 화이트리스트 컨텍스트 체크
        skip = False
        for ctx_pattern in INTERNAL_TERMS_WHITELIST_CONTEXTS:
            if re.match(ctx_pattern, line.strip()):
                skip = True
                break
        if skip:
            continue

        for term in INTERNAL_TERMS:
            if term in line:
                issues.append({
                    "line": i,
                    "issue_type": "internal_term",
                    "severity": "warning",
                    "description": f"내부 용어 잔여: '{term}'. 최종 보고서에는 외부 독자 기준 용어를 사용하세요."
                })
    return issues


def validate_duplicate_words_brackets(lines):
    """검증 8: 중복 단어/괄호 불일치"""
    issues = []
    in_code_block = False

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 중복 단어 체크 (한국어 3음절 이상, 영어 3자 이상 연속 동일)
        # 2음절은 "빌리빌리" 같은 고유명사 false positive가 많으므로 3음절부터
        dup_ko = re.findall(r'([\uac00-\ud7af]{3,})\s+\1', line)
        for dup in dup_ko:
            issues.append({
                "line": i,
                "issue_type": "duplicate_word",
                "severity": "warning",
                "description": f"중복 단어 의심: '{dup} {dup}'"
            })

        dup_en = re.findall(r'\b([a-zA-Z]{3,})\s+\1\b', line, re.IGNORECASE)
        for dup in dup_en:
            # "the the" 같은 명백한 중복만
            issues.append({
                "line": i,
                "issue_type": "duplicate_word",
                "severity": "warning",
                "description": f"중복 단어 의심: '{dup} {dup}'"
            })

        # 괄호 불일치
        # 소괄호
        if line.count("(") != line.count(")"):
            issues.append({
                "line": i,
                "issue_type": "bracket_mismatch",
                "severity": "warning",
                "description": f"소괄호 불일치: '(' {line.count('(')}개, ')' {line.count(')')}개"
            })

    return issues


def validate_source_citations(lines):
    """검증 10: 인라인 출처 ID 유무 (EP-020)
    숫자+단위 포함 라인에 [S##] 패턴이 있는지 확인
    """
    issues = []
    # 수치+단위 패턴: 억, 조, $, %, 명 등
    # "배" 뒤에 한글이 오면 제외 (예: "2. 배경" false positive 방지)
    numeric_unit_pattern = re.compile(
        r'(?:\d[\d,.]*\s*(?:억|조|만|명|%|달러|\$|원|배(?![가-힣])|종))'
    )
    # 출처 ID 패턴: [S01], [S02] 등
    source_id_pattern = re.compile(r'\[S\d{2,3}\]')

    in_code_block = False
    table_ranges = _get_table_ranges(lines)

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # 코드 블록 내부 제외
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 테이블 헤더행 제외 (구분선 바로 위 행)
        if i < len(lines) and re.match(r'\s*\|[\s\-:]+\|', lines[i] if i < len(lines) else ''):
            continue

        # 테이블 구분선 자체 제외
        if re.match(r'\s*\|[\s\-:]+\|', stripped):
            continue

        # 목차 행 제외 (## 으로 시작하는 헤딩)
        if stripped.startswith('#'):
            continue

        # 타임라인 다이어그램 제외 (코드 블록 안이므로 이미 제외됨)
        # 빈 행 제외
        if not stripped:
            continue

        # 수치+단위가 있는 라인 탐지
        if numeric_unit_pattern.search(line):
            # 해당 라인 또는 인접 라인(±1)에 [S##] 패턴이 있는지 확인
            context_lines = []
            for offset in [-1, 0, 1]:
                idx = i - 1 + offset
                if 0 <= idx < len(lines):
                    context_lines.append(lines[idx])
            context = "\n".join(context_lines)

            if not source_id_pattern.search(context):
                # 인용 블록(>) 내 메타 정보는 심각도 낮춤 — 여전히 보고
                issues.append({
                    "line": i,
                    "issue_type": "source_citation_missing",
                    "severity": "error",
                    "description": f"인라인 출처 미표기: 수치/단위가 포함된 라인에 [S##] 출처 ID가 없습니다. 모든 수치에는 출처가 필수입니다."
                })

    return issues


def validate_tilde_strikethrough(lines):
    """검증 11: 틸드(~) 문자 감지 (EP-021)
    GitHub Flavored Markdown에서 ~가 취소선(~~)으로 렌더링되는 문제 방지.
    범위 표현(N~M)이나 근사값(~N)의 ~ 사용을 감지하고 en-dash(–) 또는 '약'으로 대체 권고.
    """
    issues = []
    in_code_block = False
    # 테이블 헤더 구분선(|---|)의 ~ 는 무시
    tilde_pattern = re.compile(r'~')

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if tilde_pattern.search(line):
            issues.append({
                "line": i,
                "issue_type": "tilde_strikethrough_risk",
                "severity": "warning",
                "description": f"틸드(~) 문자 발견: GitHub에서 취소선으로 렌더링될 수 있음. 범위는 en-dash(–), 근사값은 '약'으로 대체 권고."
            })

    return issues


def validate_table_column_consistency(lines):
    """검증 12: 마크다운 테이블 열 수 일관성 — 모든 행의 열 수가 헤더와 동일한지 확인"""
    issues = []
    in_code_block = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 코드 블록 내부 제외
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            i += 1
            continue

        # 테이블 헤더 감지: | 로 구분된 행 + 다음 행이 구분선(|---|)
        if '|' in line and i + 1 < len(lines) and re.match(r'\s*\|[\s\-:]+\|', lines[i + 1]):
            header_cells = [c for c in line.split('|')]
            # 앞뒤 빈 요소 제거 (| col1 | col2 | → ['', ' col1 ', ' col2 ', ''])
            if header_cells and header_cells[0].strip() == '':
                header_cells = header_cells[1:]
            if header_cells and header_cells[-1].strip() == '':
                header_cells = header_cells[:-1]
            header_col_count = len(header_cells)
            header_line = i + 1  # 1-indexed

            # 데이터 행 검사 (구분선 다음부터)
            j = i + 2
            while j < len(lines) and '|' in lines[j] and lines[j].strip().startswith('|'):
                row_cells = [c for c in lines[j].split('|')]
                if row_cells and row_cells[0].strip() == '':
                    row_cells = row_cells[1:]
                if row_cells and row_cells[-1].strip() == '':
                    row_cells = row_cells[:-1]
                row_col_count = len(row_cells)

                if row_col_count != header_col_count:
                    issues.append({
                        "line": j + 1,
                        "issue_type": "table_column_consistency",
                        "severity": "warning",
                        "description": f"테이블 열 수 불일치: 헤더({header_col_count}열, 행 {header_line})와 현재 행({row_col_count}열)의 열 수가 다릅니다."
                    })
                j += 1
            i = j
        else:
            i += 1

    return issues


def validate_date_format_consistency(lines):
    """검증 13: 날짜 형식 일관성 — YYYY.MM.DD가 아닌 날짜 형식을 경고"""
    issues = []
    in_code_block = False

    # YYYY.MM.DD는 허용 — 그 외 형식을 감지
    # 비표준 패턴들 (한국어 문자가 \w에 포함되므로 ASCII만 경계 체크)
    non_standard_patterns = [
        # YYYY/MM/DD
        (re.compile(r'(?<![0-9a-zA-Z])(\d{4})/(\d{1,2})/(\d{1,2})(?![0-9a-zA-Z])'), "YYYY/MM/DD", "YYYY.MM.DD로 통일 권고"),
        # YYYY-MM-DD
        (re.compile(r'(?<![0-9a-zA-Z])(\d{4})-(\d{1,2})-(\d{1,2})(?![0-9a-zA-Z])'), "YYYY-MM-DD", "YYYY.MM.DD로 통일 권고"),
        # MM/DD/YYYY
        (re.compile(r'(?<![0-9a-zA-Z])(\d{1,2})/(\d{1,2})/(\d{4})(?![0-9a-zA-Z])'), "MM/DD/YYYY", "YYYY.MM.DD로 통일 권고"),
        # DD.MM.YYYY (일.월.연)
        (re.compile(r'(?<![0-9a-zA-Z])(\d{1,2})\.(\d{1,2})\.(\d{4})(?![0-9a-zA-Z])'), "DD.MM.YYYY", "YYYY.MM.DD로 통일 권고"),
    ]

    # 버전 번호 패턴 (v1.2.3 등 — 제외 대상)
    version_pattern = re.compile(r'v\d+\.\d+(?:\.\d+)?')
    # URL 패턴 (제외 대상)
    url_pattern = re.compile(r'https?://\S+')

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # 코드 블록 내부 제외
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # URL과 버전 번호를 마스킹하여 false positive 방지
        masked_line = line
        for url_match in url_pattern.finditer(line):
            masked_line = masked_line.replace(url_match.group(), ' ' * len(url_match.group()))
        for ver_match in version_pattern.finditer(masked_line):
            masked_line = masked_line.replace(ver_match.group(), ' ' * len(ver_match.group()))

        for pattern, fmt_name, suggestion in non_standard_patterns:
            for m in pattern.finditer(masked_line):
                matched_text = m.group(0)
                # DD.MM.YYYY 패턴의 경우, YYYY.MM.DD와 구별 필요
                # DD.MM.YYYY: 첫 번째 그룹이 1~31, 두 번째가 1~12, 세 번째가 4자리 연도
                if fmt_name == "DD.MM.YYYY":
                    g1, g2, g3 = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    # YYYY.MM.DD 형식인 경우(첫 그룹이 연도 범위) 건너뜀
                    if g1 >= 1900:
                        continue
                    # 유효한 날짜인지 기본 확인 (일: 1~31, 월: 1~12)
                    if not (1 <= g1 <= 31 and 1 <= g2 <= 12):
                        continue

                # YYYY-MM-DD: 연도 범위 확인
                if fmt_name == "YYYY-MM-DD":
                    year = int(m.group(1))
                    month = int(m.group(2))
                    day = int(m.group(3))
                    if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                        continue

                # YYYY/MM/DD: 연도 범위 확인
                if fmt_name == "YYYY/MM/DD":
                    year = int(m.group(1))
                    month = int(m.group(2))
                    day = int(m.group(3))
                    if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                        continue

                # MM/DD/YYYY: 범위 확인
                if fmt_name == "MM/DD/YYYY":
                    month = int(m.group(1))
                    day = int(m.group(2))
                    year = int(m.group(3))
                    if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                        continue

                issues.append({
                    "line": i,
                    "issue_type": "date_format_consistency",
                    "severity": "warning",
                    "description": f"비표준 날짜 형식: '{matched_text}' ({fmt_name}). {suggestion}."
                })

    return issues


def validate_fy_cy_mixing(lines):
    """검증 14: FY/CY 혼용 경고 — FY 표기와 역년 표기가 혼용될 때 경고"""
    issues = []
    in_code_block = False

    # FY 표기 패턴: FY2025, FY25, FY 2025 등
    fy_pattern = re.compile(r'\bFY\s*\'?(\d{2,4})\b')
    # FY 결산월 명시 패턴: FY2025(3월 결산), FY2025 (3월말 기준) 등
    fy_month_pattern = re.compile(r'\bFY\s*\'?\d{2,4}\s*[\(（].*?(?:월|月|March|June|September|December|Mar|Jun|Sep|Dec).*?[\)）]')

    # 역년(Calendar Year) 표기: 2025년, 2025 회계연도 등
    cy_pattern = re.compile(r'(\d{4})\s*년')

    fy_lines = []  # (line_number, matched_text, year)
    cy_lines = []  # (line_number, matched_text, year)
    fy_with_month = []  # FY 결산월이 명시된 행

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # 코드 블록 내부 제외
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # FY 결산월 명시 감지
        if fy_month_pattern.search(line):
            fy_with_month.append(i)

        # FY 표기 수집
        for m in fy_pattern.finditer(line):
            year_str = m.group(1)
            year = int(year_str) if len(year_str) == 4 else 2000 + int(year_str)
            fy_lines.append((i, m.group(0), year))

        # 역년 표기 수집
        for m in cy_pattern.finditer(line):
            year = int(m.group(1))
            if 2000 <= year <= 2100:  # 합리적 연도 범위만
                cy_lines.append((i, m.group(0), year))

    # FY와 CY가 모두 존재하는 경우
    if fy_lines and cy_lines:
        # 동일 연도에 대해 FY와 CY 표기가 모두 사용되는지 확인
        fy_years = set(item[2] for item in fy_lines)
        cy_years = set(item[2] for item in cy_lines)
        overlapping_years = fy_years & cy_years

        if overlapping_years:
            # FY 결산월이 명시되지 않은 경우만 경고
            for year in overlapping_years:
                fy_line_nums = [item[0] for item in fy_lines if item[2] == year]
                cy_line_nums = [item[0] for item in cy_lines if item[2] == year]
                issues.append({
                    "line": fy_line_nums[0],
                    "issue_type": "fy_cy_mixing",
                    "severity": "warning",
                    "description": f"FY/CY 혼용: {year}년에 대해 FY 표기(행 {fy_line_nums[0]})와 역년 표기(행 {cy_line_nums[0]})가 동시 사용됨. 회계연도와 역년의 차이를 명시하세요."
                })

    # FY 표기가 있지만 결산월이 명시되지 않은 경우
    if fy_lines and not fy_with_month:
        first_fy = fy_lines[0]
        issues.append({
            "line": first_fy[0],
            "issue_type": "fy_cy_mixing",
            "severity": "warning",
            "description": f"FY 표기 결산월 미명시: '{first_fy[1]}' — FY 사용 시 결산월을 표기하세요 (예: FY2025(3월 결산))."
        })

    return issues


def validate_narrative_table_pct(lines):
    """검증 9: 서술-테이블 % 교차 (EP-017)
    본문 서술의 % 수치가 동일 보고서 내 테이블 역산값과 ±2%p 이내인지 확인
    """
    issues = []

    # 테이블에서 연도별 수치 추출
    tables = _extract_tables(lines)

    # "연 N~M% 감소" 패턴 검출
    decay_pattern = re.compile(r'연\s*(\d+(?:\.\d+)?)~(\d+(?:\.\d+)?)\s*%\s*감소')
    growth_pattern = re.compile(r'연\s*(\d+(?:\.\d+)?)~(\d+(?:\.\d+)?)\s*%\s*(?:성장|증가)')

    in_code_block = False
    table_ranges = _get_table_ranges(lines)

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 테이블 셀 내부의 %는 서술이 아니라 데이터이므로 제외
        if _get_table_context_for_line(i - 1, table_ranges):
            continue

        # 감소율 서술
        for m in decay_pattern.finditer(line):
            lo, hi = float(m.group(1)), float(m.group(2))
            issues.append({
                "line": i,
                "issue_type": "narrative_table_pct",
                "severity": "error",
                "description": f"서술적 % 범위 발견: '연 {lo}~{hi}% 감소' — 테이블 역산값과 대조 필요 (EP-017). auditor가 정밀 검증합니다."
            })

        for m in growth_pattern.finditer(line):
            lo, hi = float(m.group(1)), float(m.group(2))
            issues.append({
                "line": i,
                "issue_type": "narrative_table_pct",
                "severity": "error",
                "description": f"서술적 % 범위 발견: '연 {lo}~{hi}% 성장/증가' — 테이블 역산값과 대조 필요 (EP-017). auditor가 정밀 검증합니다."
            })

    return issues


# ── 유틸리티 함수 ──

def _extract_tables(lines):
    """마크다운 테이블을 파싱하여 구조화된 리스트로 반환"""
    tables = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 테이블 헤더 감지: | 로 시작하고 | 로 끝나는 행 + 다음 행이 구분선(|---|)
        if '|' in line and i + 1 < len(lines) and re.match(r'\s*\|[\s\-:]+\|', lines[i + 1]):
            header_cells = [c.strip() for c in line.split('|')]
            # 앞뒤 빈 셀 제거
            header_cells = [c for c in header_cells if c or header_cells.index(c) not in [0, len(header_cells) - 1]]
            if not header_cells:
                header_cells = [c.strip() for c in line.split('|')[1:-1]]

            header = [c.strip() for c in line.split('|')[1:-1]]
            rows = []
            j = i + 2  # 구분선 다음부터

            while j < len(lines) and '|' in lines[j] and lines[j].strip().startswith('|'):
                cells = [c.strip() for c in lines[j].split('|')[1:-1]]
                rows.append({"line": j + 1, "cells": cells})
                j += 1

            if rows:
                tables.append({
                    "header_line": i + 1,
                    "header": header,
                    "rows": rows
                })
            i = j
        else:
            i += 1

    return tables


def _identify_numeric_columns(header, rows):
    """숫자 데이터가 주로 있는 열 인덱스를 반환"""
    numeric_cols = []
    for col_idx in range(len(header)):
        numeric_count = 0
        total_count = 0
        for row_info in rows:
            row = row_info["cells"]
            if col_idx < len(row):
                total_count += 1
                if _parse_number(row[col_idx]) is not None:
                    numeric_count += 1
        if total_count > 0 and numeric_count / total_count >= 0.5:
            numeric_cols.append(col_idx)
    return numeric_cols


def _parse_number(text):
    """텍스트에서 숫자를 추출. 실패 시 None 반환"""
    if not text:
        return None
    # 볼드, 공백, 통화 기호 제거
    cleaned = text.strip().replace("**", "").replace(",", "").replace("억", "").replace("원", "")
    cleaned = cleaned.replace("~", "").replace("약", "").strip()

    # 범위(N~M)는 무시 — 합계에 쓸 수 없음
    if "~" in text.replace("~", "", 1):
        return None

    # "—", "-" (데이터 없음) 처리
    if cleaned in ["—", "-", "–", "", "평가 중", "미정"]:
        return None

    # "N~M" 범위 패턴 처리 (하이픈 아닌 틸드)
    range_match = re.match(r'^([\d.]+)\s*[~\-–]\s*([\d.]+)$', cleaned)
    if range_match:
        return None  # 범위값은 합산 대상 아님

    # 일반 숫자
    try:
        return float(cleaned)
    except ValueError:
        return None


# ── 메인 실행 ──

def run_all_validations(filepath):
    """전체 검증 실행"""
    path = Path(filepath)
    if not path.exists():
        print(json.dumps({"error": f"파일을 찾을 수 없습니다: {filepath}"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)

    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    all_issues = []

    # 코드 블록 내부 라인 마킹 (검증 1, 2에서 코드 블록 제외)
    in_code_block = False
    code_block_lines = set()
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            code_block_lines.add(i)
            continue
        if in_code_block:
            code_block_lines.add(i)

    # 검증 1~9 실행
    validators = [
        ("1_ep_reference", validate_ep_references),
        ("2_strikethrough", validate_strikethrough),
        ("3_banned_chars", validate_banned_chars),
        ("4_table_arithmetic", validate_table_arithmetic),
        ("5_cross_reference", validate_cross_reference_consistency),
        ("6_entity_label", validate_entity_labels),
        ("7_internal_terms", validate_internal_terms),
        ("8_duplicate_brackets", validate_duplicate_words_brackets),
        ("9_narrative_table_pct", validate_narrative_table_pct),
        ("10_source_citation", validate_source_citations),
        ("11_tilde_strikethrough", validate_tilde_strikethrough),
        ("12_table_column_consistency", validate_table_column_consistency),
        ("13_date_format_consistency", validate_date_format_consistency),
        ("14_fy_cy_mixing", validate_fy_cy_mixing),
    ]

    for name, validator_fn in validators:
        try:
            issues = validator_fn(lines)
            # 코드 블록 내부 이슈 필터링 (검증 1, 2)
            if name in ["1_ep_reference", "2_strikethrough"]:
                issues = [iss for iss in issues if (iss["line"] - 1) not in code_block_lines]
            all_issues.extend(issues)
        except Exception as e:
            all_issues.append({
                "line": 0,
                "issue_type": f"{name}_error",
                "severity": "warning",
                "description": f"검증 '{name}' 실행 중 오류: {str(e)}"
            })

    # 결과 집계
    by_severity = {"error": 0, "warning": 0}
    for iss in all_issues:
        by_severity[iss["severity"]] = by_severity.get(iss["severity"], 0) + 1

    result = {
        "file": str(filepath),
        "total_issues": len(all_issues),
        "by_severity": by_severity,
        "issues": all_issues
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("사용법: python scripts/mechanical-validator.py <마크다운 파일 경로>", file=sys.stderr)
        sys.exit(2)

    filepath = sys.argv[1]
    result = run_all_validations(filepath)

    # JSON 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 종료 코드
    sys.exit(0 if result["total_issues"] == 0 else 1)


if __name__ == "__main__":
    main()
