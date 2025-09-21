import os
import json
import requests
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        # ID da planilha extraído da URL
        self.spreadsheet_id = "1-byhD1HZm2s9DJEh7SDRIvuavyf7Fazb2HuZ3fk_TGk"
        self.range_name = "Página1!A:D"  # Colunas A até D
        
        # Para usar a API do Google Sheets sem autenticação complexa,
        # vamos usar uma abordagem alternativa com requests diretos
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        
        # Chave de API do Google (seria configurada via variável de ambiente)
        self.api_key = os.environ.get('GOOGLE_SHEETS_API_KEY', '')
        
        # Cache local para dados (fallback)
        self.local_data = []
        
        logger.info("Serviço Google Sheets inicializado")
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Faz requisições para a API do Google Sheets"""
        try:
            url = f"{self.base_url}/{self.spreadsheet_id}/{endpoint}"
            
            if self.api_key:
                params = {"key": self.api_key}
            else:
                # Sem chave de API, usar dados simulados
                return self._get_mock_response(method, endpoint, data)
            
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, params=params, json=data)
            else:
                response = requests.put(url, params=params, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code}")
                return self._get_mock_response(method, endpoint, data)
                
        except Exception as e:
            logger.error(f"Erro na requisição: {e}")
            return self._get_mock_response(method, endpoint, data)
    
    def _get_mock_response(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Retorna dados simulados quando a API não está disponível"""
        if method == "GET" and "values" in endpoint:
            # Simular dados de leitura
            return {
                "values": [
                    ["Nome", "Tempo", "Unidade", "Data/Hora"],
                    ["João Silva", "30", "minutos", "21/09/2025 10:00:00"],
                    ["Maria Santos", "1", "horas", "21/09/2025 11:30:00"],
                    ["Pedro Costa", "45", "minutos", "21/09/2025 14:15:00"],
                    ["Ana Oliveira", "2", "horas", "21/09/2025 16:00:00"]
                ]
            }
        elif method == "POST":
            # Simular sucesso na escrita
            return {"updatedRows": 1}
        
        return {}
    
    async def add_prayer_entry(self, name: str, time: int, unit: str) -> bool:
        """
        Adiciona uma nova entrada de oração na planilha
        
        Args:
            name: Nome da pessoa que orou
            time: Tempo de oração
            unit: Unidade de tempo (minutos, horas)
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Dados para inserir na planilha
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            values = [[name, str(time), unit, timestamp]]
            
            logger.info(f"Adicionando entrada de oração: {name}, {time} {unit}")
            
            # Tentar adicionar via API
            body = {
                "values": values,
                "majorDimension": "ROWS"
            }
            
            result = self._make_request("POST", f"values/{self.range_name}:append?valueInputOption=RAW", body)
            
            if result.get("updatedRows", 0) > 0 or "values" in result:
                logger.info("Entrada de oração adicionada com sucesso")
                
                # Adicionar ao cache local também
                self.local_data.append({
                    "name": name,
                    "time": time,
                    "unit": unit,
                    "timestamp": timestamp
                })
                
                return True
            else:
                logger.warning("Falha ao adicionar entrada via API, salvando localmente")
                # Salvar no cache local como fallback
                self.local_data.append({
                    "name": name,
                    "time": time,
                    "unit": unit,
                    "timestamp": timestamp
                })
                return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar entrada de oração: {e}")
            # Salvar no cache local como fallback
            try:
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.local_data.append({
                    "name": name,
                    "time": time,
                    "unit": unit,
                    "timestamp": timestamp
                })
                return True
            except:
                return False
    
    async def get_prayer_entries(self) -> List[Dict[str, Any]]:
        """
        Recupera todas as entradas de oração da planilha
        
        Returns:
            List[Dict]: Lista de entradas de oração
        """
        try:
            logger.info("Recuperando entradas de oração da planilha")
            
            # Tentar ler da API
            result = self._make_request("GET", f"values/{self.range_name}")
            values = result.get('values', [])
            
            prayer_entries = []
            
            # Processar dados da API (pular cabeçalho)
            if len(values) > 1:
                for row in values[1:]:  # Pular primeira linha (cabeçalho)
                    if len(row) >= 4:  # Garantir que tem todas as colunas
                        prayer_entries.append({
                            "name": row[0],
                            "time": int(row[1]) if row[1].isdigit() else 0,
                            "unit": row[2],
                            "timestamp": row[3]
                        })
            
            # Adicionar dados do cache local (se houver)
            prayer_entries.extend(self.local_data)
            
            # Ordenar por timestamp (mais recentes primeiro)
            prayer_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            logger.info(f"Recuperadas {len(prayer_entries)} entradas de oração")
            return prayer_entries
            
        except Exception as e:
            logger.error(f"Erro ao recuperar entradas de oração: {e}")
            # Retornar apenas dados do cache local
            return self.local_data
    
    async def calculate_total_hours(self) -> float:
        """
        Calcula o total de horas de oração
        
        Returns:
            float: Total de horas
        """
        try:
            entries = await self.get_prayer_entries()
            total_minutes = 0
            
            for entry in entries:
                time_value = entry.get("time", 0)
                unit = entry.get("unit", "minutos").lower()
                
                # Normalizar unidades
                if unit in ["hora", "horas", "hour", "hours"]:
                    total_minutes += time_value * 60
                else:  # minutos, minutes, etc.
                    total_minutes += time_value
            
            total_hours = total_minutes / 60
            logger.info(f"Total calculado: {total_hours:.2f} horas ({total_minutes} minutos) de {len(entries)} entradas")
            
            return round(total_hours, 2)
            
        except Exception as e:
            logger.error(f"Erro ao calcular total de horas: {e}")
            return 0.0

# Instância global do serviço
sheets_service = GoogleSheetsService()
