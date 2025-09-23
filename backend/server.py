"""
Servidor FastAPI - EXCLUSIVAMENTE Supabase
TODOS os dados são salvos e lidos APENAS do Supabase
NÃO há fallback para armazenamento local
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar sistema EXCLUSIVO Supabase
from supabase_storage import get_storage

app = FastAPI(title="Sistema de Orações Igreja Videira - EXCLUSIVAMENTE Supabase")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class PrayerRequest(BaseModel):
    name: str
    time_minutes: int
    description: Optional[str] = ""
    unit: Optional[str] = "minutos"

class PrayerUpdate(BaseModel):
    name: Optional[str] = None
    time_minutes: Optional[int] = None
    description: Optional[str] = None
    unit: Optional[str] = None

# Inicializar armazenamento EXCLUSIVO Supabase
try:
    storage = get_storage()
    print("✅ Servidor iniciado com armazenamento EXCLUSIVO Supabase")
    print("🚫 NÃO há armazenamento local - TODOS os dados no Supabase")
except Exception as e:
    print(f"❌ ERRO CRÍTICO: Não foi possível inicializar Supabase: {e}")
    print("🚨 Servidor não pode funcionar sem Supabase!")
    print("📋 Verifique se as variáveis SUPABASE_URL e SUPABASE_KEY estão configuradas")
    exit(1)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema de Orações Igreja Videira - EXCLUSIVAMENTE Supabase",
        "storage": "supabase_only",
        "status": "connected",
        "version": "2.0",
        "local_storage": False
    }

@app.get("/api/health")
async def health_check():
    """Verificar saúde do sistema"""
    try:
        info = storage.get_storage_info()
        return {
            "status": "healthy",
            "storage": info,
            "timestamp": datetime.now().isoformat(),
            "supabase_only": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sistema não saudável: {str(e)}")

@app.post("/api/prayers")
async def add_prayer(prayer: PrayerRequest):
    """Adicionar nova oração - EXCLUSIVAMENTE no Supabase"""
    try:
        result = storage.add_prayer(
            name=prayer.name,
            time_minutes=prayer.time_minutes,
            description=prayer.description,
            unit=prayer.unit
        )
        
        return {
            "success": True,
            "message": "Oração adicionada com sucesso no Supabase!",
            "data": result,
            "storage": "supabase_only"
        }
        
    except Exception as e:
        print(f"❌ Erro ao adicionar oração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no Supabase: {str(e)}")

@app.get("/api/prayers")
async def get_prayers():
    """Buscar todas as orações - EXCLUSIVAMENTE do Supabase"""
    try:
        prayers = storage.get_all_prayers()
        
        return {
            "success": True,
            "data": prayers,
            "count": len(prayers),
            "storage": "supabase_only"
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar orações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao carregar do Supabase: {str(e)}")

@app.get("/api/prayers/stats")
async def get_prayer_stats():
    """Obter estatísticas das orações - EXCLUSIVAMENTE do Supabase"""
    try:
        stats = storage.get_prayer_stats()
        
        return {
            "success": True,
            "data": {
                "total_entries": stats["total_prayers"],
                "total_hours": stats["total_hours"],
                "total_minutes": stats["total_minutes"],
                "progress_percentage": stats["progress_percentage"],
                "remaining_hours": stats["remaining_hours"]
            },
            "storage": "supabase_only"
        }
        
    except Exception as e:
        print(f"❌ Erro ao calcular estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular estatísticas do Supabase: {str(e)}")

@app.put("/api/prayers/{prayer_id}")
async def update_prayer(prayer_id: str, updates: PrayerUpdate):
    """Atualizar oração - EXCLUSIVAMENTE no Supabase"""
    try:
        # Preparar dados para atualização
        update_data = {}
        if updates.name is not None:
            update_data["name"] = updates.name
        if updates.time_minutes is not None:
            update_data["time_minutes"] = updates.time_minutes
        if updates.description is not None:
            update_data["description"] = updates.description
        if updates.unit is not None:
            update_data["unit"] = updates.unit
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        success = storage.update_prayer(prayer_id, update_data)
        
        if success:
            return {
                "success": True,
                "message": "Oração atualizada com sucesso no Supabase!",
                "storage": "supabase_only"
            }
        else:
            raise HTTPException(status_code=404, detail="Oração não encontrada")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao atualizar oração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar no Supabase: {str(e)}")

@app.delete("/api/prayers/{prayer_id}")
async def delete_prayer(prayer_id: str):
    """Excluir oração - EXCLUSIVAMENTE do Supabase"""
    try:
        success = storage.delete_prayer(prayer_id)
        
        if success:
            return {
                "success": True,
                "message": "Oração excluída com sucesso do Supabase!",
                "storage": "supabase_only"
            }
        else:
            raise HTTPException(status_code=404, detail="Oração não encontrada")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao excluir oração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir do Supabase: {str(e)}")

@app.get("/api/storage/info")
async def get_storage_info():
    """Informações sobre o armazenamento"""
    try:
        info = storage.get_storage_info()
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando servidor EXCLUSIVAMENTE Supabase...")
    print("📊 TODOS os dados serão salvos APENAS no Supabase")
    print("🚫 NÃO há armazenamento local")
    print("🔧 Certifique-se de que SUPABASE_URL e SUPABASE_KEY estão configurados")
    
    # Verificar variáveis de ambiente
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ ERRO: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas!")
        print("📋 Copie .env.example para .env e configure as credenciais")
        exit(1)
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
