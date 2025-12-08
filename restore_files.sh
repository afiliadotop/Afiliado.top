#!/bin/bash
echo "🚑 Iniciando Restauração de Arquivos Faltantes..."

# 1. Restaurar api/main.py (Baseado no seu index.py)
echo "📝 Criando api/main.py..."
cat << 'PYTHON' > api/main.py
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
PYTHON

# 2. Restaurar api/handlers/products.py
echo "📝 Criando api/handlers/products.py..."
cat << 'PYTHON' > api/handlers/products.py
import logging
from typing import Dict, List, Any, Optional
from api.utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)
db = get_supabase_manager()

async def add_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = db.client.table("products").insert(product_data).execute()
        return {"success": True, "product": response.data[0] if response.data else {}}
    except Exception as e:
        logger.error(f"Erro DB: {e}")
        return {"success": False, "error": str(e)}

async def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    try:
        response = db.client.table("products").select("*").eq("id", product_id).single().execute()
        return response.data
    except Exception:
        return None

async def search_products(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    return await db.get_products(filters)

async def get_random_product(min_discount: int = 0) -> Optional[Dict[str, Any]]:
    return await db.get_random_product(min_discount)
PYTHON

# 3. Restaurar dashboard/Home.py (Baseado no seu main.py)
echo "📝 Criando dashboard/Home.py..."
cat << 'PYTHON' > dashboard/Home.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Ajuste de path para importar módulos da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard.utils.supabase_client import get_supabase_client
from dashboard.components.header import show_header
from dashboard.components.sidebar import show_sidebar

st.set_page_config(
    page_title="AfiliadoHub - Painel Administrativo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    show_header()
    show_sidebar()
    
    st.markdown("## 📊 Dashboard Geral")
    
    supabase = get_supabase_client()
    if not supabase:
        st.error("Erro ao conectar ao Supabase.")
        return

    # Métricas Rápidas
    col1, col2, col3 = st.columns(3)
    
    try:
        count = supabase.table("products").select("count", count="exact").eq("is_active", True).execute().count
        col1.metric("📦 Produtos Ativos", count)
    except:
        col1.metric("📦 Produtos Ativos", 0)
        
    # Mais lógica de dashboard aqui...
    st.info("Bem-vindo ao AfiliadoHub Admin. Use o menu lateral para navegar.")

if __name__ == "__main__":
    main()
PYTHON

# 4. Restaurar scripts/monitor.py (Move ou Recria)
if [ -f "monitor.py" ]; then
    echo "📦 Movendo monitor.py da raiz para scripts/..."
    mv monitor.py scripts/
else
    echo "⚠️ monitor.py não encontrado na raiz. Você precisará baixar novamente se não estiver em scripts/."
fi

# 5. Restaurar scripts/backup.py (Recriação básica baseada no seu envio)
echo "📝 Criando scripts/backup.py..."
cat << 'PYTHON' > scripts/backup.py
#!/usr/bin/env python3
import sys
import os
# Adiciona raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils.supabase_client import get_supabase_manager
import json
from datetime import datetime

async def main():
    print("💾 Iniciando Backup...")
    db = get_supabase_manager()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup Produtos
    try:
        data = db.client.table("products").select("*").execute()
        filename = f"backups/products_{timestamp}.json"
        os.makedirs("backups", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data.data, f)
        print(f"✅ Backup salvo: {filename}")
    except Exception as e:
        print(f"❌ Erro no backup: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
PYTHON

# 6. Restaurar scripts/shopee_scraper.py (Placeholder funcional)
echo "📝 Criando scripts/shopee_scraper.py..."
cat << 'PYTHON' > scripts/shopee_scraper.py
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopeeScraper:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def update_daily_products(self):
        logger.info("🕷️ Simulando Scraping da Shopee...")
        await asyncio.sleep(1)
        return []

async def main():
    async with ShopeeScraper() as scraper:
        await scraper.update_daily_products()

if __name__ == "__main__":
    asyncio.run(main())
PYTHON

# 7. Corrigir Avisos (.env e gitignore)
echo "🔧 Preenchendo .env.example e .gitignore..."
cat << 'EOF' > .env.example
# Configurações do Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica-anon
SUPABASE_SERVICE_KEY=sua-chave-secreta-service-role

# Configurações do Telegram
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Configurações da API
ADMIN_API_KEY=sua-chave-admin-segura
