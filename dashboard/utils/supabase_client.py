import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
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
        st.error("❌ Configuração do Supabase não encontrada!")
        st.info("Configure as variáveis SUPABASE_URL e SUPABASE_KEY")
        return None
    
    try:
        client = create_client(supabase_url, supabase_key)
        
        # Testa a conexão
        client.table("products").select("count", count="exact").limit(1).execute()
        
        return client
        
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        return None

def get_import_settings():
    """Busca configurações de importação"""
    client = get_supabase_client()
    if client:
        try:
            response = client.table("settings")\
                .select("value")\
                .eq("key", "import_settings")\
                .execute()
            
            if response.data:
                return response.data[0]["value"]
        except:
            pass
    
    # Configurações padrão
    return {
        "max_file_size_mb": 100,
        "default_store": "shopee",
        "auto_approve": True,
        "deduplicate": True,
        "validate_links": True,
        "batch_size": 100,
        "delay_between_batches": 1
    }
