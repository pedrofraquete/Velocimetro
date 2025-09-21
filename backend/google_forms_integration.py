"""
Integração alternativa usando Google Forms para capturar dados de oração
Esta abordagem é mais simples e não requer autenticação complexa
"""

import requests
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GoogleFormsIntegration:
    def __init__(self):
        # URL do Google Forms (será configurada quando o formulário for criado)
        self.form_url = None
        # Fallback para armazenamento local
        self.local_storage_file = "prayers_data.json"
        
    def submit_prayer(self, name: str, time_minutes: int, unit: str = "minutos"):
        """
        Submete uma oração para o Google Forms e armazena localmente como backup
        """
        try:
            # Armazenar localmente primeiro (sempre funciona)
            self._store_locally(name, time_minutes, unit)
            
            # Se o Google Forms estiver configurado, tentar enviar
            if self.form_url:
                self._submit_to_google_forms(name, time_minutes, unit)
                
            return {"success": True, "message": "Oração registrada com sucesso"}
            
        except Exception as e:
            logger.error(f"Erro ao registrar oração: {e}")
            return {"success": False, "message": "Erro ao registrar oração"}
    
    def _store_locally(self, name: str, time_minutes: int, unit: str):
        """Armazena os dados localmente como backup"""
        try:
            # Carregar dados existentes
            try:
                with open(self.local_storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"prayers": []}
            
            # Adicionar nova oração
            prayer_entry = {
                "name": name,
                "time": time_minutes,
                "unit": unit,
                "datetime": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp()
            }
            
            data["prayers"].append(prayer_entry)
            
            # Salvar dados atualizados
            with open(self.local_storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Oração armazenada localmente: {name}, {time_minutes} {unit}")
            
        except Exception as e:
            logger.error(f"Erro ao armazenar localmente: {e}")
            raise
    
    def _submit_to_google_forms(self, name: str, time_minutes: int, unit: str):
        """Submete dados para o Google Forms (quando configurado)"""
        if not self.form_url:
            return
            
        try:
            # Dados para enviar ao formulário
            form_data = {
                'entry.nome': name,
                'entry.tempo': str(time_minutes),
                'entry.unidade': unit,
                'entry.data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            # Enviar para o Google Forms
            response = requests.post(self.form_url, data=form_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Oração enviada para Google Forms: {name}")
            else:
                logger.warning(f"Falha ao enviar para Google Forms: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Erro ao enviar para Google Forms: {e}")
            # Não falha se o Google Forms não funcionar
    
    def get_prayers(self):
        """Recupera todas as orações armazenadas localmente"""
        try:
            with open(self.local_storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("prayers", [])
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Erro ao recuperar orações: {e}")
            return []
    
    def get_stats(self):
        """Calcula estatísticas das orações"""
        prayers = self.get_prayers()
        
        if not prayers:
            return {
                "total_prayers": 0,
                "total_hours": 0.0,
                "total_minutes": 0,
                "progress_percentage": 0.0
            }
        
        # Calcular total de minutos
        total_minutes = 0
        for prayer in prayers:
            time_value = prayer.get("time", 0)
            unit = prayer.get("unit", "minutos").lower()
            
            if unit in ["hora", "horas"]:
                total_minutes += time_value * 60
            else:  # minutos
                total_minutes += time_value
        
        # Converter para horas
        total_hours = total_minutes / 60
        
        # Calcular progresso (meta de 1000 horas)
        progress_percentage = (total_hours / 1000) * 100
        
        return {
            "total_prayers": len(prayers),
            "total_hours": round(total_hours, 2),
            "total_minutes": total_minutes,
            "progress_percentage": round(progress_percentage, 2)
        }
    
    def configure_google_forms(self, form_url: str):
        """Configura a URL do Google Forms"""
        self.form_url = form_url
        logger.info(f"Google Forms configurado: {form_url}")

# Instância global
google_forms = GoogleFormsIntegration()
