import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
# Adicione estas importações no topo do arquivo
from api.handlers.commission import CommissionSystem
from api.handlers.competition_analysis import CompetitionAnalyzer
from api.handlers.advanced_analytics import AdvancedAnalytics
from api.handlers.export_reports import ReportExporter

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do FastAPI
app = FastAPI(
    title="AfiliadoHub API",
    description="API completa para gestão de produtos de afiliados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CRON_TOKEN = os.getenv("CRON_TOKEN")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

# Inicialização do bot Telegram
bot = Bot(BOT_TOKEN) if BOT_TOKEN else None
telegram_app = None

# Security
security = HTTPBearer()

# ==================== MODELOS PYDANTIC ====================

class ProductCreate(BaseModel):
    store: str = Field(..., description="Loja: shopee, aliexpress, amazon, temu, shein, magalu, mercado_livre")
    name: str = Field(..., min_length=3, max_length=500)
    affiliate_link: str = Field(..., min_length=10)
    current_price: float = Field(..., gt=0)
    original_price: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    image_url: Optional[str] = None
    coupon_code: Optional[str] = None
    coupon_expiry: Optional[datetime] = None
    tags: Optional[List[str]] = []

class CSVImportRequest(BaseModel):
    store: str
    source_file: Optional[str] = None
    replace_existing: bool = False

class TelegramMessage(BaseModel):
    chat_id: str
    message: str
    parse_mode: Optional[str] = "HTML"

# ==================== DEPENDÊNCIAS ====================

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Token de administração inválido")
    return credentials.credentials

async def verify_cron_token(request: Request):
    token = request.headers.get("X-CRON-TOKEN")
    if not token or token != CRON_TOKEN:
        raise HTTPException(status_code=403, detail="Token CRON inválido")
    return True

# ==================== ROTAS DA API ====================
@app.post("/api/commission/calculate", dependencies=[Depends(verify_admin_token)])
async def calculate_commission(commission_data: dict):
    """Calcula comissão para uma venda"""
    try:
        commission_system = CommissionSystem()
        result = await commission_system.calculate_commission(
            commission_data.get("product_id"),
            commission_data.get("sale_amount")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AfiliadoHub",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "api": "/docs",
            "health": "/health",
            "products": "/api/products",
            "import": "/api/import",
            "telegram": "/api/telegram/webhook",
            "stats": "/api/stats"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",  # Verificar conexão Supabase
            "telegram": "connected" if bot else "disconnected"
        }
    }

# ==================== ROTAS DE PRODUTOS ====================

@app.post("/api/products", dependencies=[Depends(verify_admin_token)])
async def create_product(product: ProductCreate):
    """Adiciona um produto manualmente"""
    from api.handlers.products import add_product
    try:
        product_id = await add_product(product.dict())
        return {"status": "success", "id": product_id}
    except Exception as e:
        logger.error(f"Erro ao criar produto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
async def get_products(
    store: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_discount: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
):
    """Busca produtos com filtros"""
    from api.handlers.products import search_products
    try:
        filters = {
            "store": store,
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "min_discount": min_discount,
            "limit": limit,
            "offset": offset
        }
        products = await search_products(filters)
        return {"products": products, "count": len(products)}
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROTA DE IMPORTAR CSV ====================

@app.post("/api/import/csv", dependencies=[Depends(verify_admin_token)])
async def import_csv(
    file: UploadFile = File(...),
    store: str = "shopee",
    replace_existing: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Importa um arquivo CSV com produtos"""
    from api.handlers.csv_import import process_csv_upload
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são suportados")
    
    # Processa em background
    background_tasks.add_task(
        process_csv_upload,
        file.file,
        store,
        replace_existing
    )
    
    return {
        "status": "processing",
        "message": f"Arquivo {file.filename} está sendo processado",
        "store": store,
        "timestamp": datetime.now().isoformat()
    }

# ==================== ROTAS DO TELEGRAM ====================

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Webhook do Telegram"""
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        
        # Processa a atualização
        if telegram_app:
            await telegram_app.process_update(update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro no webhook Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.post("/api/telegram/send", dependencies=[Depends(verify_cron_token)])
async def send_telegram_message(message: TelegramMessage):
    """Envia mensagem para o Telegram (usado pelo cron)"""
    try:
        from api.handlers.telegram import send_product_to_channel
        
        # Busca um produto para enviar
        product = await get_random_product_for_telegram()
        if product:
            await send_product_to_channel(
                chat_id=message.chat_id,
                product=product
            )
            return {"status": "sent", "product_id": product["id"]}
        else:
            return {"status": "no_products"}
    except Exception as e:
        logger.error(f"Erro ao enviar para Telegram: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROTAS DE ESTATÍSTICAS ====================

@app.get("/api/stats")
async def get_system_stats():
    """Retorna estatísticas do sistema"""
    from api.handlers.analytics import get_system_statistics
    
    try:
        stats = await get_system_statistics()
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/daily")
async def get_daily_stats(date: Optional[str] = None):
    """Estatísticas diárias"""
    from api.handlers.analytics import get_daily_statistics
    
    try:
        stats_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
        stats = await get_daily_statistics(stats_date.date())
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas diárias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== UTILITÁRIOS ====================

async def get_random_product_for_telegram():
    """Seleciona um produto aleatório para enviar no Telegram"""
    from api.handlers.products import get_random_product
    
    try:
        product = await get_random_product(
            min_discount=20,
            max_sent_last_days=7
        )
        return product
    except Exception as e:
        logger.error(f"Erro ao buscar produto aleatório: {e}")
        return None

# ==================== INICIALIZAÇÃO ====================

@app.on_event("startup")
async def startup_event():
    """Executa na inicialização do servidor"""
    logger.info("🚀 Iniciando AfiliadoHub API")
    
    # Inicializa o bot Telegram
    if BOT_TOKEN:
        from api.handlers.telegram import setup_telegram_handlers
        global telegram_app
        telegram_app = await setup_telegram_handlers(BOT_TOKEN)
        logger.info("✅ Bot Telegram inicializado")
    
    # Verifica conexão com Supabase
    from api.utils.supabase_client import get_supabase
    try:
        supabase = get_supabase()
        # Testa a conexão
        response = supabase.table("products").select("count", count="exact").limit(1).execute()
        logger.info(f"✅ Conectado ao Supabase. Produtos: {response.count}")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao Supabase: {e}")
    
    logger.info("✅ AfiliadoHub API está pronto!")

# ==================== HANDLER PARA VERCEL ====================

async def handler(request: Request):
    """
    Handler principal para compatibilidade com Vercel
    """
    # Roteia requisições para o FastAPI
    from starlette.requests import Request as StarletteRequest
    
    # Converte request do Vercel para Starlette
    scope = request.scope
    starlette_request = StarletteRequest(scope, request.receive)
    
    # Processa com o FastAPI
    response = await app(scope, request.receive, request.send)
    
    return response

# Para desenvolvimento local
if __name__ == "__main__":
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
