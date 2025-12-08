#!/bin/bash
echo "🔧 Criando os 3 arquivos faltantes..."

# 1. Recriar api/main.py
echo "📝 Criando api/main.py..."
cat << 'PYTHON' > api/main.py
import os
import logging
from datetime import datetime
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from telegram import Bot, Update

# Imports locais
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
    return {"status": "healthy"}

# --- Rotas de Produtos ---
class ProductCreate(BaseModel):
    store: str
    name: str
    affiliate_link: str
    current_price: float
    # Adicione outros campos opcionais conforme seu modelo

@app.post("/api/products")
async def create_product_endpoint(product: ProductCreate):
    try:
        # Converte modelo Pydantic para dict
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
            # Lógica de processamento do bot aqui
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro webhook: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
PYTHON

# 2. Recriar dashboard/Home.py
echo "📝 Criando dashboard/Home.py..."
cat << 'PYTHON' > dashboard/Home.py
import streamlit as st
import sys
import os

# Ajuste crítico de path para importar módulos da raiz
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
        st.error("Erro ao conectar ao Supabase. Verifique .streamlit/secrets.toml ou .env")
        return

    # Exemplo de métrica rápida
    col1, col2, col3 = st.columns(3)
    
    try:
        count_response = supabase.table("products").select("count", count="exact").eq("is_active", True).execute()
        count = count_response.count if count_response else 0
        col1.metric("📦 Produtos Ativos", count)
    except Exception as e:
        col1.metric("📦 Produtos Ativos", "Erro")
        st.warning(f"Não foi possível conectar ao banco: {e}")

    st.info("👋 Bem-vindo ao AfiliadoHub! Utilize o menu lateral para navegar entre as funcionalidades.")

if __name__ == "__main__":
    main()
PYTHON

# 3. Recriar .gitignore
echo "📝 Criando .gitignore..."
cat << 'GITIGNORE' > .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env
.env.production
.streamlit/secrets.toml
logs/
backups/
.DS_Store
GITIGNORE

echo "✅ Arquivos criados com sucesso!"
