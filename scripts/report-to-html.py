#!/usr/bin/env python3
"""
보고서 마크다운 → HTML 변환기

단일 HTML 파일에 3개 탭으로 통합:
  - 요약 (Executive): 슬라이드 프레젠테이션 스타일, 경영진용
  - 클린 (Clean): 출처 제거, 깔끔한 보고서 스타일
  - 출처 (Sourced): [S##] 클릭 가능 + 사이드바, 실무자용

특징:
  - 100% 자기완결형(self-contained) — 외부 의존성 없음
  - 파일 다운로드 후 오프라인에서 바로 열기 가능

사용법:
  python3 report-to-html.py <보고서.md> <source-index.md> [출력.html]
"""

import re
import sys
import os
import markdown


def parse_source_index(index_path):
    """source-index.md에서 S##/U## → {url, name, reliability} 매핑 추출"""
    source_map = {}
    with open(index_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    table_pattern = re.compile(
        r"^\|\s*([SU]\d+)\s*\|"
        r"\s*(.*?)\s*\|"
        r"\s*(.*?)\s*\|"
        r"\s*(.*?)\s*\|"
        r"\s*(.*?)\s*\|"
        r"\s*(.*?)\s*\|"
        r"\s*(.*?)\s*\|"
    )

    for line in lines:
        m = table_pattern.match(line.strip())
        if m:
            sid = m.group(1).strip()
            name = m.group(2).strip()
            url = m.group(4).strip()
            reliability = m.group(7).strip()
            source_map[sid] = {"url": url, "name": name, "reliability": reliability}

    return source_map


def remove_source_tags(text):
    """[S##]/[U##] 태그 제거"""
    return re.sub(r"\[([SU]\d+)\]", "", text)


def strip_metadata(md_content):
    """슬라이드 메타데이터 제거 (레이아웃, 다이어그램/차트 플레이스홀더)"""
    lines = md_content.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # **레이아웃**: ... 제거
        if stripped.startswith("**레이아웃**"):
            continue
        # [다이어그램: ...], [차트: ...] 플레이스홀더 제거
        if re.match(r"^\[(다이어그램|차트)\s*:", stripped):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def remove_presenter_notes(md_content):
    """발표자 노트(> 발표자 노트: ...) 제거"""
    lines = md_content.split("\n")
    cleaned = []
    skip = False
    for line in lines:
        if "발표자 노트" in line and line.strip().startswith(">"):
            skip = True
            continue
        if skip and line.strip().startswith(">"):
            continue
        skip = False
        cleaned.append(line)
    return "\n".join(cleaned)


def replace_source_tags(html_content, source_map):
    """[S##]/[U##] 태그를 클릭 가능한 링크로 변환"""

    def replace_tag(match):
        sid = match.group(1)
        if sid in source_map:
            src = source_map[sid]
            url = src["url"]
            name = src["name"]
            reliability = src["reliability"]
            if url.startswith("http"):
                color_map = {"High": "#2563eb", "Medium": "#d97706", "Low": "#dc2626"}
                color = color_map.get(reliability, "#6b7280")
                return (
                    f'<a href="{url}" target="_blank" rel="noopener" '
                    f'class="stag" data-sid="{sid}" data-r="{reliability}" '
                    f'title="{name} ({reliability})" '
                    f'style="color:{color};">[{sid}]</a>'
                )
            return f'<span class="stag int" title="{name}">[{sid}]</span>'
        return match.group(0)

    return re.compile(r"\[([SU]\d+)\]").sub(replace_tag, html_content)


def md_to_html(md_content, is_slides=False):
    """마크다운 → HTML 본문 변환"""
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "attr_list", "md_in_html"],
        extension_configs={"toc": {"title": "목차", "toc_depth": 3}},
    )
    html = md.convert(md_content)

    if is_slides:
        html = html.replace("<hr />", '</div><div class="slide">')
        html = f'<div class="slide">{html}</div>'
        html = html.replace('<div class="slide"></div>', "", 1)

    return html


def build_source_json(source_map):
    """JavaScript용 소스 JSON 문자열"""
    items = []
    for sid, src in sorted(source_map.items()):
        url = src["url"]
        name = src["name"].replace('"', '\\"').replace("'", "\\'")
        rel = src["reliability"]
        if url.startswith("http"):
            items.append(f'"{sid}":{{"u":"{url}","n":"{name}","r":"{rel}"}}')
    return "{" + ",".join(items) + "}"


def generate_combined_html(report_path, source_index_path, output_path):
    """3탭 통합 HTML 생성"""

    source_map = parse_source_index(source_index_path)
    print(f"소스 매핑 로드: {len(source_map)}개 소스")

    with open(report_path, "r", encoding="utf-8") as f:
        md_raw = f.read()

    title_match = re.match(r"^#\s+(.+)$", md_raw, re.MULTILINE)
    title = title_match.group(1) if title_match else "보고서"

    is_slides = "report-slides" in report_path

    # --- 3가지 버전 ---
    # Executive: 메타데이터 + 출처 + 발표자 노트 제거, 슬라이드 레이아웃
    md_exec = strip_metadata(remove_presenter_notes(remove_source_tags(md_raw)))
    html_exec = md_to_html(md_exec, is_slides=True)

    # Clean: 메타데이터 + 출처 제거
    md_clean = strip_metadata(remove_source_tags(md_raw))
    html_clean = md_to_html(md_clean, is_slides=is_slides)

    # Sourced: 메타데이터 제거 + 출처 링크 변환
    md_sourced = strip_metadata(md_raw)
    html_sourced_raw = md_to_html(md_sourced, is_slides=is_slides)
    html_sourced = replace_source_tags(html_sourced_raw, source_map)

    tag_count = len(re.findall(r'class="stag"', html_sourced))
    link_count = len(re.findall(r'data-r=', html_sourced))
    source_json = build_source_json(source_map)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
/* ===== 리셋 ===== */
*{{margin:0;padding:0;box-sizing:border-box;}}

/* ===== 컬러 ===== */
:root{{
  --ink:#1a1a2e;--sub:#475569;--mute:#94a3b8;
  --bg:#f5f5f7;--card:#fff;--line:#e5e5ea;
  --blue:#0066cc;--blue-bg:#eef4ff;
  --orange:#b45309;--red:#c0392b;
}}

body{{
  font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',sans-serif;
  background:var(--bg);color:var(--ink);
  font-size:15px;line-height:1.65;
  -webkit-font-smoothing:antialiased;
}}

/* ===== 헤더 네비게이션 ===== */
.nav{{
  position:sticky;top:0;z-index:999;
  background:var(--ink);
  display:flex;align-items:stretch;
  height:46px;
  box-shadow:0 1px 4px rgba(0,0,0,.2);
}}
.nav-title{{
  color:rgba(255,255,255,.7);
  font-size:13px;font-weight:600;
  padding:0 20px;
  display:flex;align-items:center;
  border-right:1px solid rgba(255,255,255,.1);
  white-space:nowrap;
}}
.tab{{
  background:none;border:none;
  color:rgba(255,255,255,.5);
  font-size:13px;font-weight:500;
  padding:0 18px;cursor:pointer;
  border-bottom:2px solid transparent;
  transition:all .15s;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  gap:1px;
}}
.tab:hover{{color:rgba(255,255,255,.8);background:rgba(255,255,255,.05);}}
.tab.on{{color:#fff;border-bottom-color:#4dabf7;font-weight:600;}}
.tab small{{font-size:10px;opacity:.55;font-weight:400;}}

/* ===== 탭 패널 ===== */
.panel{{display:none;}}
.panel.on{{display:block;}}

/* ===== 공통 보고서 스타일 ===== */
.report{{
  max-width:880px;
  margin:0 auto;
  padding:28px 36px 60px;
}}
h1{{
  font-size:22px;font-weight:700;color:var(--ink);
  margin:20px 0 8px;
  padding-bottom:8px;
  border-bottom:2px solid var(--ink);
}}
h2{{
  font-size:17px;font-weight:700;color:var(--ink);
  margin:28px 0 10px;
  padding-bottom:6px;
  border-bottom:1px solid var(--line);
}}
h3{{
  font-size:16px;font-weight:700;color:var(--ink);
  margin:24px 0 8px;
  padding-left:10px;
  border-left:3px solid var(--blue);
}}
h4{{
  font-size:15px;font-weight:600;color:#1e293b;
  margin:20px 0 6px;
}}
h5{{
  font-size:14px;font-weight:600;color:#334155;
  margin:16px 0 6px;
  padding-bottom:4px;
  border-bottom:1px dashed var(--line);
}}
p{{margin:6px 0 10px;}}
blockquote{{
  border-left:3px solid var(--blue);
  padding:10px 16px;margin:14px 0;
  background:var(--blue-bg);
  border-radius:0 6px 6px 0;
  color:var(--sub);font-size:14px;
}}
strong{{color:var(--ink);}}
ul,ol{{margin:6px 0 10px 20px;}}
li{{margin:3px 0;}}
hr{{border:none;border-top:2px solid var(--line);margin:32px 0;}}

/* ===== 테이블 ===== */
table{{
  width:100%;border-collapse:collapse;
  margin:8px 0 12px;font-size:13.5px;
}}
thead th{{
  background:var(--ink);color:#fff;
  padding:7px 10px;text-align:left;
  font-weight:600;font-size:12.5px;
  text-transform:uppercase;letter-spacing:.3px;
}}
tbody td{{
  padding:6px 10px;
  border-bottom:1px solid var(--line);
  vertical-align:top;
}}
tbody tr:hover{{background:#f8f9fa;}}

/* ===== 코드 ===== */
pre{{
  background:var(--ink);color:#e2e8f0;
  padding:14px 16px;border-radius:6px;
  overflow-x:auto;margin:8px 0;
  font-size:12.5px;line-height:1.5;
}}
code{{font-family:'SF Mono','Fira Code',monospace;font-size:.85em;}}
p code,li code,td code{{
  background:#f1f3f5;padding:1px 5px;
  border-radius:3px;color:#c0392b;font-size:12.5px;
}}

/* ===== 출처 태그 ===== */
.stag{{
  font-size:11px;font-weight:600;
  text-decoration:none;cursor:pointer;
  padding:0 2px;border-radius:2px;
  transition:background .1s;
}}
.stag:hover{{background:#dbeafe;text-decoration:underline;}}
.stag.int{{color:var(--mute);cursor:default;}}

/* ========================================
   EXECUTIVE 슬라이드 스타일
   ======================================== */
.exec-wrap{{
  max-width:1000px;
  margin:0 auto;
  padding:20px 24px 60px;
}}

.slide{{
  background:#fff;
  border-radius:8px;
  box-shadow:0 1px 4px rgba(0,0,0,.07);
  padding:36px 44px 32px;
  margin:16px 0;
  position:relative;
  min-height:120px;
  page-break-inside:avoid;
}}
/* 슬라이드 번호 */
.slide::after{{
  content:attr(data-n);
  position:absolute;bottom:12px;right:18px;
  font-size:11px;color:var(--mute);font-weight:500;
}}
/* 슬라이드 상단 액센트 라인 */
.slide::before{{
  content:'';position:absolute;top:0;left:0;right:0;
  height:3px;background:linear-gradient(90deg,#0066cc,#4dabf7);
  border-radius:8px 8px 0 0;
}}

/* 슬라이드 내 타이포 오버라이드 */
.slide h2{{
  font-size:19px;font-weight:700;
  color:var(--ink);
  margin:0 0 14px;padding:0;
  border:none;
  line-height:1.3;
}}
.slide h3{{font-size:14px;margin:12px 0 6px;}}
.slide h4{{font-size:13px;margin:10px 0 4px;}}
.slide p{{font-size:14px;margin:3px 0 6px;line-height:1.6;}}
.slide ul,.slide ol{{font-size:14px;margin:4px 0 8px 18px;}}
.slide li{{margin:2px 0;}}
.slide table{{font-size:13px;margin:6px 0 10px;}}
.slide thead th{{
  font-size:11.5px;padding:6px 8px;
  background:#1a1a2e;
}}
.slide tbody td{{padding:5px 8px;font-size:13px;}}
.slide blockquote{{
  font-size:13px;padding:6px 12px;margin:8px 0;
}}
.slide strong{{color:var(--ink);}}
.slide pre{{font-size:12px;padding:10px 14px;}}

/* 첫 번째 슬라이드 = 표지 */
.slide:first-child{{
  text-align:center;
  padding:60px 44px 48px;
  background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
  color:#fff;
}}
.slide:first-child::before{{display:none;}}
.slide:first-child h2{{color:#fff;font-size:24px;margin-bottom:16px;}}
.slide:first-child p{{color:rgba(255,255,255,.75);font-size:15px;}}
.slide:first-child blockquote{{
  background:rgba(255,255,255,.08);border-left-color:rgba(255,255,255,.3);
  color:rgba(255,255,255,.6);
}}
.slide:first-child strong{{color:#fff;}}

/* 핵심 메시지 강조 */
.slide p:has(strong:first-child){{
  font-size:14.5px;
}}

/* ===== Sourced 사이드바 ===== */
.src-layout{{display:flex;max-width:1200px;margin:0 auto;}}
.src-layout .report{{flex:1;}}
.sidebar{{
  width:300px;
  position:sticky;top:46px;
  height:calc(100vh - 46px);
  overflow-y:auto;
  border-left:1px solid var(--line);
  background:#fff;padding:16px;
  display:none;
}}
.sidebar.on{{display:block;}}
.sidebar h3{{font-size:13px;font-weight:600;margin:0 0 10px;color:var(--ink);}}
.sb-toggle{{
  position:fixed;bottom:16px;right:16px;
  width:42px;height:42px;border-radius:50%;
  background:var(--blue);color:#fff;border:none;
  cursor:pointer;font-size:16px;
  box-shadow:0 3px 10px rgba(0,102,204,.35);
  z-index:100;display:none;
  align-items:center;justify-content:center;
}}
.sb-toggle.on{{display:flex;}}
.sp{{
  background:#f8f9fa;border:1px solid var(--line);
  border-radius:6px;padding:10px;margin-top:8px;
  display:none;font-size:13px;
}}
.sp.on{{display:block;}}
.sp h4{{margin:0 0 4px;font-size:13px;}}
.sp a{{color:var(--blue);word-break:break-all;font-size:12px;}}
.rl{{display:inline-block;padding:1px 6px;border-radius:3px;font-size:11px;font-weight:600;}}
.rl-High{{background:#dbeafe;color:#1e40af;}}
.rl-Medium{{background:#fef3c7;color:#92400e;}}
.rl-Low{{background:#fee2e2;color:#991b1b;}}

/* ===== 프린트 ===== */
@media print{{
  .nav,.sidebar,.sb-toggle{{display:none!important;}}
  .panel{{display:block!important;}}
  .panel:not(.print-target){{display:none!important;}}
  .report,.exec-wrap{{padding:10px;max-width:100%;}}
  .slide{{box-shadow:none;margin:10px 0;page-break-after:always;}}
  .slide:first-child{{background:var(--ink)!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
}}

/* ===== 반응형 ===== */
@media(max-width:900px){{
  .report{{padding:16px 18px 40px;}}
  .exec-wrap{{padding:10px 8px 40px;}}
  .slide{{padding:24px 22px 24px;margin:10px 0;}}
  .sidebar{{display:none!important;}}
  .nav-title{{display:none;}}
  .tab{{padding:0 12px;font-size:12px;}}
}}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-title">{title}</div>
  <button class="tab on" data-t="exec" onclick="go('exec')">요약<small>경영진</small></button>
  <button class="tab" data-t="clean" onclick="go('clean')">클린<small>팀장/타부서</small></button>
  <button class="tab" data-t="src" onclick="go('src')">출처<small>실무자</small></button>
</nav>

<div id="p-exec" class="panel on">
  <div class="exec-wrap">{html_exec}</div>
</div>

<div id="p-clean" class="panel">
  <div class="report">{html_clean}</div>
</div>

<div id="p-src" class="panel">
  <div class="src-layout">
    <div class="report">{html_sourced}</div>
    <div class="sidebar" id="sb">
      <h3>출처 패널</h3>
      <p style="font-size:12px;color:var(--mute);">[S##] 태그를 클릭하면 해당 출처로 이동합니다.</p>
      <div id="sp" class="sp">
        <p style="color:var(--mute);font-size:12px;">출처 태그를 클릭하세요.</p>
      </div>
      <hr style="margin:10px 0;">
      <h3>전체 출처 ({len(source_map)}건)</h3>
      <div id="sl" style="font-size:12px;max-height:60vh;overflow-y:auto;"></div>
    </div>
  </div>
</div>

<button class="sb-toggle" id="sbt" title="출처 패널">&#128269;</button>

<script>
const S={source_json};

function go(t){{
  document.querySelectorAll('.panel').forEach(e=>e.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('on'));
  document.getElementById('p-'+t).classList.add('on');
  document.querySelector('[data-t="'+t+'"]').classList.add('on');
  var sbt=document.getElementById('sbt'),sb=document.getElementById('sb');
  if(t==='src'){{sbt.classList.add('on');}}
  else{{sbt.classList.remove('on');sb.classList.remove('on');}}
  window.scrollTo(0,0);
}}

// 슬라이드 번호
document.querySelectorAll('.slide').forEach(function(s,i){{s.dataset.n=i+1;}});

// 사이드바 토글
document.getElementById('sbt').addEventListener('click',function(){{
  document.getElementById('sb').classList.toggle('on');
}});

// 출처 태그 클릭
document.querySelectorAll('.stag[data-sid]').forEach(function(t){{
  t.addEventListener('click',function(){{
    var sid=t.dataset.sid,s=S[sid];
    if(!s)return;
    var p=document.getElementById('sp');
    p.classList.add('on');
    p.innerHTML='<h4>'+sid+'</h4><p style="font-weight:600;margin:2px 0">'+s.n+'</p><p><span class="rl rl-'+s.r+'">'+s.r+'</span></p><p><a href="'+s.u+'" target="_blank" rel="noopener">'+s.u+'</a></p>';
    document.getElementById('sb').classList.add('on');
  }});
}});

// 출처 목록
(function(){{
  var el=document.getElementById('sl');if(!el)return;
  Object.keys(S).sort(function(a,b){{return parseInt(a.replace(/[SU]/,''))-parseInt(b.replace(/[SU]/,''));}}).forEach(function(sid){{
    var s=S[sid],d=document.createElement('div');
    d.style.cssText='padding:3px 0;border-bottom:1px solid #eee;';
    d.innerHTML='<a href="'+s.u+'" target="_blank" rel="noopener" style="font-weight:600;color:var(--ink);text-decoration:none;font-size:12px;">'+sid+'</a> <span class="rl rl-'+s.r+'" style="margin-left:2px;">'+s.r+'</span><br><span style="color:var(--mute);font-size:11px;">'+s.n+'</span>';
    el.appendChild(d);
  }});
}})();

// 인쇄
window.addEventListener('beforeprint',function(){{
  document.querySelectorAll('.panel').forEach(function(e){{e.classList.remove('print-target');}});
  document.querySelector('.panel.on').classList.add('print-target');
}});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML 생성 완료: {output_path}")
    print(f"  - 3탭: 요약 / 클린 / 출처")
    print(f"  - 출처 태그: {tag_count}개 ({link_count}개 외부 링크)")
    file_size = os.path.getsize(output_path)
    print(f"  - 파일 크기: {file_size / 1024:.0f} KB")


def main():
    if len(sys.argv) < 3:
        print("사용법: python3 report-to-html.py <보고서.md> <source-index.md> [출력.html]")
        sys.exit(1)

    report_path = sys.argv[1]
    index_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) >= 4 else os.path.splitext(report_path)[0] + ".html"

    if not os.path.exists(report_path):
        print(f"오류: 보고서 파일 없음 — {report_path}")
        sys.exit(1)
    if not os.path.exists(index_path):
        print(f"오류: 출처 인덱스 없음 — {index_path}")
        sys.exit(1)

    generate_combined_html(report_path, index_path, output_path)


if __name__ == "__main__":
    main()
