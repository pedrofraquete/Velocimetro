#!/usr/bin/env python3
"""
Servidor FastAPI com sistema híbrido de armazenamento
Funciona com Supabase quando disponível, fallback para JSON local
Sistema de Orações - Igreja Videira
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from dotenv import load_dotenv
from hybrid_storage import get_storage

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Modelos Pydantic
class PrayerRequest(BaseModel):
    name: str
    time: int
    unit: str = "minutos"
    description: Optional[str] = ""

class PrayerResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PrayerStats(BaseModel):
    total_hours: float
    total_entries: int
    progress_percentage: float

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Orações - Igreja Videira",
    description="API para gerenciar as 1000 horas de oração com armazenamento híbrido",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obter instância do armazenamento
storage = get_storage()

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Sistema de Orações - Igreja Videira",
        "version": "2.0.0",
        "features": ["Supabase", "Local Storage", "Hybrid Mode"],
        "storage_info": storage._get_storage_info()
    }

@app.post("/api/prayers", response_model=PrayerResponse)
async def add_prayer(prayer: PrayerRequest):
    """Adicionar uma nova oração"""
    try:
        result = storage.add_prayer(
            name=prayer.name,
            time_minutes=prayer.time,
            description=prayer.description,
            unit=prayer.unit
        )
        
        if result["success"]:
            return PrayerResponse(
                success=True,
                message=f"Oração de {prayer.name} registrada com sucesso!",
                data=result.get("data")
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Erro desconhecido"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prayers")
async def get_prayers():
    """Buscar todas as orações"""
    try:
        prayers = storage.get_all_prayers()
        return {
            "success": True,
            "data": prayers,
            "count": len(prayers),
            "storage_info": storage._get_storage_info()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prayers/stats", response_model=dict)
async def get_prayer_stats():
    """Obter estatísticas das orações"""
    try:
        stats = storage.get_prayer_stats()
        
        # Formato compatível com frontend
        return {
            "success": True,
            "data": {
                "total_hours": stats.get("total_hours", 0),
                "total_entries": stats.get("total_prayers", 0),
                "progress_percentage": stats.get("progress_percentage", 0),
                "remaining_hours": stats.get("remaining_hours", 1000),
                "storage_info": stats.get("storage_info", {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prayers/recent")
async def get_recent_prayers(limit: int = 10):
    """Buscar orações recentes"""
    try:
        all_prayers = storage.get_all_prayers()
        
        # Ordenar por data (mais recentes primeiro)
        sorted_prayers = sorted(
            all_prayers, 
            key=lambda x: x.get("datetime", ""), 
            reverse=True
        )
        
        recent_prayers = sorted_prayers[:limit]
        
        return {
            "success": True,
            "data": recent_prayers,
            "count": len(recent_prayers),
            "total": len(all_prayers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync")
async def sync_to_supabase():
    """Sincronizar dados locais para Supabase"""
    try:
        result = storage.sync_local_to_supabase()
        
        if result["success"]:
            return {
                "success": True,
                "message": "Sincronização concluída",
                "data": result
            }
        else:
            return {
                "success": False,
                "message": result.get("error", "Erro na sincronização"),
                "data": result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backup")
async def create_backup():
    """Criar backup dos dados"""
    try:
        result = storage.create_backup()
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Backup criado com {result['count']} orações",
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Verificar saúde do sistema"""
    try:
        stats = storage.get_prayer_stats()
        storage_info = storage._get_storage_info()
        
        return {
            "status": "healthy",
            "storage": storage_info,
            "data_summary": {
                "total_prayers": stats.get("total_prayers", 0),
                "total_hours": stats.get("total_hours", 0),
                "progress": f"{stats.get('progress_percentage', 0)}%"
            },
            "timestamp": "2025-09-21T21:00:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-09-21T21:00:00Z"
        }

# Manter compatibilidade com rotas antigas
@app.get("/api/status")
async def get_status():
    """Endpoint de compatibilidade"""
    return await health_check()

if __name__ == "__main__":
    print("🚀 Iniciando servidor híbrido...")
    print(f"📊 Storage info: {storage._get_storage_info()}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
