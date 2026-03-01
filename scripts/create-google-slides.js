/**
 * Google Slides 보고서 생성 Apps Script
 *
 * 사용법:
 * 1. Google Apps Script (script.google.com)에서 새 프로젝트 생성
 * 2. 이 코드를 붙여넣기
 * 3. createSlidesFromMarkdown() 함수 실행
 * 4. 또는 웹앱으로 배포하여 API 형태로 호출
 *
 * 슬라이드 마크다운 입력 → Google Slides 프레젠테이션 생성
 */

// ===== 설정 =====
const SLIDE_CONFIG = {
  outputFolderId: '', // Google Drive 폴더 ID
  // 컬러 팔레트 (컨설팅 보고서 스타일)
  colors: {
    primary: '#1a1a2e',     // 진한 네이비
    secondary: '#16213e',   // 네이비
    accent: '#0f3460',      // 블루
    highlight: '#e94560',   // 레드 (강조)
    background: '#ffffff',  // 화이트
    lightGray: '#f8f9fa',   // 연한 회색
    darkText: '#1a1a2e',    // 텍스트
    lightText: '#ffffff',   // 밝은 텍스트
    subtleText: '#6c757d',  // 서브 텍스트
  },
  fonts: {
    title: 'Noto Sans KR',
    body: 'Noto Sans KR',
    code: 'Roboto Mono',
  }
};

/**
 * 슬라이드 마크다운을 Google Slides로 변환
 * @param {string} markdownText - 슬라이드 마크다운 (---로 구분)
 * @param {string} title - 프레젠테이션 제목
 * @returns {string} 생성된 Google Slides URL
 */
function createSlidesFromMarkdown(markdownText, title) {
  const presentation = SlidesApp.create(title || '리서치 보고서');
  const slides = presentation.getSlides();

  // 기본 빈 슬라이드 삭제
  if (slides.length > 0) {
    slides[0].remove();
  }

  // 마크다운을 슬라이드별로 분리
  const slideBlocks = markdownText.split(/\n---\n/).filter(s => s.trim());

  slideBlocks.forEach((block, index) => {
    const slideContent = parseSlideBlock(block.trim());
    createSlide(presentation, slideContent, index);
  });

  // 폴더에 이동
  if (SLIDE_CONFIG.outputFolderId) {
    const file = DriveApp.getFileById(presentation.getId());
    const folder = DriveApp.getFolderById(SLIDE_CONFIG.outputFolderId);
    folder.addFile(file);
    DriveApp.getRootFolder().removeFile(file);
  }

  presentation.saveAndClose();
  return presentation.getUrl();
}

/**
 * 슬라이드 블록 파싱
 */
function parseSlideBlock(block) {
  const lines = block.split('\n');
  const result = {
    title: '',
    layout: 'title_body', // 기본 레이아웃
    content: [],
    speakerNotes: '',
    table: null,
  };

  let inTable = false;
  let tableData = [];

  for (const line of lines) {
    // 제목 추출
    if (line.startsWith('## ')) {
      result.title = line.substring(3).trim();
      continue;
    }

    // 레이아웃 지시
    if (line.startsWith('**레이아웃**:') || line.startsWith('**레이아웃**：')) {
      result.layout = line.split(':').slice(1).join(':').trim().replace(/\*/g, '');
      continue;
    }

    // 발표자 노트
    if (line.startsWith('> 발표자 노트:') || line.startsWith('> 발표자 노트：')) {
      result.speakerNotes = line.substring(line.indexOf(':') + 1).trim();
      continue;
    }

    // 테이블 처리
    if (line.trim().startsWith('|')) {
      if (!inTable) {
        inTable = true;
        tableData = [];
      }
      if (line.trim().match(/^\|[\s\-:|]+\|$/)) continue;
      const cells = line.split('|').filter((c, idx, arr) => idx > 0 && idx < arr.length - 1).map(c => c.trim());
      tableData.push(cells);
      continue;
    } else if (inTable) {
      result.table = tableData;
      inTable = false;
      tableData = [];
    }

    // 일반 콘텐츠
    if (line.trim()) {
      result.content.push(line);
    }
  }

  if (inTable && tableData.length > 0) {
    result.table = tableData;
  }

  return result;
}

/**
 * 슬라이드 생성
 */
function createSlide(presentation, slideContent, index) {
  let slide;

  if (index === 0) {
    // 표지 슬라이드
    slide = presentation.appendSlide(SlidesApp.PredefinedLayout.TITLE);
    setupCoverSlide(slide, slideContent);
  } else if (slideContent.table) {
    // 테이블 포함 슬라이드
    slide = presentation.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    setupTableSlide(slide, slideContent);
  } else {
    // 일반 콘텐츠 슬라이드
    slide = presentation.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    setupContentSlide(slide, slideContent);
  }

  // 발표자 노트 추가
  if (slideContent.speakerNotes) {
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(slideContent.speakerNotes);
  }
}

/**
 * 표지 슬라이드 설정
 */
function setupCoverSlide(slide, content) {
  slide.getBackground().setSolidFill(SLIDE_CONFIG.colors.primary);

  // 제목
  const titleShape = slide.insertTextBox(content.title);
  titleShape.setLeft(50);
  titleShape.setTop(150);
  titleShape.setWidth(620);
  titleShape.setHeight(80);
  const titleText = titleShape.getText();
  titleText.getTextStyle()
    .setFontFamily(SLIDE_CONFIG.fonts.title)
    .setFontSize(32)
    .setForegroundColor(SLIDE_CONFIG.colors.lightText)
    .setBold(true);

  // 부제 (content의 첫 줄)
  if (content.content.length > 0) {
    const subtitleShape = slide.insertTextBox(content.content.join('\n'));
    subtitleShape.setLeft(50);
    subtitleShape.setTop(250);
    subtitleShape.setWidth(620);
    subtitleShape.setHeight(50);
    subtitleShape.getText().getTextStyle()
      .setFontFamily(SLIDE_CONFIG.fonts.body)
      .setFontSize(14)
      .setForegroundColor(SLIDE_CONFIG.colors.subtleText);
  }
}

/**
 * 콘텐츠 슬라이드 설정
 */
function setupContentSlide(slide, content) {
  slide.getBackground().setSolidFill(SLIDE_CONFIG.colors.background);

  // 상단 색상 바
  const colorBar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE);
  colorBar.setLeft(0);
  colorBar.setTop(0);
  colorBar.setWidth(720);
  colorBar.setHeight(6);
  colorBar.getFill().setSolidFill(SLIDE_CONFIG.colors.accent);
  colorBar.getBorder().setTransparent();

  // 서술형 제목
  const titleShape = slide.insertTextBox(content.title);
  titleShape.setLeft(40);
  titleShape.setTop(20);
  titleShape.setWidth(640);
  titleShape.setHeight(50);
  titleShape.getText().getTextStyle()
    .setFontFamily(SLIDE_CONFIG.fonts.title)
    .setFontSize(20)
    .setForegroundColor(SLIDE_CONFIG.colors.primary)
    .setBold(true);

  // 본문 콘텐츠
  if (content.content.length > 0) {
    const bodyText = content.content.map(line => {
      // 불릿 포인트 변환
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return '  ' + line.trim();
      }
      return line;
    }).join('\n');

    const bodyShape = slide.insertTextBox(bodyText);
    bodyShape.setLeft(40);
    bodyShape.setTop(80);
    bodyShape.setWidth(640);
    bodyShape.setHeight(300);
    bodyShape.getText().getTextStyle()
      .setFontFamily(SLIDE_CONFIG.fonts.body)
      .setFontSize(14)
      .setForegroundColor(SLIDE_CONFIG.colors.darkText);

    // 볼드 텍스트 처리
    applyBoldFormatting(bodyShape.getText(), bodyText);
  }
}

/**
 * 테이블 슬라이드 설정
 */
function setupTableSlide(slide, content) {
  slide.getBackground().setSolidFill(SLIDE_CONFIG.colors.background);

  // 상단 색상 바
  const colorBar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE);
  colorBar.setLeft(0);
  colorBar.setTop(0);
  colorBar.setWidth(720);
  colorBar.setHeight(6);
  colorBar.getFill().setSolidFill(SLIDE_CONFIG.colors.accent);
  colorBar.getBorder().setTransparent();

  // 제목
  const titleShape = slide.insertTextBox(content.title);
  titleShape.setLeft(40);
  titleShape.setTop(20);
  titleShape.setWidth(640);
  titleShape.setHeight(50);
  titleShape.getText().getTextStyle()
    .setFontFamily(SLIDE_CONFIG.fonts.title)
    .setFontSize(20)
    .setForegroundColor(SLIDE_CONFIG.colors.primary)
    .setBold(true);

  // 테이블 삽입
  if (content.table && content.table.length > 0) {
    const numRows = content.table.length;
    const numCols = content.table[0].length;
    const table = slide.insertTable(numRows, numCols);

    // 테이블 위치 및 크기
    table.setLeft(40);
    table.setTop(85);
    table.setWidth(640);

    for (let r = 0; r < numRows; r++) {
      for (let c = 0; c < numCols; c++) {
        const cell = table.getCell(r, c);
        cell.getText().setText(content.table[r][c] || '');
        cell.getText().getTextStyle()
          .setFontFamily(SLIDE_CONFIG.fonts.body)
          .setFontSize(10);

        if (r === 0) {
          // 헤더 행
          cell.getFill().setSolidFill(SLIDE_CONFIG.colors.primary);
          cell.getText().getTextStyle()
            .setForegroundColor(SLIDE_CONFIG.colors.lightText)
            .setBold(true)
            .setFontSize(10);
        } else if (r % 2 === 0) {
          cell.getFill().setSolidFill(SLIDE_CONFIG.colors.lightGray);
        }
      }
    }
  }

  // 테이블 아래 추가 콘텐츠
  if (content.content.length > 0) {
    const bodyShape = slide.insertTextBox(content.content.join('\n'));
    bodyShape.setLeft(40);
    bodyShape.setTop(350);
    bodyShape.setWidth(640);
    bodyShape.setHeight(100);
    bodyShape.getText().getTextStyle()
      .setFontFamily(SLIDE_CONFIG.fonts.body)
      .setFontSize(11)
      .setForegroundColor(SLIDE_CONFIG.colors.darkText);
  }
}

/**
 * 볼드 텍스트 포매팅 적용
 */
function applyBoldFormatting(textRange, rawText) {
  const boldRegex = /\*\*(.+?)\*\*/g;
  let match;
  let offset = 0; // ** 마크업 제거에 따른 오프셋

  while ((match = boldRegex.exec(rawText)) !== null) {
    const fullMatch = match[0]; // **text**
    const boldContent = match[1]; // text
    const startInRaw = match.index;
    const adjustedStart = startInRaw - offset;

    // 이 시점에서 텍스트에서 볼드 부분 찾기
    const currentText = textRange.asString();
    const boldIdx = currentText.indexOf(boldContent, Math.max(0, adjustedStart - 10));

    if (boldIdx >= 0) {
      textRange.getRange(boldIdx, boldIdx + boldContent.length).getTextStyle().setBold(true);
    }

    offset += 4; // ** 2개 = 4문자 제거
  }
}

/**
 * 웹앱 엔드포인트
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const url = createSlidesFromMarkdown(data.markdown, data.title);
    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      url: url
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 테스트 함수
 */
function testCreateSlides() {
  const sampleMarkdown = `## 대상 기업 전략 리서치
작성일: 2026.02.25 | 리서치팀

---

## 목차

- 시장 규모 및 성장 전망
- 경쟁 환경 분석
- 고객 분석
- 전략적 시사점

---

## 국내 대상 시장은 2026년 1.2조원 규모, YoY 18% 성장 전망

**레이아웃**: 제목+본문

- 2025년 시장 규모: **1.0조원**
- 2026년 전망: **1.2조원** (YoY +18%)
- 성장 동인: 신규 고객 유입, 하이브리드 수익화 모델

> 발표자 노트: 낮은 진입 장벽과 높은 수익화 효율로 지속 성장 중인 시장

---

## 상위 5개 기업이 매출의 65%를 점유하는 과점 구조

**레이아웃**: 표

| 순위 | 기업명 | 매출 비중 | 비고 |
|------|--------|----------|------|
| 1 | 기업A | 20% | 시장 리더 |
| 2 | 기업B | 18% | 고성장 |
| 3 | 기업C | 12% | 안정적 |
| 4 | 기업D | 8% | 신규 진입 |
| 5 | 기업E | 7% | 니치 시장 |

> 발표자 노트: 상위 과점이지만, 신규 진입 시 빠르게 순위 변동이 일어나는 시장
`;

  const url = createSlidesFromMarkdown(sampleMarkdown, '테스트 슬라이드');
  Logger.log('생성된 슬라이드 URL: ' + url);
}
