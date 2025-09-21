#!/usr/bin/env python3
"""
Solução simples para adicionar dados na planilha do Google Sheets
Gera comandos que podem ser executados manualmente na planilha
"""

import json
from datetime import datetime

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

def load_prayers_data():
    """Carregar dados das orações"""
    try:
        with open("/home/ubuntu/Velocimetro/backend/prayers_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("prayers", [])
    except FileNotFoundError:
        return []

def generate_sheets_data():
    """Gerar dados formatados para a planilha"""
    prayers = load_prayers_data()
    
    if not prayers:
        print("❌ Nenhum dado encontrado!")
        return
    
    print("📋 DADOS PARA ADICIONAR NA PLANILHA:")
    print("="*60)
    print("Copie e cole os dados abaixo na planilha do Google Sheets:")
    print("="*60)
    
    # Cabeçalhos
    print("LINHA 1 (Cabeçalhos):")
    print("A1: Nome")
    print("B1: Tempo") 
    print("C1: Data/Hora")
    print()
    
    # Dados
    for i, prayer in enumerate(prayers, 2):
        time_display = format_time_display(prayer["time"])
        datetime_display = format_datetime(prayer["datetime"])
        
        print(f"LINHA {i}:")
        print(f"A{i}: {prayer['name']}")
        print(f"B{i}: {time_display}")
        print(f"C{i}: {datetime_display}")
        print()
    
    # Resumo
    total_minutes = sum(p["time"] for p in prayers)
    total_hours = total_minutes / 60
    
    print("="*60)
    print("📊 RESUMO:")
    print(f"Total de orações: {len(prayers)}")
    print(f"Total de tempo: {format_time_display(total_minutes)} ({total_hours:.1f}h)")
    print(f"Progresso: {(total_hours/1000)*100:.2f}% da meta de 1000h")
    print("="*60)

def create_csv_file():
    """Criar arquivo CSV para importar na planilha"""
    prayers = load_prayers_data()
    
    if not prayers:
        print("❌ Nenhum dado encontrado!")
        return
    
    csv_content = "Nome,Tempo,Data/Hora\n"
    
    for prayer in prayers:
        time_display = format_time_display(prayer["time"])
        datetime_display = format_datetime(prayer["datetime"])
        csv_content += f'"{prayer["name"]}","{time_display}","{datetime_display}"\n'
    
    csv_file = "/home/ubuntu/Velocimetro/orações_para_planilha.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print(f"📄 Arquivo CSV criado: {csv_file}")
    print("💡 Para usar:")
    print("1. Abra a planilha do Google Sheets")
    print("2. Vá em Arquivo > Importar")
    print("3. Faça upload do arquivo orações_para_planilha.csv")
    print("4. Configure para substituir os dados existentes")

if __name__ == "__main__":
    print("🔄 Preparando dados para Google Sheets...")
    print()
    
    # Gerar dados formatados
    generate_sheets_data()
    
    # Criar arquivo CSV
    create_csv_file()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Copie os dados mostrados acima")
    print("2. Cole na planilha do Google Sheets")
    print("3. OU use o arquivo CSV para importar")
    print("4. ✅ Dados aparecerão na planilha!")
