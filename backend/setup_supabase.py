#!/usr/bin/env python3
"""
Script para configurar automaticamente a tabela no Supabase
Cria a tabela e migra os dados existentes
"""

import os
import json
from supabase import create_client
from supabase_client import SupabaseManager

def create_table_via_rpc():
    """Criar tabela usando RPC (Remote Procedure Call)"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ SUPABASE_URL e SUPABASE_KEY devem estar configurados")
            return False
        
        supabase = create_client(url, key)
        
        # SQL para criar a tabela
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS prayers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            time_minutes INTEGER NOT NULL,
            unit VARCHAR(50) DEFAULT 'minutos',
            datetime TIMESTAMP WITH TIME ZONE NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Tentar executar via RPC
        try:
            result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            print("✅ Tabela criada via RPC")
            return True
        except Exception as e:
            print(f"⚠️  RPC não disponível: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False

def setup_supabase_manually():
    """Configurar Supabase manualmente - mostrar instruções"""
    print("🔧 CONFIGURAÇÃO MANUAL DO SUPABASE")
    print("="*50)
    print()
    print("1. Acesse: https://supabase.com/dashboard")
    print("2. Vá para seu projeto")
    print("3. Clique em 'SQL Editor' no menu lateral")
    print("4. Cole o SQL abaixo e execute:")
    print()
    print("="*50)
    print("SQL PARA EXECUTAR:")
    print("="*50)
    
    sql = """
-- Criar tabela de orações
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

-- Inserir dados de exemplo (opcional)
INSERT INTO prayers (name, time_minutes, unit, datetime, description) VALUES
('Pedro Fraquete', 60, 'minutos', '2025-09-21T12:40:00+00:00', 'Devocional'),
('Luara', 30, 'minutos', '2025-09-21T12:50:00+00:00', 'Nova!');
"""
    
    print(sql)
    print("="*50)
    print()
    print("5. Após executar, pressione Enter para continuar...")
    input()
    
    return True

def migrate_existing_data():
    """Migrar dados existentes do arquivo local"""
    try:
        local_file = "/home/ubuntu/Velocimetro/backend/prayers_data.json"
        
        if not os.path.exists(local_file):
            print("📭 Nenhum arquivo local encontrado para migrar")
            return True
        
        print("🔄 Migrando dados existentes...")
        
        manager = SupabaseManager()
        result = manager.migrate_local_data(local_file)
        
        if result["success"]:
            print(f"✅ Migração concluída: {result.get('migrated_count', 0)} orações migradas")
            if result.get("errors"):
                print("⚠️  Alguns erros ocorreram:")
                for error in result["errors"]:
                    print(f"   - {error}")
            return True
        else:
            print(f"❌ Erro na migração: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

def test_final_setup():
    """Testar configuração final"""
    try:
        print("🧪 Testando configuração final...")
        
        manager = SupabaseManager()
        
        # Testar conexão
        if not manager.test_connection():
            print("❌ Teste de conexão falhou")
            return False
        
        # Testar inserção
        test_result = manager.add_prayer(
            name="Teste Supabase",
            time_minutes=5,
            description="Teste de configuração"
        )
        
        if test_result["success"]:
            print("✅ Teste de inserção passou")
            
            # Buscar estatísticas
            stats = manager.get_prayer_stats()
            print(f"📊 Estatísticas: {stats}")
            
            return True
        else:
            print(f"❌ Teste de inserção falhou: {test_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal de configuração"""
    print("🚀 CONFIGURAÇÃO DO SUPABASE PARA SISTEMA DE ORAÇÕES")
    print("="*60)
    print()
    
    # Verificar variáveis de ambiente
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Variáveis SUPABASE_URL e SUPABASE_KEY não configuradas")
        return False
    
    print(f"✅ Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"✅ Supabase Key: {os.getenv('SUPABASE_KEY')[:20]}...")
    print()
    
    # Tentar criar tabela automaticamente
    print("🔧 Tentando criar tabela automaticamente...")
    if create_table_via_rpc():
        print("✅ Tabela criada automaticamente")
    else:
        print("⚠️  Criação automática falhou, configuração manual necessária")
        setup_supabase_manually()
    
    # Testar conexão
    try:
        manager = SupabaseManager()
        if manager.test_connection():
            print("✅ Conexão com Supabase estabelecida")
            
            # Migrar dados existentes
            migrate_existing_data()
            
            # Teste final
            if test_final_setup():
                print()
                print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
                print("✅ Supabase está pronto para uso")
                print("✅ Dados migrados (se existiam)")
                print("✅ Sistema funcionando")
                return True
            else:
                print("❌ Teste final falhou")
                return False
        else:
            print("❌ Não foi possível conectar ao Supabase")
            print("💡 Verifique se executou o SQL no dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. ✅ Supabase configurado")
        print("2. 🔄 Atualizar server.py para usar Supabase")
        print("3. 🚀 Testar sistema completo")
    else:
        print("\n❌ CONFIGURAÇÃO FALHOU")
        print("💡 Execute o SQL manualmente no Supabase Dashboard")
        print("🔗 https://supabase.com/dashboard")
