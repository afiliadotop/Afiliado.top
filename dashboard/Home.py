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
