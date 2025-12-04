"""
Cliente Supabase para o dashboard
"""
import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Any
import pandas as pd

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """Inicializa e retorna o cliente Supabase"""
    
    # Tenta carregar do secrets do Streamlit
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    except:
        # Fallback para variáveis de ambiente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("""
        ❌ **Configuração do Supabase não encontrada!**
        
        Configure as variáveis no Streamlit Cloud:
        1. Acesse https://share.streamlit.io/
        2. Seu app → Settings → Secrets
        3. Adicione:
           - SUPABASE_URL
           - SUPABASE_KEY
        """)
        return None
    
    try:
        # Configura opções do cliente
        from supabase.lib.client_options import ClientOptions
        
        options = ClientOptions(
            postgrest_client_timeout=30,
            storage_client_timeout=30,
            schema="public",
            headers={
                "X-Client-Info": "afiliadohub-dashboard/1.0.0"
            }
        )
        
        client = create_client(supabase_url, supabase_key, options=options)
        
        # Testa a conexão
        test_response = client.table("products").select("count", count="exact").limit(1).execute()
        
        return client
        
    except Exception as e:
        st.error(f"""
        ❌ **Erro ao conectar ao Supabase:**
        
        {str(e)}
        
        **Verifique:**
        1. Se o projeto Supabase está ativo
        2. Se as credenciais estão corretas
        3. Se a tabela 'products' existe
        """)
        return None

def get_products_dataframe(filters: Dict[str, Any] = None, limit: int = 1000) -> pd.DataFrame:
    """Busca produtos como DataFrame"""
    try:
        client = get_supabase_client()
        if not client:
            return pd.DataFrame()
        
        query = client.table("products").select("*")
        
        # Aplica filtros
        if filters:
            if filters.get("store"):
                query = query.eq("store", filters["store"])
            if filters.get("category"):
                query = query.ilike("category", f"%{filters['category']}%")
            if filters.get("min_price"):
                query = query.gte("current_price", filters["min_price"])
            if filters.get("max_price"):
                query = query.lte("current_price", filters["max_price"])
            if filters.get("min_discount"):
                query = query.gte("discount_percentage", filters["min_discount"])
            if filters.get("active_only", True):
                query = query.eq("is_active", True)
        
        # Ordena e limita
        query = query.order("created_at", desc=True).limit(limit)
        
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Converte datas
            date_columns = ['created_at', 'updated_at', 'last_checked', 'expires_at', 'coupon_expiry']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            
            return df
        else:
            return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

def get_daily_stats(date: str = None) -> Dict[str, Any]:
    """Busca estatísticas do dia"""
    try:
        client = get_supabase_client()
        if not client:
            return {}
        
        if not date:
            from datetime import datetime
            date = datetime.now().date().isoformat()
        
        # Produtos adicionados hoje
        added_response = client.table("products")\
            .select("count", count="exact")\
            .gte("created_at", f"{date}T00:00:00")\
            .lte("created_at", f"{date}T23:59:59")\
            .execute()
        
        # Envios hoje
        sends_response = client.table("product_stats")\
            .select("telegram_send_count")\
            .gte("last_sent", f"{date}T00:00:00")\
            .lte("last_sent", f"{date}T23:59:59")\
            .execute()
        
        sends_today = sum([s.get('telegram_send_count', 0) for s in sends_response.data]) \
            if sends_response.data else 0
        
        return {
            "date": date,
            "products_added": added_response.count or 0,
            "telegram_sends": sends_today
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_store_summary() -> Dict[str, Any]:
    """Resumo por loja"""
    try:
        client = get_supabase_client()
        if not client:
            return {}
        
        # Contagem por loja
        response = client.table("products")\
            .select("store, count, current_price, discount_percentage")\
            .eq("is_active", True)\
            .group("store")\
            .execute()
        
        if not response.data:
            return {}
        
        summary = {}
        for item in response.data:
            store = item["store"]
            summary[store] = {
                "count": item["count"],
                "avg_price": item.get("current_price", 0),
                "avg_discount": item.get("discount_percentage", 0)
            }
        
        return summary
        
    except Exception as e:
        return {"error": str(e)}

def insert_product(product_data: Dict[str, Any]) -> bool:
    """Insere um novo produto"""
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        response = client.table("products").insert(product_data).execute()
        return len(response.data) > 0
        
    except Exception as e:
        st.error(f"Erro ao inserir produto: {e}")
        return False

def update_product(product_id: int, update_data: Dict[str, Any]) -> bool:
    """Atualiza um produto"""
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        response = client.table("products")\
            .update(update_data)\
            .eq("id", product_id)\
            .execute()
        
        return len(response.data) > 0
        
    except Exception as e:
        st.error(f"Erro ao atualizar produto: {e}")
        return False

def delete_product(product_id: int, soft_delete: bool = True) -> bool:
    """Remove um produto"""
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        if soft_delete:
            response = client.table("products")\
                .update({"is_active": False})\
                .eq("id", product_id)\
                .execute()
        else:
            response = client.table("products")\
                .delete()\
                .eq("id", product_id)\
                .execute()
        
        return len(response.data) > 0
        
    except Exception as e:
        st.error(f"Erro ao remover produto: {e}")
        return False
