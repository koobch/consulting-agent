/**
 * 마크다운 → Google Docs 변환 스크립트
 *
 * 사용법:
 * 1. Google Drive에서 새 Google Apps Script 프로젝트 생성 (script.google.com)
 * 2. 이 코드를 붙여넣기
 * 3. convertMarkdownToDoc() 함수 실행
 * 4. 최초 실행 시 Google Drive 권한 승인 필요
 */

// ========== 설정 ==========
const CONFIG = {
  // 마크다운 내용을 아래 MARKDOWN_CONTENT에 붙여넣거나,
  // Google Drive의 .md 파일 ID를 사용
  SOURCE_MODE: 'inline', // 'inline' 또는 'drive_file'
  DRIVE_FILE_ID: '', // SOURCE_MODE가 'drive_file'일 때 사용

  // 생성될 문서 설정
  OUTPUT_FOLDER_ID: '', // 빈 값이면 My Drive 루트에 생성
  DOC_TITLE: '리서치 보고서',

  // 스타일 설정
  STYLES: {
    H1: { fontSize: 24, bold: true, foregroundColor: '#1a1a2e' },
    H2: { fontSize: 20, bold: true, foregroundColor: '#16213e' },
    H3: { fontSize: 16, bold: true, foregroundColor: '#0f3460' },
    BODY: { fontSize: 11, foregroundColor: '#333333' },
    TABLE_HEADER: { fontSize: 10, bold: true, backgroundColor: '#1a1a2e', foregroundColor: '#ffffff' },
    TABLE_BODY: { fontSize: 10, foregroundColor: '#333333' },
  }
};

/**
 * 메인 실행 함수 — Google Docs 생성
 */
function convertMarkdownToDoc() {
  const markdown = getMarkdownContent_();
  if (!markdown) {
    Logger.log('마크다운 콘텐츠가 없습니다. CONFIG.SOURCE_MODE 설정을 확인하세요.');
    return;
  }

  // 문서 생성
  const doc = DocumentApp.create(CONFIG.DOC_TITLE);
  const body = doc.getBody();

  // 기본 페이지 설정
  body.setMarginTop(72);
  body.setMarginBottom(72);
  body.setMarginLeft(72);
  body.setMarginRight(72);

  // 기본 텍스트 제거
  body.clear();

  // 마크다운 파싱 및 문서 작성
  const lines = markdown.split('\n');
  let i = 0;
  let tableBuffer = [];
  let inTable = false;
  let inCodeBlock = false;
  let codeBuffer = [];

  while (i < lines.length) {
    const line = lines[i];

    // 코드 블록 처리
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // 코드 블록 종료
        appendCodeBlock_(body, codeBuffer.join('\n'));
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        // 코드 블록 시작
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

    // 테이블 처리
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      if (!inTable) {
        inTable = true;
        tableBuffer = [];
      }
      // 구분선(---|---|---) 제외
      if (!/^\|[\s\-:]+\|$/.test(line.trim().replace(/\|/g, '|'))) {
        const isSeparator = line.replace(/\|/g, '').trim().replace(/[-:\s]/g, '') === '';
        if (!isSeparator) {
          tableBuffer.push(line);
        }
      }
      i++;
      continue;
    } else if (inTable) {
      // 테이블 종료
      appendTable_(body, tableBuffer);
      tableBuffer = [];
      inTable = false;
    }

    // 빈 줄
    if (line.trim() === '' || line.trim() === '---') {
      i++;
      continue;
    }

    // 헤딩 처리
    if (line.startsWith('# ')) {
      appendHeading_(body, line.substring(2).trim(), DocumentApp.ParagraphHeading.HEADING1, CONFIG.STYLES.H1);
    } else if (line.startsWith('## ')) {
      appendHeading_(body, line.substring(3).trim(), DocumentApp.ParagraphHeading.HEADING2, CONFIG.STYLES.H2);
    } else if (line.startsWith('### ')) {
      appendHeading_(body, line.substring(4).trim(), DocumentApp.ParagraphHeading.HEADING3, CONFIG.STYLES.H3);
    } else if (line.startsWith('#### ')) {
      appendHeading_(body, line.substring(5).trim(), DocumentApp.ParagraphHeading.HEADING4, CONFIG.STYLES.H3);
    }
    // 볼드 텍스트 줄 (** 로 시작)
    else if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
      const text = line.trim().replace(/\*\*/g, '');
      const para = body.appendParagraph(text);
      para.setBold(true);
      para.setFontSize(CONFIG.STYLES.BODY.fontSize);
    }
    // 불릿 포인트
    else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const indent = line.search(/\S/);
      const text = line.trim().substring(2);
      const listItem = body.appendListItem(processInlineFormatting_(text));
      listItem.setGlyphType(DocumentApp.GlyphType.BULLET);
      listItem.setFontSize(CONFIG.STYLES.BODY.fontSize);
      if (indent > 2) {
        listItem.setNestingLevel(1);
      }
    }
    // 번호 리스트
    else if (/^\d+\.\s/.test(line.trim())) {
      const text = line.trim().replace(/^\d+\.\s/, '');
      const listItem = body.appendListItem(processInlineFormatting_(text));
      listItem.setGlyphType(DocumentApp.GlyphType.NUMBER);
      listItem.setFontSize(CONFIG.STYLES.BODY.fontSize);
    }
    // 인용 (> )
    else if (line.trim().startsWith('> ')) {
      const text = line.trim().substring(2);
      const para = body.appendParagraph(processInlineFormatting_(text));
      para.setFontSize(CONFIG.STYLES.BODY.fontSize - 1);
      para.setItalic(true);
      para.setForegroundColor('#666666');
      para.setIndentStart(36);
    }
    // 일반 텍스트
    else {
      const para = body.appendParagraph(processInlineFormatting_(line.trim()));
      para.setFontSize(CONFIG.STYLES.BODY.fontSize);
      para.setForegroundColor(CONFIG.STYLES.BODY.foregroundColor);
    }

    i++;
  }

  // 마지막 테이블 처리
  if (inTable && tableBuffer.length > 0) {
    appendTable_(body, tableBuffer);
  }

  // 폴더 이동 (지정된 경우)
  if (CONFIG.OUTPUT_FOLDER_ID) {
    const file = DriveApp.getFileById(doc.getId());
    const folder = DriveApp.getFolderById(CONFIG.OUTPUT_FOLDER_ID);
    folder.addFile(file);
    DriveApp.getRootFolder().removeFile(file);
  }

  doc.saveAndClose();

  Logger.log('✅ Google Docs 생성 완료!');
  Logger.log('📄 문서 URL: ' + doc.getUrl());
  Logger.log('📁 문서 ID: ' + doc.getId());

  return doc.getUrl();
}

// ========== 헬퍼 함수 ==========

/**
 * 마크다운 콘텐츠 가져오기
 */
function getMarkdownContent_() {
  if (CONFIG.SOURCE_MODE === 'drive_file' && CONFIG.DRIVE_FILE_ID) {
    const file = DriveApp.getFileById(CONFIG.DRIVE_FILE_ID);
    return file.getBlob().getDataAsString();
  }
  // inline 모드: MARKDOWN_CONTENT 변수 사용
  return MARKDOWN_CONTENT || '';
}

/**
 * 헤딩 추가
 */
function appendHeading_(body, text, headingType, style) {
  const para = body.appendParagraph(text);
  para.setHeading(headingType);
  para.setFontSize(style.fontSize);
  para.setBold(style.bold);
  para.setForegroundColor(style.foregroundColor);
  para.setSpacingBefore(16);
  para.setSpacingAfter(8);
}

/**
 * 테이블 추가
 */
function appendTable_(body, tableLines) {
  if (tableLines.length === 0) return;

  // 테이블 데이터 파싱
  const rows = tableLines.map(line => {
    return line.split('|')
      .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
      .map(cell => cell.trim());
  });

  if (rows.length === 0) return;

  const numCols = rows[0].length;
  const numRows = rows.length;

  // 테이블 생성
  const table = body.appendTable();

  for (let r = 0; r < numRows; r++) {
    const tableRow = (r === 0) ? table.getRow(0) : table.appendTableRow();

    for (let c = 0; c < numCols; c++) {
      const cellText = (rows[r][c] || '').replace(/\*\*/g, '');
      let cell;

      if (r === 0 && c === 0) {
        cell = tableRow.getCell(0);
        cell.setText(cellText);
      } else if (r === 0) {
        cell = tableRow.appendTableCell(cellText);
      } else if (c === 0) {
        cell = tableRow.getCell(0);
        cell.setText(cellText);
      } else {
        cell = tableRow.appendTableCell(cellText);
      }

      // 스타일 적용
      const style = r === 0 ? CONFIG.STYLES.TABLE_HEADER : CONFIG.STYLES.TABLE_BODY;
      const para = cell.getChild(0).asParagraph();
      para.setFontSize(style.fontSize);

      if (r === 0) {
        para.setBold(true);
        cell.setBackgroundColor(style.backgroundColor);
        para.setForegroundColor(style.foregroundColor);
      }
    }
  }

  body.appendParagraph(''); // 테이블 후 빈 줄
}

/**
 * 코드 블록 추가
 */
function appendCodeBlock_(body, code) {
  const para = body.appendParagraph(code);
  para.setFontFamily('Courier New');
  para.setFontSize(9);
  para.setForegroundColor('#333333');
  para.setBackgroundColor('#f5f5f5');
  para.setIndentStart(18);
  para.setIndentEnd(18);
  para.setSpacingBefore(8);
  para.setSpacingAfter(8);
}

/**
 * 인라인 포맷팅 처리 (볼드, 이탈릭)
 * 간단한 처리 — 텍스트만 반환 (Apps Script 제약상 완전한 리치텍스트는 별도 처리 필요)
 */
function processInlineFormatting_(text) {
  // **bold** 와 *italic* 마크다운 제거 (순수 텍스트로)
  return text.replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1');
}


// ========== 마크다운 콘텐츠 (inline 모드용) ==========
// report-docs.md 내용을 아래에 붙여넣으세요
const MARKDOWN_CONTENT = `
여기에 report-docs.md 내용을 붙여넣으세요
`;
