import os
import logging
from datetime import datetime
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from telegram import Bot, Update

# Imports locais corrigidos
from api.handlers.commission import CommissionSystem
# from api.handlers.competition_analysis import CompetitionAnalyzer (se existir)
# from api.handlers.advanced_analytics import AdvancedAnalytics (se existir)
# from api.handlers.export_reports import ReportExporter (se existir)
from api.handlers.products import add_product, search_products, get_random_product

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AfiliadoHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN) if BOT_TOKEN else None

@app.get("/")
async def root():
    return {"status": "online", "service": "AfiliadoHub API", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "telegram": "connected" if bot else "disconnected"}

# --- Rotas de Produtos ---
class ProductCreate(BaseModel):
    store: str
    name: str
    affiliate_link: str
    current_price: float

@app.post("/api/products")
async def create_product_endpoint(product: ProductCreate):
    try:
        result = await add_product(product.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
async def get_products_endpoint(store: Optional[str] = None, limit: int = 50):
    filters = {"store": store, "limit": limit}
    return await search_products(filters)

# --- Webhook Telegram ---
@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        if bot:
            update = Update.de_json(data, bot)
            # Aqui entraria a lógica do bot processar o update
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro webhook: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
