"""
Sistema de armazenamento EXCLUSIVAMENTE Supabase
TODOS os dados são salvos e lidos APENAS do Supabase
NÃO há fallback para armazenamento local
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from supabase_client import SupabaseManager

class SupabaseStorage:
    def __init__(self):
        """Inicializar sistema EXCLUSIVO Supabase"""
        self.supabase_manager = None
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Inicializar conexão OBRIGATÓRIA com Supabase"""
        try:
            # Verificar se as variáveis estão configuradas
            if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
                raise Exception("❌ ERRO CRÍTICO: Credenciais Supabase não configuradas!")
            
            self.supabase_manager = SupabaseManager()
            
            # Testar conexão OBRIGATÓRIA
            if not self.supabase_manager.test_connection():
                raise Exception("❌ ERRO CRÍTICO: Não foi possível conectar ao Supabase!")
            
            print("✅ Supabase conectado - TODOS os dados serão salvos na nuvem")
                
        except Exception as e:
            print(f"❌ ERRO CRÍTICO: {e}")
            raise Exception(f"Sistema não pode funcionar sem Supabase: {e}")
    
    def add_prayer(self, name: str, time_minutes: int, description: str = "", unit: str = "minutos") -> Dict:
        """Adicionar oração EXCLUSIVAMENTE no Supabase"""
        try:
            if not self.supabase_manager:
                raise Exception("❌ Supabase não inicializado!")
            
            result = self.supabase_manager.add_prayer(name, time_minutes, description, unit)
            
            if not result.get("success"):
                raise Exception(f"❌ Erro ao salvar no Supabase: {result.get('error', 'Erro desconhecido')}")
            
            print(f"✅ Oração salva no Supabase: {name} - {time_minutes} min")
            return result
            
        except Exception as e:
            print(f"❌ ERRO ao adicionar oração: {e}")
            raise Exception(f"Falha ao salvar no Supabase: {e}")
    
    def get_all_prayers(self) -> List[Dict]:
        """Buscar TODAS as orações EXCLUSIVAMENTE do Supabase"""
        try:
            if not self.supabase_manager:
                raise Exception("❌ Supabase não inicializado!")
            
            prayers = self.supabase_manager.get_all_prayers()
            print(f"✅ {len(prayers)} orações carregadas do Supabase")
            return prayers
            
        except Exception as e:
            print(f"❌ ERRO ao buscar orações: {e}")
            raise Exception(f"Falha ao carregar do Supabase: {e}")
    
    def update_prayer(self, prayer_id: str, updates: Dict) -> bool:
        """Atualizar oração EXCLUSIVAMENTE no Supabase"""
        try:
            if not self.supabase_manager:
                raise Exception("❌ Supabase não inicializado!")
            
            result = self.supabase_manager.update_prayer(prayer_id, updates)
            
            if not result.get("success"):
                raise Exception(f"❌ Erro ao atualizar no Supabase: {result.get('error', 'Erro desconhecido')}")
            
            print(f"✅ Oração atualizada no Supabase: ID {prayer_id}")
            return True
            
        except Exception as e:
            print(f"❌ ERRO ao atualizar oração: {e}")
            raise Exception(f"Falha ao atualizar no Supabase: {e}")
    
    def delete_prayer(self, prayer_id: str) -> bool:
        """Excluir oração EXCLUSIVAMENTE do Supabase"""
        try:
            if not self.supabase_manager:
                raise Exception("❌ Supabase não inicializado!")
            
            result = self.supabase_manager.delete_prayer(prayer_id)
            
            if not result.get("success"):
                raise Exception(f"❌ Erro ao excluir do Supabase: {result.get('error', 'Erro desconhecido')}")
            
            print(f"✅ Oração excluída do Supabase: ID {prayer_id}")
            return True
            
        except Exception as e:
            print(f"❌ ERRO ao excluir oração: {e}")
            raise Exception(f"Falha ao excluir do Supabase: {e}")
    
    def get_prayer_stats(self) -> Dict:
        """Calcular estatísticas EXCLUSIVAMENTE do Supabase"""
        try:
            prayers = self.get_all_prayers()
            
            if not prayers:
                return {
                    "total_prayers": 0,
                    "total_minutes": 0,
                    "total_hours": 0,
                    "progress_percentage": 0,
                    "remaining_hours": 1000,
                    "storage_info": {"source": "supabase", "status": "connected"}
                }
            
            total_minutes = sum(prayer.get("time_minutes", 0) for prayer in prayers)
            total_hours = total_minutes / 60
            progress_percentage = (total_hours / 1000) * 100
            remaining_hours = max(0, 1000 - total_hours)
            
            return {
                "total_prayers": len(prayers),
                "total_minutes": total_minutes,
                "total_hours": round(total_hours, 2),
                "progress_percentage": round(progress_percentage, 2),
                "remaining_hours": round(remaining_hours, 2),
                "storage_info": {"source": "supabase", "status": "connected"}
            }
            
        except Exception as e:
            print(f"❌ ERRO ao calcular estatísticas: {e}")
            raise Exception(f"Falha ao calcular estatísticas do Supabase: {e}")
    
    def get_storage_info(self) -> Dict:
        """Informações do armazenamento - EXCLUSIVAMENTE Supabase"""
        return {
            "storage_type": "supabase_only",
            "supabase_available": True,
            "local_storage": False,
            "description": "Todos os dados são salvos EXCLUSIVAMENTE no Supabase"
        }

# Instância global
supabase_storage = None

def get_storage() -> SupabaseStorage:
    """Obter instância do armazenamento EXCLUSIVO Supabase"""
    global supabase_storage
    if supabase_storage is None:
        supabase_storage = SupabaseStorage()
    return supabase_storage

if __name__ == "__main__":
    # Teste do sistema EXCLUSIVO Supabase
    print("🔄 Testando sistema EXCLUSIVO Supabase...")
    
    try:
        storage = SupabaseStorage()
        
        # Mostrar informações de armazenamento
        info = storage.get_storage_info()
        print(f"📊 Informações de armazenamento: {info}")
        
        # Mostrar estatísticas
        stats = storage.get_prayer_stats()
        print(f"📈 Estatísticas: {stats}")
        
        print("✅ Sistema EXCLUSIVO Supabase funcionando!")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        print("🚨 Sistema não pode funcionar sem Supabase!")
