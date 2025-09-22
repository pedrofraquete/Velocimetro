"""
Servidor FastAPI - EXCLUSIVAMENTE SUPABASE
ZERO armazenamento local - TODOS os dados APENAS no Supabase
Sistema FALHA se Supabase não funcionar (comportamento desejado)
"""

import os
import sys
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(title="Sistema de Orações - EXCLUSIVAMENTE Supabase")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ ERRO CRÍTICO: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas!")
    logger.error("❌ Sistema não pode funcionar sem Supabase!")
    sys.exit(1)

# Inicializar cliente Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Cliente Supabase inicializado com sucesso")
except Exception as e:
    logger.error(f"❌ ERRO CRÍTICO: Não foi possível inicializar Supabase: {e}")
    logger.error("🚨 Sistema não pode funcionar sem Supabase!")
    sys.exit(1)

# Modelos Pydantic
class PrayerCreate(BaseModel):
    name: str
    time_minutes: int
    description: Optional[str] = ""
    unit: Optional[str] = "minutos"

class PrayerUpdate(BaseModel):
    name: Optional[str] = None
    time_minutes: Optional[int] = None
    description: Optional[str] = None

class PrayerResponse(BaseModel):
    id: int
    name: str
    time_minutes: int
    unit: str
    datetime: str
    description: Optional[str]
    created_at: str

class StatsResponse(BaseModel):
    total_hours: float
    total_entries: int
    progress_percentage: float

# Função para verificar conexão Supabase
def check_supabase_connection():
    """Verifica se Supabase está funcionando"""
    try:
        # Tentar fazer uma consulta simples
        result = supabase.table('prayers').select('id').limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão com Supabase: {e}")
        return False

# Startup event
@app.on_event("startup")
async def startup_event():
    """Verificar Supabase na inicialização"""
    logger.info("🔄 Verificando conexão com Supabase...")
    
    if not check_supabase_connection():
        logger.error("❌ ERRO CRÍTICO: Não foi possível conectar ao Supabase!")
        logger.error("🚨 Sistema não pode funcionar sem Supabase!")
        sys.exit(1)
    
    logger.info("✅ Supabase conectado com sucesso!")
    logger.info("🎯 Sistema funcionando EXCLUSIVAMENTE com Supabase")

# Health check
@app.get("/api/health")
async def health_check():
    """Health check que verifica Supabase"""
    if not check_supabase_connection():
        raise HTTPException(
            status_code=503, 
            detail="Supabase não disponível - Sistema não pode funcionar"
        )
    
    return {
        "status": "healthy",
        "message": "Sistema funcionando EXCLUSIVAMENTE com Supabase",
        "supabase": "connected"
    }

# Listar orações
@app.get("/api/prayers")
async def get_prayers():
    """Buscar TODAS as orações do Supabase"""
    try:
        result = supabase.table('prayers').select('*').order('created_at', desc=True).execute()
        
        prayers = []
        for prayer in result.data:
            prayers.append({
                "id": prayer["id"],
                "name": prayer["name"],
                "time_minutes": prayer["time_minutes"],
                "unit": prayer.get("unit", "minutos"),
                "datetime": prayer["datetime"],
                "description": prayer.get("description", ""),
                "created_at": prayer["created_at"]
            })
        
        logger.info(f"✅ Carregadas {len(prayers)} orações do Supabase")
        return {
            "success": True,
            "data": prayers,
            "message": f"Dados carregados do Supabase: {len(prayers)} orações"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar orações no Supabase: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conectar com Supabase: {str(e)}"
        )

# Adicionar oração
@app.post("/api/prayers")
async def add_prayer(prayer: PrayerCreate):
    """Adicionar oração EXCLUSIVAMENTE no Supabase"""
    try:
        # Preparar dados
        prayer_data = {
            "name": prayer.name,
            "time_minutes": prayer.time_minutes,
            "unit": prayer.unit,
            "datetime": datetime.now().isoformat(),
            "description": prayer.description or ""
        }
        
        # Inserir no Supabase
        result = supabase.table('prayers').insert(prayer_data).execute()
        
        if result.data:
            logger.info(f"✅ Oração salva no Supabase: {prayer.name} - {prayer.time_minutes}min")
            return {
                "success": True,
                "data": result.data[0],
                "message": "Oração salva no Supabase com sucesso"
            }
        else:
            raise Exception("Nenhum dado retornado do Supabase")
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar oração no Supabase: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar no Supabase: {str(e)}"
        )

# Atualizar oração
@app.put("/api/prayers/{prayer_id}")
async def update_prayer(prayer_id: int, prayer: PrayerUpdate):
    """Atualizar oração EXCLUSIVAMENTE no Supabase"""
    try:
        # Preparar dados para atualização
        update_data = {}
        if prayer.name is not None:
            update_data["name"] = prayer.name
        if prayer.time_minutes is not None:
            update_data["time_minutes"] = prayer.time_minutes
        if prayer.description is not None:
            update_data["description"] = prayer.description
        
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Atualizar no Supabase
        result = supabase.table('prayers').update(update_data).eq('id', prayer_id).execute()
        
        if result.data:
            logger.info(f"✅ Oração atualizada no Supabase: ID {prayer_id}")
            return {
                "success": True,
                "data": result.data[0],
                "message": "Oração atualizada no Supabase com sucesso"
            }
        else:
            raise HTTPException(status_code=404, detail="Oração não encontrada no Supabase")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar oração no Supabase: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar no Supabase: {str(e)}"
        )

# Excluir oração
@app.delete("/api/prayers/{prayer_id}")
async def delete_prayer(prayer_id: int):
    """Excluir oração EXCLUSIVAMENTE do Supabase"""
    try:
        # Excluir do Supabase
        result = supabase.table('prayers').delete().eq('id', prayer_id).execute()
        
        if result.data:
            logger.info(f"✅ Oração excluída do Supabase: ID {prayer_id}")
            return {
                "success": True,
                "message": "Oração excluída do Supabase com sucesso"
            }
        else:
            raise HTTPException(status_code=404, detail="Oração não encontrada no Supabase")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao excluir oração do Supabase: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao excluir do Supabase: {str(e)}"
        )

# Estatísticas
@app.get("/api/prayers/stats")
async def get_stats():
    """Calcular estatísticas EXCLUSIVAMENTE do Supabase"""
    try:
        # Buscar todas as orações do Supabase
        result = supabase.table('prayers').select('time_minutes').execute()
        
        prayers = result.data
        total_entries = len(prayers)
        total_minutes = sum(prayer['time_minutes'] for prayer in prayers)
        total_hours = round(total_minutes / 60, 2)
        progress_percentage = round((total_hours / 1000) * 100, 2)
        
        stats = {
            "total_hours": total_hours,
            "total_entries": total_entries,
            "progress_percentage": progress_percentage,
            "total_minutes": total_minutes,
            "remaining_hours": round(1000 - total_hours, 2)
        }
        
        logger.info(f"✅ Estatísticas calculadas do Supabase: {total_hours}h, {total_entries} orações")
        return {
            "success": True,
            "data": stats,
            "message": "Estatísticas calculadas do Supabase"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao calcular estatísticas do Supabase: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular estatísticas do Supabase: {str(e)}"
        )

# Executar servidor
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor EXCLUSIVAMENTE Supabase...")
    logger.info("🚫 ZERO armazenamento local - TODOS os dados no Supabase")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
