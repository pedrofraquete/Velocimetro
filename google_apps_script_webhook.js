
// Google Apps Script para receber dados via webhook
// Cole este código em script.google.com

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.openById("1-byhD1HZm2s9DJEh7SDRIvuavyf7Fazb2HuZ3fk_TGk").getActiveSheet();
    
    // Adicionar cabeçalhos se a planilha estiver vazia
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, 3).setValues([["Nome", "Tempo", "Data/Hora"]]);
    }
    
    // Adicionar dados
    const row = [
      data.name,
      data.time_display,
      data.datetime_formatted
    ];
    
    sheet.appendRow(row);
    
    return ContentService
      .createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
