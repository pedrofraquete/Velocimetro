from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from google_sheets import sheets_service


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (opcional, mantendo para compatibilidade)
try:
    mongo_url = os.environ.get('MONGO_URL', '')
    if mongo_url:
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'velocimetro')]
    else:
        client = None
        db = None
except Exception as e:
    logging.warning(f"MongoDB não configurado: {e}")
    client = None
    db = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class PrayerEntry(BaseModel):
    name: str
    time: int
    unit: str  # "minutos" ou "horas"
    timestamp: Optional[str] = None

class PrayerEntryCreate(BaseModel):
    name: str
    time: int
    unit: str

class PrayerStats(BaseModel):
    total_hours: float
    total_entries: int
    progress_percentage: float

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Sistema de Orações - API funcionando!"}

# Rotas para orações
@api_router.post("/prayers", response_model=dict)
async def add_prayer(prayer: PrayerEntryCreate):
    """Adiciona uma nova entrada de oração na planilha do Google Sheets"""
    try:
        success = await sheets_service.add_prayer_entry(
            name=prayer.name,
            time=prayer.time,
            unit=prayer.unit
        )
        
        if success:
            return {"message": "Oração registrada com sucesso!", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Erro ao registrar oração")
            
    except Exception as e:
        logging.error(f"Erro ao adicionar oração: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/prayers", response_model=List[dict])
async def get_prayers():
    """Recupera todas as entradas de oração da planilha"""
    try:
        entries = await sheets_service.get_prayer_entries()
        return entries
    except Exception as e:
        logging.error(f"Erro ao recuperar orações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/prayers/stats", response_model=PrayerStats)
async def get_prayer_stats():
    """Calcula estatísticas das orações"""
    try:
        total_hours = await sheets_service.calculate_total_hours()
        entries = await sheets_service.get_prayer_entries()
        total_entries = len(entries)
        
        # Meta de 1000 horas
        goal_hours = 1000
        progress_percentage = min((total_hours / goal_hours) * 100, 100)
        
        return PrayerStats(
            total_hours=total_hours,
            total_entries=total_entries,
            progress_percentage=progress_percentage
        )
    except Exception as e:
        logging.error(f"Erro ao calcular estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Rotas originais (mantendo para compatibilidade)
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Banco de dados não configurado")
    
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if db is None:
        return []
    
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
