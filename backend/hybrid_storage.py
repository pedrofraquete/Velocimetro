#!/usr/bin/env python3
"""
Sistema híbrido de armazenamento - funciona com JSON local e Supabase
Automaticamente detecta se Supabase está disponível e usa o melhor método
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class HybridStorage:
    def __init__(self):
        """Inicializar sistema híbrido"""
        self.local_file = "/app/backend/prayers_data.json"
        self.supabase_available = False
        self.supabase_manager = None
        
        # Tentar conectar com Supabase
        self._try_supabase_connection()
    
    def _try_supabase_connection(self):
        """Tentar conectar com Supabase"""
        try:
            from supabase_client import SupabaseManager
            
            # Verificar se as variáveis estão configuradas
            if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
                self.supabase_manager = SupabaseManager()
                
                # Testar conexão
                if self.supabase_manager.test_connection():
                    self.supabase_available = True
                    print("✅ Supabase conectado - usando banco de dados na nuvem")
                else:
                    print("⚠️  Supabase não disponível - usando armazenamento local")
            else:
                print("⚠️  Credenciais Supabase não configuradas - usando armazenamento local")
                
        except Exception as e:
            print(f"⚠️  Erro ao conectar Supabase: {e} - usando armazenamento local")
    
    def add_prayer(self, name: str, time_minutes: int, description: str = "", unit: str = "minutos") -> Dict:
        """Adicionar oração usando o melhor método disponível"""
        try:
            # Tentar Supabase primeiro
            if self.supabase_available and self.supabase_manager:
                result = self.supabase_manager.add_prayer(name, time_minutes, description, unit)
                if result["success"]:
                    # Também salvar localmente como backup
                    self._add_to_local_file(name, time_minutes, description, unit)
                    return result
                else:
                    print("⚠️  Falha no Supabase, salvando localmente")
            
            # Fallback para arquivo local
            return self._add_to_local_file(name, time_minutes, description, unit)
            
        except Exception as e:
            print(f"❌ Erro ao adicionar oração: {e}")
            return {"success": False, "error": str(e)}
    
    def _add_to_local_file(self, name: str, time_minutes: int, description: str = "", unit: str = "minutos") -> Dict:
        """Adicionar oração ao arquivo local"""
        try:
            # Carregar dados existentes
            data = self._load_local_data()
            
            # Criar nova entrada
            prayer_entry = {
                "name": name,
                "time": time_minutes,
                "unit": unit,
                "datetime": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
                "description": description
            }
            
            data["prayers"].append(prayer_entry)
            
            # Salvar dados
            with open(self.local_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Oração salva localmente: {name} - {self._format_time(time_minutes)}")
            return {"success": True, "data": prayer_entry, "storage": "local"}
            
        except Exception as e:
            print(f"❌ Erro ao salvar localmente: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_prayers(self) -> List[Dict]:
        """Buscar todas as orações do melhor fonte disponível"""
        try:
            # Tentar Supabase primeiro
            if self.supabase_available and self.supabase_manager:
                prayers = self.supabase_manager.get_all_prayers()
                if prayers:
                    return self._normalize_prayer_format(prayers, "supabase")
            
            # Fallback para dados locais
            data = self._load_local_data()
            prayers = data.get("prayers", [])
            return self._normalize_prayer_format(prayers, "local")
            
        except Exception as e:
            print(f"❌ Erro ao buscar orações: {e}")
            return []
    
    def _normalize_prayer_format(self, prayers: List[Dict], source: str) -> List[Dict]:
        """Normalizar formato das orações independente da fonte"""
        normalized = []
        
        for prayer in prayers:
            if source == "supabase":
                # Formato Supabase
                normalized_prayer = {
                    "id": prayer.get("id"),
                    "name": prayer.get("name"),
                    "time": prayer.get("time_minutes"),
                    "unit": prayer.get("unit", "minutos"),
                    "datetime": prayer.get("datetime"),
                    "description": prayer.get("description", ""),
                    "created_at": prayer.get("created_at"),
                    "source": "supabase"
                }
            else:
                # Formato local
                normalized_prayer = {
                    "name": prayer.get("name"),
                    "time": prayer.get("time"),
                    "unit": prayer.get("unit", "minutos"),
                    "datetime": prayer.get("datetime"),
                    "description": prayer.get("description", ""),
                    "timestamp": prayer.get("timestamp"),
                    "source": "local"
                }
            
            normalized.append(normalized_prayer)
        
        return normalized
    
    def get_prayer_stats(self) -> Dict:
        """Calcular estatísticas das orações"""
        try:
            prayers = self.get_all_prayers()
            
            if not prayers:
                return {
                    "total_prayers": 0,
                    "total_minutes": 0,
                    "total_hours": 0,
                    "progress_percentage": 0,
                    "remaining_hours": 1000,
                    "storage_info": self._get_storage_info()
                }
            
            total_minutes = sum(prayer.get("time", 0) for prayer in prayers)
            total_hours = total_minutes / 60
            progress_percentage = (total_hours / 1000) * 100
            remaining_hours = 1000 - total_hours
            
            return {
                "total_prayers": len(prayers),
                "total_minutes": total_minutes,
                "total_hours": round(total_hours, 2),
                "progress_percentage": round(progress_percentage, 2),
                "remaining_hours": round(remaining_hours, 2),
                "storage_info": self._get_storage_info()
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {"error": str(e)}
    
    def _get_storage_info(self) -> Dict:
        """Informações sobre o armazenamento atual"""
        return {
            "supabase_available": self.supabase_available,
            "primary_storage": "supabase" if self.supabase_available else "local",
            "backup_storage": "local" if self.supabase_available else None,
            "supabase_url": os.getenv("SUPABASE_URL", "não configurado")[:50] + "..." if os.getenv("SUPABASE_URL") else "não configurado"
        }
    
    def _load_local_data(self) -> Dict:
        """Carregar dados do arquivo local"""
        try:
            if os.path.exists(self.local_file):
                with open(self.local_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"prayers": []}
        except Exception as e:
            print(f"⚠️  Erro ao carregar dados locais: {e}")
            return {"prayers": []}
    
    def _format_time(self, minutes: int) -> str:
        """Formatar tempo para exibição"""
        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h{remaining_minutes}min"
        else:
            return f"{minutes}min"
    
    def sync_local_to_supabase(self) -> Dict:
        """Sincronizar dados locais para Supabase"""
        if not self.supabase_available:
            return {"success": False, "error": "Supabase não disponível"}
        
        try:
            result = self.supabase_manager.migrate_local_data(self.local_file)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_prayer(self, prayer_id: int, name: str, time_minutes: int, description: str = "", unit: str = "minutos") -> Dict:
        """Atualizar uma oração usando o melhor método disponível"""
        try:
            # Tentar Supabase primeiro
            if self.supabase_available and self.supabase_manager:
                result = self.supabase_manager.update_prayer(prayer_id, name, time_minutes, description, unit)
                if result["success"]:
                    return result
                else:
                    print("⚠️  Falha no Supabase para atualização")
            
            # Fallback para arquivo local (limitado - não suporta IDs específicos)
            return {"success": False, "error": "Atualização só disponível com Supabase"}
            
        except Exception as e:
            print(f"❌ Erro ao atualizar oração: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_prayer(self, prayer_id: int) -> Dict:
        """Excluir uma oração usando o melhor método disponível"""
        try:
            # Tentar Supabase primeiro
            if self.supabase_available and self.supabase_manager:
                result = self.supabase_manager.delete_prayer(prayer_id)
                if result["success"]:
                    return result
                else:
                    print("⚠️  Falha no Supabase para exclusão")
            
            # Fallback para arquivo local (limitado - não suporta IDs específicos)
            return {"success": False, "error": "Exclusão só disponível com Supabase"}
            
        except Exception as e:
            print(f"❌ Erro ao excluir oração: {e}")
            return {"success": False, "error": str(e)}

    def create_backup(self) -> Dict:
        """Criar backup dos dados"""
        try:
            backup_file = f"/app/backup_orações_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            prayers = self.get_all_prayers()
            stats = self.get_prayer_stats()
            
            backup_data = {
                "backup_date": datetime.now().isoformat(),
                "storage_info": self._get_storage_info(),
                "statistics": stats,
                "prayers": prayers
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return {"success": True, "file": backup_file, "count": len(prayers)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Instância global
hybrid_storage = None

def get_storage() -> HybridStorage:
    """Obter instância do armazenamento híbrido"""
    global hybrid_storage
    if hybrid_storage is None:
        hybrid_storage = HybridStorage()
    return hybrid_storage

if __name__ == "__main__":
    # Teste do sistema híbrido
    print("🔄 Testando sistema híbrido de armazenamento...")
    
    storage = HybridStorage()
    
    # Mostrar informações de armazenamento
    info = storage._get_storage_info()
    print(f"📊 Informações de armazenamento: {info}")
    
    # Mostrar estatísticas
    stats = storage.get_prayer_stats()
    print(f"📈 Estatísticas: {stats}")
    
    # Testar adição
    result = storage.add_prayer("Teste Sistema Híbrido", 15, "Teste de funcionamento")
    print(f"➕ Resultado do teste: {result}")
    
    print("✅ Sistema híbrido funcionando!")
