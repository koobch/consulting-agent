/**
 * 마크다운 → Google Slides 변환 스크립트
 *
 * 사용법:
 * 1. Google Drive에서 새 Google Apps Script 프로젝트 생성 (script.google.com)
 * 2. 이 코드를 붙여넣기
 * 3. convertMarkdownToSlides() 함수 실행
 * 4. 최초 실행 시 Google Slides 권한 승인 필요
 */

// ========== 설정 ==========
const SLIDE_CONFIG = {
  OUTPUT_FOLDER_ID: '', // 빈 값이면 My Drive 루트에 생성
  PRESENTATION_TITLE: '리서치 보고서',

  // 색상 테마
  THEME: {
    PRIMARY: '#1a1a2e',      // 다크 네이비
    SECONDARY: '#16213e',    // 네이비
    ACCENT: '#e94560',       // 레드 액센트
    TEXT_DARK: '#1a1a2e',
    TEXT_LIGHT: '#ffffff',
    TEXT_GRAY: '#666666',
    BG_WHITE: '#ffffff',
    BG_LIGHT: '#f8f9fa',
  }
};

/**
 * 메인 실행 함수 — Google Slides 생성
 */
function convertMarkdownToSlides() {
  const markdown = getSlideMarkdownContent_();
  if (!markdown) {
    Logger.log('마크다운 콘텐츠가 없습니다.');
    return;
  }

  // 프레젠테이션 생성
  const presentation = SlidesApp.create(SLIDE_CONFIG.PRESENTATION_TITLE);

  // 기본 빈 슬라이드 삭제
  const defaultSlide = presentation.getSlides()[0];

  // 슬라이드 섹션 파싱 (## 슬라이드 N: 으로 분리)
  const sections = parseSlides_(markdown);

  sections.forEach((section, index) => {
    createSlide_(presentation, section, index);
  });

  // 기본 슬라이드 삭제
  if (presentation.getSlides().length > 1) {
    defaultSlide.remove();
  }

  // 폴더 이동
  if (SLIDE_CONFIG.OUTPUT_FOLDER_ID) {
    const file = DriveApp.getFileById(presentation.getId());
    const folder = DriveApp.getFolderById(SLIDE_CONFIG.OUTPUT_FOLDER_ID);
    folder.addFile(file);
    DriveApp.getRootFolder().removeFile(file);
  }

  presentation.saveAndClose();

  Logger.log('✅ Google Slides 생성 완료!');
  Logger.log('🎯 프레젠테이션 URL: ' + presentation.getUrl());
  Logger.log('📁 프레젠테이션 ID: ' + presentation.getId());

  return presentation.getUrl();
}

/**
 * 마크다운을 슬라이드 섹션으로 분리
 */
function parseSlides_(markdown) {
  const sections = [];
  const parts = markdown.split(/(?=## 슬라이드 \d+:)/);

  parts.forEach(part => {
    part = part.trim();
    if (!part || !part.startsWith('## 슬라이드')) return;

    // 타이틀 추출
    const titleMatch = part.match(/## 슬라이드 \d+:\s*(.+)/);
    const title = titleMatch ? titleMatch[1].trim() : '';

    // 발표자 노트 추출
    const noteMatch = part.match(/> \*\*발표자 노트\*\*:\s*([\s\S]*?)(?=\n---|\n## |$)/);
    const speakerNote = noteMatch ? noteMatch[1].trim() : '';

    // 본문 추출 (타이틀 줄 이후, 발표자 노트 이전)
    let bodyText = part;
    // 타이틀 줄 제거
    bodyText = bodyText.replace(/## 슬라이드 \d+:.+\n?/, '');
    // 발표자 노트 제거
    bodyText = bodyText.replace(/> \*\*발표자 노트\*\*:[\s\S]*?(?=\n---|\n## |$)/, '');
    // 구분선 제거
    bodyText = bodyText.replace(/\n---\n?/g, '');
    bodyText = bodyText.trim();

    sections.push({
      title: cleanMarkdown_(title),
      body: bodyText,
      speakerNote: cleanMarkdown_(speakerNote)
    });
  });

  return sections;
}

/**
 * 개별 슬라이드 생성
 */
function createSlide_(presentation, section, index) {
  const slide = presentation.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  const theme = SLIDE_CONFIG.THEME;
  const pageWidth = 720; // 포인트 (10인치 * 72)
  const pageHeight = 405; // 포인트 (5.625인치 * 72)

  // 배경색 설정
  slide.getBackground().setSolidFill(theme.BG_WHITE);

  // 상단 컬러 바
  const topBar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 4);
  topBar.getFill().setSolidFill(theme.ACCENT);
  topBar.getBorder().setTransparent();

  // 슬라이드 번호
  const pageNum = slide.insertTextBox(
    String(index + 1),
    pageWidth - 50, pageHeight - 30, 40, 20
  );
  pageNum.getText().getTextStyle()
    .setFontSize(9)
    .setForegroundColor(theme.TEXT_GRAY);

  if (index === 0) {
    // ===== 표지 슬라이드 =====
    createTitleSlide_(slide, section, theme, pageWidth, pageHeight);
  } else {
    // ===== 콘텐츠 슬라이드 =====
    createContentSlide_(slide, section, theme, pageWidth, pageHeight);
  }

  // 발표자 노트 추가
  if (section.speakerNote) {
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(section.speakerNote);
  }
}

/**
 * 표지 슬라이드 생성
 */
function createTitleSlide_(slide, section, theme, pageWidth, pageHeight) {
  // 배경을 다크 네이비로
  slide.getBackground().setSolidFill(theme.PRIMARY);

  // 메인 타이틀
  const titleBox = slide.insertTextBox(
    SLIDE_CONFIG.PRESENTATION_TITLE,
    60, pageHeight / 2 - 60, pageWidth - 120, 60
  );
  titleBox.getText().getTextStyle()
    .setFontSize(36)
    .setBold(true)
    .setForegroundColor(theme.TEXT_LIGHT);

  // 서브타이틀
  const subtitleText = '팩트시트 → 가설 수립 → 데이터 수집 → 인사이트 도출';
  const subtitleBox = slide.insertTextBox(
    subtitleText,
    60, pageHeight / 2 + 10, pageWidth - 120, 30
  );
  subtitleBox.getText().getTextStyle()
    .setFontSize(16)
    .setForegroundColor(theme.ACCENT);

  // 날짜/팀
  const infoBox = slide.insertTextBox(
    'Research Orchestrator',
    60, pageHeight / 2 + 50, pageWidth - 120, 25
  );
  infoBox.getText().getTextStyle()
    .setFontSize(12)
    .setForegroundColor(theme.TEXT_GRAY);
}

/**
 * 콘텐츠 슬라이드 생성
 */
function createContentSlide_(slide, section, theme, pageWidth, pageHeight) {
  // 타이틀
  const titleBox = slide.insertTextBox(
    section.title,
    40, 20, pageWidth - 80, 45
  );
  titleBox.getText().getTextStyle()
    .setFontSize(18)
    .setBold(true)
    .setForegroundColor(theme.PRIMARY);

  // 본문 — 테이블 감지 및 텍스트 변환
  const bodyContent = convertBodyToSlideText_(section.body);

  const bodyBox = slide.insertTextBox(
    bodyContent,
    40, 75, pageWidth - 80, pageHeight - 110
  );
  bodyBox.getText().getTextStyle()
    .setFontSize(11)
    .setForegroundColor(theme.TEXT_DARK);

  // "So What" 강조 처리
  highlightKeyPhrases_(bodyBox, theme);
}

/**
 * 마크다운 본문을 슬라이드용 텍스트로 변환
 */
function convertBodyToSlideText_(body) {
  let text = body;

  // 마크다운 테이블을 정렬된 텍스트로 변환
  text = text.replace(/(\|.+\|(\n\|[-:\s|]+\|)?\n(\|.+\|\n?)+)/g, (match) => {
    return convertTableToText_(match);
  });

  // 마크다운 포맷 정리
  text = text.replace(/\*\*([^*]+)\*\*/g, '$1'); // 볼드
  text = text.replace(/\*([^*]+)\*/g, '$1');       // 이탈릭
  text = text.replace(/^- /gm, '• ');              // 불릿
  text = text.replace(/^#{1,4}\s/gm, '');          // 하위 헤딩
  text = text.replace(/```[\s\S]*?```/g, (match) => {
    return match.replace(/```\w*\n?/g, '').trim();  // 코드 블록
  });

  // 연속 빈 줄 제거
  text = text.replace(/\n{3,}/g, '\n\n');

  return text.trim();
}

/**
 * 마크다운 테이블을 텍스트 정렬로 변환
 */
function convertTableToText_(tableMarkdown) {
  const lines = tableMarkdown.trim().split('\n');
  const dataLines = lines.filter(line => {
    const stripped = line.replace(/\|/g, '').trim();
    return stripped.replace(/[-:\s]/g, '') !== '';
  });

  const rows = dataLines.map(line => {
    return line.split('|')
      .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
      .map(cell => cell.trim().replace(/\*\*/g, ''));
  });

  if (rows.length === 0) return '';

  // 각 컬럼 최대 너비 계산
  const colWidths = [];
  rows.forEach(row => {
    row.forEach((cell, idx) => {
      // 한글 너비 보정 (한글은 약 2자 폭)
      const width = getDisplayWidth_(cell);
      colWidths[idx] = Math.max(colWidths[idx] || 0, width);
    });
  });

  // 정렬된 텍스트 생성
  const result = rows.map((row, rowIdx) => {
    const paddedCells = row.map((cell, colIdx) => {
      return padToWidth_(cell, colWidths[colIdx]);
    });
    return paddedCells.join('  ');
  });

  return result.join('\n');
}

/**
 * 문자열 표시 너비 (한글=2, 영문=1)
 */
function getDisplayWidth_(str) {
  let width = 0;
  for (let i = 0; i < str.length; i++) {
    const code = str.charCodeAt(i);
    width += (code > 0x7F) ? 2 : 1;
  }
  return width;
}

/**
 * 목표 너비로 패딩
 */
function padToWidth_(str, targetWidth) {
  const currentWidth = getDisplayWidth_(str);
  const padding = Math.max(0, targetWidth - currentWidth);
  return str + ' '.repeat(padding);
}

/**
 * 키 프레이즈 강조 (So What, Now What 등)
 */
function highlightKeyPhrases_(textBox, theme) {
  const text = textBox.getText();
  const content = text.asString();

  const keywords = ['So What', 'Now What', '핵심', '추천', '결론'];
  keywords.forEach(keyword => {
    let startIndex = 0;
    while (true) {
      const idx = content.indexOf(keyword, startIndex);
      if (idx === -1) break;
      try {
        text.getRange(idx, idx + keyword.length)
          .getTextStyle()
          .setBold(true)
          .setForegroundColor(theme.ACCENT);
      } catch (e) {
        // 범위 초과 시 무시
      }
      startIndex = idx + keyword.length;
    }
  });
}

/**
 * 마크다운 서식 제거
 */
function cleanMarkdown_(text) {
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .trim();
}

/**
 * 마크다운 콘텐츠 가져오기
 */
function getSlideMarkdownContent_() {
  // Google Drive 파일에서 가져오기
  if (SLIDE_CONFIG.SOURCE_FILE_ID) {
    const file = DriveApp.getFileById(SLIDE_CONFIG.SOURCE_FILE_ID);
    return file.getBlob().getDataAsString();
  }
  return SLIDE_MARKDOWN_CONTENT || '';
}


// ========== 마크다운 콘텐츠 (inline 모드용) ==========
// report-slides.md 내용을 아래에 붙여넣으세요
const SLIDE_MARKDOWN_CONTENT = `
여기에 report-slides.md 내용을 붙여넣으세요
`;
