#!/usr/bin/env python3
"""
Módulo de integração com Supabase para o sistema de orações
Gerencia todas as operações de banco de dados
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

class SupabaseManager:
    def __init__(self):
        """Inicializar cliente Supabase"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configurados")
        
        self.supabase: Client = create_client(self.url, self.key)
        self.table_name = "prayers"
        
        # Criar tabela se não existir
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Garantir que a tabela de orações existe"""
        try:
            # Tentar fazer uma consulta simples para verificar se a tabela existe
            result = self.supabase.table(self.table_name).select("*").limit(1).execute()
            print("✅ Tabela 'prayers' encontrada no Supabase")
        except Exception as e:
            print(f"⚠️  Tabela 'prayers' não encontrada. Erro: {e}")
            print("📝 Você precisa criar a tabela no Supabase Dashboard")
            print("🔧 SQL para criar a tabela:")
            print(self._get_create_table_sql())
    
    def _get_create_table_sql(self):
        """Retornar SQL para criar a tabela"""
        return """
CREATE TABLE prayers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    time_minutes INTEGER NOT NULL,
    unit VARCHAR(50) DEFAULT 'minutos',
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX idx_prayers_datetime ON prayers(datetime);
CREATE INDEX idx_prayers_name ON prayers(name);
CREATE INDEX idx_prayers_created_at ON prayers(created_at);

-- RLS (Row Level Security) - opcional
ALTER TABLE prayers ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública
CREATE POLICY "Allow public read access" ON prayers
    FOR SELECT USING (true);

-- Política para permitir inserção pública
CREATE POLICY "Allow public insert access" ON prayers
    FOR INSERT WITH CHECK (true);
"""
    
    def add_prayer(self, name: str, time_minutes: int, description: str = "", unit: str = "minutos") -> Dict:
        """Adicionar uma nova oração"""
        try:
            prayer_data = {
                "name": name,
                "time_minutes": time_minutes,
                "unit": unit,
                "datetime": datetime.now().isoformat(),
                "description": description
            }
            
            result = self.supabase.table(self.table_name).insert(prayer_data).execute()
            
            if result.data:
                print(f"✅ Oração adicionada: {name} - {self._format_time(time_minutes)}")
                return {"success": True, "data": result.data[0]}
            else:
                print(f"❌ Erro ao adicionar oração: {result}")
                return {"success": False, "error": "Falha na inserção"}
                
        except Exception as e:
            print(f"❌ Erro ao adicionar oração: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_prayers(self) -> List[Dict]:
        """Buscar todas as orações"""
        try:
            result = self.supabase.table(self.table_name).select("*").order("datetime", desc=True).execute()
            
            if result.data:
                print(f"✅ {len(result.data)} orações encontradas")
                return result.data
            else:
                print("📭 Nenhuma oração encontrada")
                return []
                
        except Exception as e:
            print(f"❌ Erro ao buscar orações: {e}")
            return []
    
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
                    "remaining_hours": 1000
                }
            
            total_minutes = sum(prayer.get("time_minutes", 0) for prayer in prayers)
            total_hours = total_minutes / 60
            progress_percentage = (total_hours / 1000) * 100
            remaining_hours = 1000 - total_hours
            
            stats = {
                "total_prayers": len(prayers),
                "total_minutes": total_minutes,
                "total_hours": round(total_hours, 2),
                "progress_percentage": round(progress_percentage, 2),
                "remaining_hours": round(remaining_hours, 2)
            }
            
            print(f"📊 Estatísticas: {len(prayers)} orações, {self._format_time(total_minutes)} total")
            return stats
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {"error": str(e)}
    
    def get_recent_prayers(self, limit: int = 10) -> List[Dict]:
        """Buscar orações recentes"""
        try:
            result = self.supabase.table(self.table_name).select("*").order("datetime", desc=True).limit(limit).execute()
            
            if result.data:
                return result.data
            else:
                return []
                
        except Exception as e:
            print(f"❌ Erro ao buscar orações recentes: {e}")
            return []
    
    def migrate_local_data(self, local_file_path: str) -> Dict:
        """Migrar dados do arquivo local para Supabase"""
        try:
            # Ler dados locais
            with open(local_file_path, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            
            prayers = local_data.get("prayers", [])
            
            if not prayers:
                return {"success": True, "message": "Nenhum dado local para migrar"}
            
            # Verificar quais orações já existem
            existing_prayers = self.get_all_prayers()
            existing_signatures = set()
            
            for prayer in existing_prayers:
                signature = f"{prayer['name']}_{prayer['time_minutes']}_{prayer['datetime'][:19]}"
                existing_signatures.add(signature)
            
            # Migrar dados novos
            migrated_count = 0
            errors = []
            
            for prayer in prayers:
                # Criar assinatura única
                datetime_str = prayer.get("datetime", "").replace("T", " ")[:19]
                signature = f"{prayer['name']}_{prayer['time']}_{datetime_str}"
                
                if signature not in existing_signatures:
                    result = self.add_prayer(
                        name=prayer["name"],
                        time_minutes=prayer["time"],
                        description=prayer.get("description", ""),
                        unit=prayer.get("unit", "minutos")
                    )
                    
                    if result["success"]:
                        migrated_count += 1
                    else:
                        errors.append(f"Erro ao migrar {prayer['name']}: {result['error']}")
                else:
                    print(f"⏭️  Pulando oração duplicada: {prayer['name']}")
            
            return {
                "success": True,
                "migrated_count": migrated_count,
                "total_local": len(prayers),
                "errors": errors
            }
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            return {"success": False, "error": str(e)}
    
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
    
    def test_connection(self) -> bool:
        """Testar conexão com Supabase"""
        try:
            result = self.supabase.table(self.table_name).select("count").execute()
            print("✅ Conexão com Supabase funcionando")
            return True
        except Exception as e:
            print(f"❌ Erro de conexão com Supabase: {e}")
            return False
    
    def backup_to_json(self, backup_file_path: str) -> Dict:
        """Fazer backup dos dados do Supabase para arquivo JSON"""
        try:
            prayers = self.get_all_prayers()
            
            backup_data = {
                "backup_date": datetime.now().isoformat(),
                "total_prayers": len(prayers),
                "prayers": prayers
            }
            
            with open(backup_file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Backup criado: {backup_file_path} ({len(prayers)} orações)")
            return {"success": True, "file": backup_file_path, "count": len(prayers)}
            
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return {"success": False, "error": str(e)}

# Instância global do gerenciador
supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Obter instância do gerenciador Supabase"""
    global supabase_manager
    if supabase_manager is None:
        supabase_manager = SupabaseManager()
    return supabase_manager

if __name__ == "__main__":
    # Teste da conexão
    print("🔄 Testando conexão com Supabase...")
    
    try:
        manager = SupabaseManager()
        
        # Testar conexão
        if manager.test_connection():
            print("✅ Supabase conectado com sucesso!")
            
            # Mostrar estatísticas
            stats = manager.get_prayer_stats()
            print(f"📊 Estatísticas atuais: {stats}")
            
        else:
            print("❌ Falha na conexão com Supabase")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
