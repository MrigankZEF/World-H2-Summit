/**
 * ZEF Poll · Google Apps Script Web App
 *
 * What this does:
 *   doPost  →  Append a submission row to the "Submissions" tab.
 *   doGet   →  Return live aggregate shares for the reveal chart.
 *
 * Multi-select questions: values are stored as comma-separated strings in a
 * single column (e.g. "power,electrolyzers,epc"). Aggregate counts each token.
 *
 * Setup (one time):
 *   1. Open your Google Sheet.
 *   2. Extensions → Apps Script.
 *   3. Replace Code.gs with this file's contents. Save.
 *   4. Deploy → New deployment → "Web app".
 *        Execute as: Me
 *        Who has access: Anyone
 *      Authorize when prompted. Copy the /exec URL.
 *
 * Updating: when QUESTION_IDS or MULTI_QUESTION_IDS changes here, Deploy →
 * Manage deployments → ✏️ on the active deployment → Version: New version →
 * Deploy.
 */

const SHEET_NAME = 'Submissions';
const QUESTION_IDS = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'];
const MULTI_QUESTION_IDS = ['q2'];

const HEADERS = [
  'Timestamp',
  'Type',
  'SessionId',
  'Email',
  'Role',
  ...QUESTION_IDS,
  'Source',
  'Consent',
  'UserAgent',
];

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function jsonOut_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || '{}');
    const sheet = getSheet_();
    const row = [
      payload.timestamp ? new Date(payload.timestamp) : new Date(),
      payload.type || '',
      payload.sessionId || '',
      payload.email || '',
      payload.role || '',
      ...QUESTION_IDS.map(id => {
        const v = payload[id];
        if (Array.isArray(v)) return v.join(',');
        return v == null ? '' : String(v);
      }),
      payload.source || '',
      payload.consent === true ? 'yes' : (payload.consent === false ? 'no' : ''),
      (payload.userAgent || '').toString().slice(0, 250),
    ];
    sheet.appendRow(row);
    return jsonOut_({ ok: true });
  } catch (err) {
    return jsonOut_({ ok: false, error: String(err) });
  }
}

function doGet(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    const empty = { total: 0, updatedAt: new Date().toISOString() };
    QUESTION_IDS.forEach(id => empty[id] = {});
    if (!sheet || sheet.getLastRow() < 2) return jsonOut_(empty);

    const rows = sheet.getRange(2, 1, sheet.getLastRow() - 1, HEADERS.length).getValues();
    const typeCol = HEADERS.indexOf('Type');
    const qCols = QUESTION_IDS.map(id => HEADERS.indexOf(id));

    const counts = {};
    QUESTION_IDS.forEach(id => counts[id] = {});

    let total = 0;
    rows.forEach(r => {
      if (r[typeCol] !== 'poll') return;
      total += 1;
      QUESTION_IDS.forEach((id, i) => {
        const raw = (r[qCols[i]] || '').toString().trim();
        if (!raw) return;
        if (MULTI_QUESTION_IDS.indexOf(id) >= 0) {
          raw.split(',').map(s => s.trim()).filter(Boolean).forEach(v => {
            counts[id][v] = (counts[id][v] || 0) + 1;
          });
        } else {
          counts[id][raw] = (counts[id][raw] || 0) + 1;
        }
      });
    });

    const result = { total: total, updatedAt: new Date().toISOString() };
    QUESTION_IDS.forEach(id => {
      const shares = {};
      const denom = Math.max(total, 1);
      Object.keys(counts[id]).forEach(k => shares[k] = counts[id][k] / denom);
      result[id] = shares;
    });
    return jsonOut_(result);
  } catch (err) {
    return jsonOut_({ ok: false, error: String(err) });
  }
}
