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
