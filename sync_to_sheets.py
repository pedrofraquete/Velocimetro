#!/usr/bin/env python3
"""
Script para sincronizar dados existentes do sistema com Google Sheets
Adiciona os dados que já estão no sistema local para a planilha
"""

import requests
import json
from datetime import datetime

# ID da planilha do Google Sheets
SHEET_ID = "1-byhD1HZm2s9DJEh7SDRIvuavyf7Fazb2HuZ3fk_TGk"

# Dados que já estão no sistema (baseado na imagem do usuário)
existing_data = [
    {
        "name": "Pedro Fraquete",
        "time": 60,  # 1 hora em minutos
        "unit": "minutos",
        "description": "Devocional",
        "datetime": "2025-09-21T12:40:00"
    },
    {
        "name": "Luara",
        "time": 30,  # 30 minutos
        "unit": "minutos", 
        "description": "Nova!",
        "datetime": "2025-09-21T12:50:00"
    }
]

def format_time_display(time_minutes):
    """Formatar tempo para exibição"""
    if time_minutes >= 60:
        hours = time_minutes // 60
        remaining_minutes = time_minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h{remaining_minutes}min"
    else:
        return f"{time_minutes}min"

def format_datetime(datetime_str):
    """Formatar data/hora para exibição"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return datetime_str

def create_google_form_url():
    """
    Criar URL de um Google Form que alimenta a planilha
    Esta é uma abordagem mais simples que a API direta
    """
    # Para implementar: criar um Google Form que alimente a planilha
    # Por enquanto, vamos usar uma abordagem de webhook simples
    pass

def add_data_to_local_storage():
    """Adicionar dados ao armazenamento local do sistema"""
    local_file = "/home/ubuntu/Velocimetro/backend/prayers_data.json"
    
    try:
        # Carregar dados existentes
        try:
            with open(local_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"prayers": []}
        
        # Adicionar dados se não existirem
        for prayer_data in existing_data:
            # Verificar se já existe
            exists = any(
                p.get("name") == prayer_data["name"] and 
                p.get("time") == prayer_data["time"]
                for p in data["prayers"]
            )
            
            if not exists:
                prayer_entry = {
                    "name": prayer_data["name"],
                    "time": prayer_data["time"],
                    "unit": prayer_data["unit"],
                    "datetime": prayer_data["datetime"],
                    "timestamp": datetime.fromisoformat(prayer_data["datetime"]).timestamp(),
                    "description": prayer_data.get("description", "")
                }
                data["prayers"].append(prayer_entry)
                print(f"✅ Adicionado: {prayer_data['name']} - {format_time_display(prayer_data['time'])}")
        
        # Salvar dados atualizados
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Dados salvos em: {local_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados locais: {e}")
        return False

def create_sheets_webhook():
    """
    Criar um webhook simples que pode ser usado para enviar dados para Google Sheets
    """
    webhook_code = '''
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
'''
    
    with open("/home/ubuntu/Velocimetro/google_apps_script_webhook.js", "w") as f:
        f.write(webhook_code)
    
    print("📝 Código do webhook criado em: google_apps_script_webhook.js")
    print("📋 Para usar:")
    print("1. Acesse script.google.com")
    print("2. Crie um novo projeto")
    print("3. Cole o código do arquivo google_apps_script_webhook.js")
    print("4. Publique como Web App")
    print("5. Use a URL gerada no sistema")

def print_summary():
    """Imprimir resumo dos dados"""
    total_minutes = sum(d["time"] for d in existing_data)
    total_hours = total_minutes / 60
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS DADOS")
    print("="*50)
    
    for data in existing_data:
        time_display = format_time_display(data["time"])
        datetime_display = format_datetime(data["datetime"])
        print(f"👤 {data['name']}: {time_display} - {datetime_display}")
        if data.get("description"):
            print(f"   📝 {data['description']}")
    
    print("-"*50)
    print(f"⏱️  Total: {format_time_display(total_minutes)} ({total_hours:.1f}h)")
    print(f"📈 Progresso: {(total_hours/1000)*100:.2f}% da meta de 1000h")
    print(f"🎯 Restam: {1000-total_hours:.1f}h para completar a meta")
    print("="*50)

if __name__ == "__main__":
    print("🔄 Sincronizando dados com o sistema...")
    
    # Adicionar dados ao armazenamento local
    if add_data_to_local_storage():
        print("✅ Dados sincronizados com sucesso!")
    
    # Criar webhook para Google Sheets
    create_sheets_webhook()
    
    # Mostrar resumo
    print_summary()
    
    print("\n🚀 Próximos passos:")
    print("1. ✅ Dados já estão no sistema local")
    print("2. 📋 Use o código do webhook para conectar com Google Sheets")
    print("3. 🔄 Configure o webhook no Google Apps Script")
    print("4. 🎉 Dados aparecerão automaticamente na planilha!")
