import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show_sidebar():
    """Componente de sidebar do dashboard"""
    
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1E3A8A;">🚀</h1>
            <h3 style="color: #1E3A8A; margin: 0;">AfiliadoHub</h3>
            <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Dashboard Admin</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navegação
        st.markdown("### 📁 Navegação")
        
        # Mapeamento de páginas
        pages = [
            {"icon": "🏠", "name": "Dashboard", "page": "1_🏠_Dashboard.py"},
            {"icon": "📦", "name": "Produtos", "page": "2_📦_Produtos.py"},
            {"icon": "📊", "name": "Estatísticas", "page": "3_📊_Estatísticas.py"},
            {"icon": "🔄", "name": "Importar", "page": "4_🔄_Importar.py"},
            {"icon": "🤖", "name": "Telegram", "page": "5_🤖_Telegram.py"},
            {"icon": "⚙️", "name": "Configurações", "page": "6_⚙️_Configurações.py"}
        ]
        
        current_page = st.session_state.get("current_page", "1_🏠_Dashboard.py")
        
        for page in pages:
            # Botão de navegação
            if st.button(
                f"{page['icon']} {page['name']}",
                key=f"nav_{page['page']}",
                use_container_width=True,
                type="primary" if current_page == page['page'] else "secondary"
            ):
                st.session_state["current_page"] = page['page']
                st.switch_page(f"pages/{page['page']}")
        
        st.markdown("---")
        
        # Estatísticas rápidas
        st.markdown("### 📊 Status Rápido")
        
        try:
            from dashboard.utils.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            # Total de produtos
            response = supabase.table("products").select("count", count="exact").eq("is_active", True).execute()
            total_products = response.count or 0
            
            # Produtos hoje
            today = datetime.now().date().isoformat()
            response = supabase.table("products")\
                .select("count", count="exact")\
                .gte("created_at", f"{today}T00:00:00")\
                .execute()
            today_products = response.count or 0
            
            # Envios hoje
            response = supabase.table("product_stats")\
                .select("telegram_send_count")\
                .gte("last_sent", f"{today}T00:00:00")\
                .execute()
            sends_today = sum([s.get('telegram_send_count', 0) for s in response.data]) if response.data else 0
            
            # Métricas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📦 Produtos", f"{total_products:,}")
            with col2:
                st.metric("🆕 Hoje", today_products)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🤖 Envios", sends_today)
            with col2:
                # Taxa de crescimento (simulado)
                growth = "+12%"
                st.metric("📈 Cresc.", growth)
            
        except Exception as e:
            st.error("Erro ao carregar dados")
        
        st.markdown("---")
        
        # Ações rápidas
        st.markdown("### ⚡ Ações Rápidas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🆕 Add Produto", use_container_width=True):
                st.session_state["current_page"] = "2_📦_Produtos.py"
                st.switch_page("pages/2_📦_Produtos.py")
        
        with col2:
            if st.button("📤 Enviar Agora", use_container_width=True):
                st.info("Enviando promoção...")
                # Lógica para envio imediato
        
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Informações do sistema
        st.markdown("### ℹ️ Sistema")
        
        st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.caption("🌐 AfiliadoHub v1.0.0")
        st.caption("⚡ Status: Online")
        
        # Logout
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            st.success("Até logo!")
            # Aqui você implementaria a lógica de logout
            st.stop()
