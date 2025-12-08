import streamlit as st
import sys
import os

# --- CORREÇÃO DE PATH CRÍTICA ---
# Pega o caminho absoluto da pasta onde este arquivo (Home.py) está
current_dir = os.path.dirname(os.path.abspath(__file__))

# Adiciona essa pasta ao sistema de imports do Python
# Isso permite que 'from utils' e 'from components' funcionem, 
# pois eles estão na mesma pasta que o Home.py
if current_dir not in sys.path:
    sys.path.append(current_dir)

from utils.supabase_client import get_supabase_client
from components.header import show_header
from components.sidebar import show_sidebar

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
        st.stop()

    # Métricas Rápidas
    col1, col2, col3 = st.columns(3)
    
    try:
        count_response = supabase.table("products").select("count", count="exact").eq("is_active", True).execute()
        count = count_response.count if count_response else 0
        col1.metric("📦 Produtos Ativos", count)
    except Exception as e:
        col1.metric("📦 Produtos Ativos", "Off")
        # st.caption(f"Erro: {e}")

    st.info("👋 Bem-vindo ao AfiliadoHub! Use o menu lateral para navegar.")

if __name__ == "__main__":
    main()
