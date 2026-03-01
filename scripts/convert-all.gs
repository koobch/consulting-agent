/**
 * 리서치 보고서 변환 올인원 스크립트
 *
 * === 사용법 ===
 * 1. Google Drive에 report-docs.md, report-slides.md 파일을 업로드
 * 2. script.google.com에서 새 프로젝트 생성 → 이 코드 붙여넣기
 * 3. 아래 DRIVE_FILE_IDS에 업로드한 파일 ID 입력
 *    (파일 ID = Google Drive URL에서 /d/ 와 /view 사이의 문자열)
 * 4. runAll() 함수 실행
 * 5. 최초 실행 시 권한 승인 (Google Drive, Docs, Slides 접근)
 * 6. 실행 로그에서 생성된 문서 URL 확인
 */

// ============================================================
// ★ 여기만 수정하세요 ★
// ============================================================
const DRIVE_FILE_IDS = {
  docs: '',    // report-docs.md 파일 ID
  slides: '',  // report-slides.md 파일 ID
};

// 생성될 문서를 저장할 폴더 (빈 값이면 My Drive 루트)
const OUTPUT_FOLDER_ID = '';
// ============================================================

// 색상 테마
const THEME = {
  PRIMARY: '#1a1a2e',
  SECONDARY: '#16213e',
  ACCENT: '#0f3460',
  HIGHLIGHT: '#e94560',
  BG: '#ffffff',
  LIGHT_GRAY: '#f8f9fa',
  TEXT: '#333333',
  TEXT_LIGHT: '#ffffff',
  TEXT_GRAY: '#6c757d',
};

/**
 * ★ 메인 실행 함수 — Docs + Slides 모두 생성
 */
function runAll() {
  Logger.log('=== 리서치 보고서 변환 시작 ===\n');

  if (!DRIVE_FILE_IDS.docs && !DRIVE_FILE_IDS.slides) {
    Logger.log('⚠️ DRIVE_FILE_IDS에 파일 ID를 입력해주세요.');
    Logger.log('   Google Drive에 .md 파일 업로드 후, URL에서 파일 ID를 복사하세요.');
    Logger.log('   예: https://drive.google.com/file/d/[이부분이_파일ID]/view');
    return;
  }

  if (DRIVE_FILE_IDS.docs) {
    Logger.log('[1/2] Google Docs 생성 중...');
    const docsUrl = createGoogleDoc_();
    Logger.log('✅ Google Docs 완료: ' + docsUrl + '\n');
  }

  if (DRIVE_FILE_IDS.slides) {
    Logger.log('[2/2] Google Slides 생성 중...');
    const slidesUrl = createGoogleSlides_();
    Logger.log('✅ Google Slides 완료: ' + slidesUrl + '\n');
  }

  Logger.log('=== 모든 변환 완료 ===');
}

/** Docs만 생성 */
function runDocsOnly() {
  const url = createGoogleDoc_();
  Logger.log('✅ Google Docs: ' + url);
}

/** Slides만 생성 */
function runSlidesOnly() {
  const url = createGoogleSlides_();
  Logger.log('✅ Google Slides: ' + url);
}

// ============================================================
// Google Docs 생성
// ============================================================
function createGoogleDoc_() {
  const markdown = DriveApp.getFileById(DRIVE_FILE_IDS.docs).getBlob().getDataAsString('UTF-8');
  const doc = DocumentApp.create('리서치 보고서');
  const body = doc.getBody();

  body.setMarginTop(60);
  body.setMarginBottom(60);
  body.setMarginLeft(60);
  body.setMarginRight(60);

  // 기본 텍스트 삭제
  body.clear();

  const lines = markdown.split('\n');
  let i = 0;
  let tableBuffer = [];
  let inTable = false;
  let inCodeBlock = false;
  let codeBuffer = [];

  while (i < lines.length) {
    const line = lines[i];

    // 코드 블록
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        appendCodeBlock_(body, codeBuffer.join('\n'));
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      i++;
      continue;
    }
    if (inCodeBlock) {
      codeBuffer.push(line);
      i++;
      continue;
    }

    // 테이블
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      if (!inTable) { inTable = true; tableBuffer = []; }
      // 구분선 제외
      const stripped = line.replace(/\|/g, '').trim().replace(/[-:\s]/g, '');
      if (stripped !== '') {
        tableBuffer.push(line);
      }
      i++;
      continue;
    } else if (inTable) {
      appendTable_(body, tableBuffer);
      tableBuffer = [];
      inTable = false;
    }

    // 빈 줄 / 수평선
    if (line.trim() === '' || line.trim() === '---' || line.trim() === '***') {
      if (line.trim() === '---') {
        body.appendHorizontalRule();
      }
      i++;
      continue;
    }

    // 헤딩
    if (line.startsWith('# ')) {
      appendHeading_(body, cleanMd_(line.substring(2)), DocumentApp.ParagraphHeading.HEADING1, 22, THEME.PRIMARY);
    } else if (line.startsWith('## ')) {
      appendHeading_(body, cleanMd_(line.substring(3)), DocumentApp.ParagraphHeading.HEADING2, 16, THEME.PRIMARY);
    } else if (line.startsWith('### ')) {
      appendHeading_(body, cleanMd_(line.substring(4)), DocumentApp.ParagraphHeading.HEADING3, 13, THEME.SECONDARY);
    } else if (line.startsWith('#### ')) {
      appendHeading_(body, cleanMd_(line.substring(5)), DocumentApp.ParagraphHeading.HEADING4, 11, THEME.ACCENT);
    }
    // 불릿
    else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const indent = line.search(/\S/);
      const text = cleanMd_(line.trim().substring(2));
      const li = body.appendListItem(text);
      li.setGlyphType(DocumentApp.GlyphType.BULLET);
      li.setFontSize(10);
      if (indent > 2) li.setNestingLevel(1);
      applyBold_(li, line.trim().substring(2));
    }
    // 번호 리스트
    else if (/^\d+\.\s/.test(line.trim())) {
      const text = cleanMd_(line.trim().replace(/^\d+\.\s/, ''));
      const li = body.appendListItem(text);
      li.setGlyphType(DocumentApp.GlyphType.NUMBER);
      li.setFontSize(10);
      applyBold_(li, line.trim().replace(/^\d+\.\s/, ''));
    }
    // 인용
    else if (line.trim().startsWith('> ')) {
      const para = body.appendParagraph(cleanMd_(line.trim().substring(2)));
      para.setFontSize(9);
      para.setItalic(true);
      para.setForegroundColor(THEME.TEXT_GRAY);
      para.setIndentStart(36);
    }
    // 일반 텍스트
    else {
      const para = body.appendParagraph(cleanMd_(line.trim()));
      para.setFontSize(10);
      para.setForegroundColor(THEME.TEXT);
      applyBold_(para, line.trim());
    }

    i++;
  }

  // 마지막 테이블
  if (inTable && tableBuffer.length > 0) {
    appendTable_(body, tableBuffer);
  }

  moveToFolder_(doc.getId());
  doc.saveAndClose();
  return doc.getUrl();
}

// ============================================================
// Google Slides 생성
// ============================================================
function createGoogleSlides_() {
  const markdown = DriveApp.getFileById(DRIVE_FILE_IDS.slides).getBlob().getDataAsString('UTF-8');
  const presentation = SlidesApp.create('리서치 보고서');

  // 기본 슬라이드 삭제
  const defaultSlide = presentation.getSlides()[0];

  // 슬라이드별 분리
  const sections = parseSlides_(markdown);

  sections.forEach(function(section, idx) {
    buildSlide_(presentation, section, idx);
  });

  // 기본 슬라이드 삭제
  if (presentation.getSlides().length > 1) {
    defaultSlide.remove();
  }

  moveToFolder_(presentation.getId());
  presentation.saveAndClose();
  return presentation.getUrl();
}

function parseSlides_(md) {
  const sections = [];
  const parts = md.split(/(?=## 슬라이드 \d+:)/);

  parts.forEach(function(part) {
    part = part.trim();
    if (!part || !part.startsWith('## 슬라이드')) return;

    var titleMatch = part.match(/## 슬라이드 \d+:\s*(.+)/);
    var title = titleMatch ? cleanMd_(titleMatch[1]) : '';

    // 발표자 노트
    var noteMatch = part.match(/> \*\*발표자 노트\*\*:\s*([\s\S]*?)(?=\n---|\n## |$)/);
    var note = noteMatch ? cleanMd_(noteMatch[1].trim()) : '';

    // 본문
    var bodyText = part
      .replace(/## 슬라이드 \d+:.+\n?/, '')
      .replace(/> \*\*발표자 노트\*\*:[\s\S]*?(?=\n---|\n## |$)/, '')
      .replace(/\n---\n?/g, '')
      .trim();

    sections.push({ title: title, body: bodyText, note: note });
  });

  return sections;
}

function buildSlide_(pres, section, idx) {
  var slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  var W = 720, H = 405;

  if (idx === 0) {
    // 표지
    slide.getBackground().setSolidFill(THEME.PRIMARY);

    var tb1 = slide.insertTextBox('리서치 보고서', 60, H/2 - 60, W - 120, 50);
    tb1.getText().getTextStyle().setFontSize(32).setBold(true).setForegroundColor(THEME.TEXT_LIGHT);

    var tb2 = slide.insertTextBox('팩트시트 → 가설 수립 → 데이터 수집 → 인사이트 도출', 60, H/2, W - 120, 30);
    tb2.getText().getTextStyle().setFontSize(14).setForegroundColor(THEME.HIGHLIGHT);

    var tb3 = slide.insertTextBox('Research Orchestrator', 60, H/2 + 40, W - 120, 25);
    tb3.getText().getTextStyle().setFontSize(11).setForegroundColor(THEME.TEXT_GRAY);
  } else {
    // 일반 슬라이드
    slide.getBackground().setSolidFill(THEME.BG);

    // 상단 바
    var bar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, W, 4);
    bar.getFill().setSolidFill(THEME.HIGHLIGHT);
    bar.getBorder().setTransparent();

    // 제목
    var titleBox = slide.insertTextBox(section.title, 40, 15, W - 80, 45);
    titleBox.getText().getTextStyle().setFontSize(16).setBold(true).setForegroundColor(THEME.PRIMARY);

    // 본문
    var bodyClean = convertBodyForSlide_(section.body);
    if (bodyClean) {
      var bodyBox = slide.insertTextBox(bodyClean, 40, 65, W - 80, H - 100);
      bodyBox.getText().getTextStyle().setFontSize(10).setForegroundColor(THEME.TEXT);
    }

    // 슬라이드 번호
    var numBox = slide.insertTextBox(String(idx + 1), W - 45, H - 25, 30, 18);
    numBox.getText().getTextStyle().setFontSize(8).setForegroundColor(THEME.TEXT_GRAY);
  }

  // 발표자 노트
  if (section.note) {
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(section.note);
  }
}

function convertBodyForSlide_(body) {
  var text = body;
  // 테이블 → 텍스트
  text = text.replace(/(\|.+\|(\n\|[-:\s|]+\|)?\n(\|.+\|\n?)+)/g, function(match) {
    return tableToText_(match);
  });
  // 마크다운 정리
  text = cleanMd_(text);
  text = text.replace(/^- /gm, '• ');
  text = text.replace(/^#{1,4}\s/gm, '');
  text = text.replace(/```[\s\S]*?```/g, function(m) { return m.replace(/```\w*\n?/g, '').trim(); });
  text = text.replace(/\n{3,}/g, '\n\n');
  return text.trim();
}

function tableToText_(tableMd) {
  var lines = tableMd.trim().split('\n');
  var dataLines = lines.filter(function(l) {
    return l.replace(/\|/g, '').trim().replace(/[-:\s]/g, '') !== '';
  });
  var rows = dataLines.map(function(l) {
    return l.split('|').filter(function(_, i, a) { return i > 0 && i < a.length - 1; }).map(function(c) { return cleanMd_(c.trim()); });
  });
  if (rows.length === 0) return '';
  return rows.map(function(r) { return r.join('  |  '); }).join('\n');
}

// ============================================================
// 공통 헬퍼
// ============================================================
function appendHeading_(body, text, type, size, color) {
  var p = body.appendParagraph(text);
  p.setHeading(type);
  p.setFontSize(size);
  p.setBold(true);
  p.setForegroundColor(color);
  p.setSpacingBefore(14);
  p.setSpacingAfter(6);
}

function appendTable_(body, lines) {
  if (lines.length === 0) return;
  var rows = lines.map(function(l) {
    return l.split('|').filter(function(_, i, a) { return i > 0 && i < a.length - 1; }).map(function(c) { return cleanMd_(c.trim()); });
  });
  if (rows.length === 0) return;

  var nCols = rows[0].length;
  var table = body.appendTable();

  for (var r = 0; r < rows.length; r++) {
    var tr = (r === 0) ? table.getRow(0) : table.appendTableRow();
    for (var c = 0; c < nCols; c++) {
      var cellText = rows[r][c] || '';
      var cell;
      if (r === 0 && c === 0) {
        cell = tr.getCell(0);
        cell.setText(cellText);
      } else if (r === 0) {
        cell = tr.appendTableCell(cellText);
      } else if (c === 0) {
        cell = tr.getCell(0);
        cell.setText(cellText);
      } else {
        cell = tr.appendTableCell(cellText);
      }

      var cp = cell.getChild(0).asParagraph();
      cp.setFontSize(9);
      if (r === 0) {
        cp.setBold(true);
        cell.setBackgroundColor(THEME.PRIMARY);
        cp.setForegroundColor(THEME.TEXT_LIGHT);
      } else if (r % 2 === 0) {
        cell.setBackgroundColor(THEME.LIGHT_GRAY);
      }
    }
  }
  body.appendParagraph('');
}

function appendCodeBlock_(body, code) {
  var p = body.appendParagraph(code);
  p.setFontFamily('Courier New');
  p.setFontSize(8);
  p.setForegroundColor(THEME.TEXT);
  p.setBackgroundColor(THEME.LIGHT_GRAY);
  p.setIndentStart(18);
  p.setSpacingBefore(6);
  p.setSpacingAfter(6);
}

/** 마크다운 서식 제거 */
function cleanMd_(text) {
  return text.replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1').replace(/`([^`]+)`/g, '$1').trim();
}

/** 볼드 부분에 실제 볼드 적용 */
function applyBold_(element, rawText) {
  var regex = /\*\*(.+?)\*\*/g;
  var match;
  var currentText = element.getText ? element.getText() : element.editAsText().getText();
  while ((match = regex.exec(rawText)) !== null) {
    var boldContent = match[1];
    var idx = currentText.indexOf(boldContent);
    if (idx >= 0) {
      try {
        element.editAsText().setBold(idx, idx + boldContent.length - 1, true);
      } catch(e) {}
    }
  }
}

/** 생성된 파일을 지정 폴더로 이동 */
function moveToFolder_(fileId) {
  if (!OUTPUT_FOLDER_ID) return;
  var file = DriveApp.getFileById(fileId);
  var folder = DriveApp.getFolderById(OUTPUT_FOLDER_ID);
  folder.addFile(file);
  DriveApp.getRootFolder().removeFile(file);
}
