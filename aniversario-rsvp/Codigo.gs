// Confirmação de presença do aniversário (Google Planilhas + Apps Script, sem Google Forms).
// O convidado abre o link, toca em "Vou" ou "Não vou", diz quantas pessoas e envia;
// a resposta cai direto na aba "Confirmações" e a aba "Resumo" soma tudo sozinha.

// ===== AJUSTE AQUI =====
const FESTA = {
  aniversariante: 'NOME DA SUA FILHA',
  idade: '',                       // ex.: '5 anos' (pode deixar vazio)
  data: 'Sábado, 22/11',
  hora: '15h',
  local: 'Endereço da festa',
  prazoTexto: '15/11',
  prazo: '2026-11-15T23:59:59-03:00', // depois disso o link avisa que encerrou
};
// =======================

const ABA = 'Confirmações';
const CAB = ['Data/hora', 'Nome', 'Resposta', 'Adultos', 'Crianças', 'Total', 'Recado'];

function doGet() {
  const t = HtmlService.createTemplateFromFile('Index');
  t.festa = FESTA;
  t.encerrado = new Date() > new Date(FESTA.prazo);
  return t.evaluate()
    .setTitle('Aniversário da ' + FESTA.aniversariante)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// Rode UMA vez pelo editor (botão Executar) para criar as abas e autorizar.
function configurar() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(ABA) || ss.insertSheet(ABA);
  sh.getRange(1, 1, 1, CAB.length).setValues([CAB]).setFontWeight('bold').setBackground('#FFE08A');
  sh.setFrozenRows(1);
  sh.setColumnWidth(2, 200);
  sh.setColumnWidth(7, 260);

  const r = ss.getSheetByName('Resumo') || ss.insertSheet('Resumo', 0);
  r.clear();
  const f = "'" + ABA + "'!";
  r.getRange('A1:B7').setValues([
    ['RESUMO', ''],
    ['Famílias que vão', '=COUNTIF(' + f + 'C:C,"Vou")'],
    ['Adultos', '=SUMIF(' + f + 'C:C,"Vou",' + f + 'D:D)'],
    ['Crianças', '=SUMIF(' + f + 'C:C,"Vou",' + f + 'E:E)'],
    ['TOTAL DE PESSOAS', '=B3+B4'],
    ['Não vão', '=COUNTIF(' + f + 'C:C,"Não vou")'],
    ['Respostas', '=COUNTA(' + f + 'B:B)-1'],
  ]);
  r.getRange('A1').setFontSize(14).setFontWeight('bold');
  r.getRange('A5:B5').setFontWeight('bold').setBackground('#C8F0C8');
  r.setColumnWidth(1, 180);
  const padrao = ss.getSheetByName('Página1') || ss.getSheetByName('Sheet1');
  if (padrao && ss.getSheets().length > 2) ss.deleteSheet(padrao);
}

// Chamado pela página. Se o mesmo nome responder de novo, a linha é atualizada (não duplica).
function salvar(d) {
  if (new Date() > new Date(FESTA.prazo)) throw new Error('As confirmações encerraram em ' + FESTA.prazoTexto + '.');
  const nome = String(d.nome || '').trim().slice(0, 80);
  if (!nome) throw new Error('Escreva seu nome.');
  const vai = d.resposta === 'Vou';
  const adultos = vai ? Math.max(0, Math.min(20, parseInt(d.adultos, 10) || 0)) : 0;
  const criancas = vai ? Math.max(0, Math.min(20, parseInt(d.criancas, 10) || 0)) : 0;
  if (vai && adultos + criancas === 0) throw new Error('Diga quantas pessoas vão.');
  const linha = [new Date(), nome, vai ? 'Vou' : 'Não vou', adultos, criancas, adultos + criancas,
                 String(d.recado || '').slice(0, 300)];

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ABA);
    const chave = normaliza(nome);
    const nomes = sh.getLastRow() > 1 ? sh.getRange(2, 2, sh.getLastRow() - 1, 1).getValues() : [];
    const i = nomes.findIndex(n => normaliza(n[0]) === chave);
    if (i >= 0) sh.getRange(i + 2, 1, 1, linha.length).setValues([linha]);
    else sh.appendRow(linha);
  } finally {
    lock.releaseLock();
  }
  return vai;
}

function normaliza(s) {
  return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ').trim();
}
