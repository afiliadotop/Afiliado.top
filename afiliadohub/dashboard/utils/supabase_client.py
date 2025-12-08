import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Any
import pandas as pd

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """Inicializa e retorna o cliente Supabase (Versão Simplificada)"""
    
    # 1. Tenta carregar do secrets do Streamlit
    try:
        # Tenta pegar da raiz (como corrigimos antes)
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    except Exception:
        # 2. Fallback para variáveis de ambiente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Credenciais do Supabase não encontradas em .streamlit/secrets.toml ou .env")
        return None
    
    try:
        # --- CORREÇÃO AQUI: Conexão direta sem ClientOptions complexos ---
        client = create_client(supabase_url, supabase_key)
        
        return client
        
    except Exception as e:
        st.error(f"❌ Erro crítico ao conectar ao Supabase: {e}")
        return None

# --- Funções Auxiliares mantidas para compatibilidade ---

def get_products_dataframe(filters: Dict[str, Any] = None, limit: int = 1000) -> pd.DataFrame:
    """Busca produtos como DataFrame"""
    client = get_supabase_client()
    if not client: return pd.DataFrame()
    
    try:
        query = client.table("products").select("*")
        
        if filters:
            if filters.get("store"): query = query.eq("store", filters["store"])
            if filters.get("category"): query = query.ilike("category", f"%{filters['category']}%")
            if filters.get("active_only", True): query = query.eq("is_active", True)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

def get_daily_stats(date: str = None) -> Dict[str, Any]:
    return {} # Placeholder para evitar erro de importação

def get_store_summary() -> Dict[str, Any]:
    return {} # Placeholder

def insert_product(product_data: Dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client: return False
    try:
        client.table("products").insert(product_data).execute()
        return True
    except Exception:
        return False

def update_product(product_id: int, update_data: Dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client: return False
    try:
        client.table("products").update(update_data).eq("id", product_id).execute()
        return True
    except Exception:
        return False

def delete_product(product_id: int, soft_delete: bool = True) -> bool:
    client = get_supabase_client()
    if not client: return False
    try:
        if soft_delete:
            client.table("products").update({"is_active": False}).eq("id", product_id).execute()
        else:
            client.table("products").delete().eq("id", product_id).execute()
        return True
    except Exception:
        return False
