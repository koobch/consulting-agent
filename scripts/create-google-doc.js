/**
 * Google Docs 보고서 생성 Apps Script
 *
 * 사용법:
 * 1. Google Apps Script (script.google.com)에서 새 프로젝트 생성
 * 2. 이 코드를 붙여넣기
 * 3. createReportFromMarkdown() 함수 실행
 * 4. 또는 웹앱으로 배포하여 API 형태로 호출
 *
 * 마크다운 입력 → Google Docs 보고서 생성
 */

// ===== 설정 =====
const CONFIG = {
  outputFolderId: '', // Google Drive 폴더 ID (빈 값이면 루트에 생성)
  defaultFontFamily: 'Noto Sans KR', // 기본 폰트
  titleFontSize: 24,
  heading1FontSize: 18,
  heading2FontSize: 14,
  heading3FontSize: 12,
  bodyFontSize: 10,
  primaryColor: '#1a1a2e', // 제목 색상
  accentColor: '#16213e',  // 강조 색상
};

/**
 * 마크다운 텍스트를 Google Docs로 변환
 * @param {string} markdownText - 마크다운 형식의 보고서 텍스트
 * @param {string} title - 문서 제목
 * @returns {string} 생성된 Google Docs URL
 */
function createReportFromMarkdown(markdownText, title) {
  // 문서 생성
  const doc = DocumentApp.create(title || '리서치 보고서');
  const body = doc.getBody();

  // 기본 스타일 설정
  const defaultStyle = {};
  defaultStyle[DocumentApp.Attribute.FONT_FAMILY] = CONFIG.defaultFontFamily;
  defaultStyle[DocumentApp.Attribute.FONT_SIZE] = CONFIG.bodyFontSize;
  body.setAttributes(defaultStyle);

  // 마크다운 파싱 및 변환
  const lines = markdownText.split('\n');
  let inTable = false;
  let tableData = [];
  let inCodeBlock = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // 코드 블록 처리
    if (line.trim().startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      if (inCodeBlock) {
        // 코드 블록 시작
        continue;
      } else {
        // 코드 블록 끝
        continue;
      }
    }

    if (inCodeBlock) {
      const codePara = body.appendParagraph(line);
      codePara.setFontFamily('Roboto Mono');
      codePara.setFontSize(9);
      codePara.setBackgroundColor('#f5f5f5');
      continue;
    }

    // 테이블 처리
    if (line.trim().startsWith('|')) {
      if (!inTable) {
        inTable = true;
        tableData = [];
      }
      // 구분선 무시
      if (line.trim().match(/^\|[\s\-:|]+\|$/)) continue;

      const cells = line.split('|').filter((c, idx, arr) => idx > 0 && idx < arr.length - 1).map(c => c.trim());
      tableData.push(cells);
      continue;
    } else if (inTable) {
      // 테이블 종료 → 테이블 삽입
      insertTable(body, tableData);
      inTable = false;
      tableData = [];
    }

    // 빈 줄
    if (line.trim() === '') {
      continue;
    }

    // 수평선
    if (line.trim() === '---' || line.trim() === '***') {
      body.appendHorizontalRule();
      continue;
    }

    // 제목 (Heading) 처리
    if (line.startsWith('# ')) {
      const heading = body.appendParagraph(line.substring(2));
      heading.setHeading(DocumentApp.ParagraphHeading.HEADING1);
      heading.setFontSize(CONFIG.titleFontSize);
      heading.setForegroundColor(CONFIG.primaryColor);
      heading.setBold(true);
      continue;
    }
    if (line.startsWith('## ')) {
      const heading = body.appendParagraph(line.substring(3));
      heading.setHeading(DocumentApp.ParagraphHeading.HEADING2);
      heading.setFontSize(CONFIG.heading1FontSize);
      heading.setForegroundColor(CONFIG.primaryColor);
      heading.setBold(true);
      continue;
    }
    if (line.startsWith('### ')) {
      const heading = body.appendParagraph(line.substring(4));
      heading.setHeading(DocumentApp.ParagraphHeading.HEADING3);
      heading.setFontSize(CONFIG.heading2FontSize);
      heading.setForegroundColor(CONFIG.accentColor);
      heading.setBold(true);
      continue;
    }
    if (line.startsWith('#### ')) {
      const heading = body.appendParagraph(line.substring(5));
      heading.setHeading(DocumentApp.ParagraphHeading.HEADING4);
      heading.setFontSize(CONFIG.heading3FontSize);
      heading.setBold(true);
      continue;
    }

    // 불릿 리스트
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const indent = line.search(/\S/);
      const nestingLevel = Math.floor(indent / 2);
      const text = line.trim().substring(2);
      const listItem = body.appendListItem(applyInlineFormatting(body, text));
      listItem.setGlyphType(DocumentApp.GlyphType.BULLET);
      listItem.setNestingLevel(nestingLevel);
      listItem.setFontSize(CONFIG.bodyFontSize);
      continue;
    }

    // 숫자 리스트
    const numberedMatch = line.trim().match(/^(\d+)\.\s(.+)/);
    if (numberedMatch) {
      const text = numberedMatch[2];
      const listItem = body.appendListItem(applyInlineFormatting(body, text));
      listItem.setGlyphType(DocumentApp.GlyphType.NUMBER);
      listItem.setFontSize(CONFIG.bodyFontSize);
      continue;
    }

    // 인용문
    if (line.trim().startsWith('> ')) {
      const text = line.trim().substring(2);
      const quote = body.appendParagraph(text);
      quote.setIndentStart(36);
      quote.setForegroundColor('#666666');
      quote.setItalic(true);
      quote.setFontSize(CONFIG.bodyFontSize);
      continue;
    }

    // 일반 텍스트
    const para = body.appendParagraph(line);
    para.setFontSize(CONFIG.bodyFontSize);
    applyInlineFormattingToParagraph(para, line);
  }

  // 마지막 테이블 처리
  if (inTable && tableData.length > 0) {
    insertTable(body, tableData);
  }

  // 폴더에 이동 (설정된 경우)
  if (CONFIG.outputFolderId) {
    const file = DriveApp.getFileById(doc.getId());
    const folder = DriveApp.getFolderById(CONFIG.outputFolderId);
    folder.addFile(file);
    DriveApp.getRootFolder().removeFile(file);
  }

  doc.saveAndClose();
  return doc.getUrl();
}

/**
 * 테이블 삽입
 */
function insertTable(body, tableData) {
  if (tableData.length === 0) return;

  const numRows = tableData.length;
  const numCols = tableData[0].length;

  const table = body.appendTable();

  for (let r = 0; r < numRows; r++) {
    const row = (r === 0) ? table.getRow(0) || table.appendTableRow() : table.appendTableRow();
    for (let c = 0; c < numCols; c++) {
      const cellText = (tableData[r][c] || '').trim();
      let cell;
      if (r === 0 && c === 0) {
        cell = row.getCell(0);
        cell.setText(cellText);
      } else if (r === 0) {
        cell = row.appendTableCell(cellText);
      } else if (c === 0) {
        cell = row.getCell(0) || row.appendTableCell(cellText);
        if (row.getNumCells() === 0) {
          cell = row.appendTableCell(cellText);
        } else {
          cell.setText(cellText);
        }
      } else {
        cell = row.appendTableCell(cellText);
      }

      // 헤더 행 스타일
      if (r === 0) {
        cell.setBackgroundColor('#1a1a2e');
        cell.editAsText().setForegroundColor('#ffffff').setBold(true).setFontSize(9);
      } else {
        cell.editAsText().setFontSize(9);
        if (r % 2 === 0) {
          cell.setBackgroundColor('#f8f9fa');
        }
      }
    }
  }

  body.appendParagraph(''); // 테이블 후 빈 줄
}

/**
 * 인라인 포매팅 (굵게, 기울임 등)
 */
function applyInlineFormatting(body, text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1');
}

function applyInlineFormattingToParagraph(para, text) {
  // 볼드 처리
  const boldRegex = /\*\*(.+?)\*\*/g;
  let match;
  while ((match = boldRegex.exec(text)) !== null) {
    const startIndex = text.indexOf(match[0]);
    const boldText = match[1];
    // 간략화된 볼드 적용 (전체 텍스트에서 볼드 부분 찾기)
    const paraText = para.getText();
    const boldIdx = paraText.indexOf(boldText);
    if (boldIdx >= 0) {
      para.editAsText().setBold(boldIdx, boldIdx + boldText.length - 1, true);
    }
  }
}

/**
 * 웹앱 엔드포인트 (POST 요청으로 외부에서 호출 가능)
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const url = createReportFromMarkdown(data.markdown, data.title);
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
function testCreateReport() {
  const sampleMarkdown = `# 테스트 보고서

## Executive Summary
이것은 테스트 보고서입니다.

## 1. 시장 분석
### 1.1 시장 규모
- 글로벌 시장: **$200B**
- 국내 시장: **22조원**

| 지역 | 시장 규모 | 성장률 |
|------|----------|--------|
| 글로벌 | $200B | 5% |
| 한국 | 22조원 | 8% |
| 중국 | $50B | 3% |

### 1.2 트렌드
1. AI 기술 접목 확대
2. 크로스플랫폼 전환
3. 라이브서비스 강화
`;

  const url = createReportFromMarkdown(sampleMarkdown, '테스트 리서치 보고서');
  Logger.log('생성된 문서 URL: ' + url);
}
