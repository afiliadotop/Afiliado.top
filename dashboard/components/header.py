import streamlit as st
from datetime import datetime

def show_header():
    """Componente de cabeçalho do dashboard"""
    
    # CSS personalizado para o header
    st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            color: white;
        }
        .header-title {
            font-size: 2.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .header-subtitle {
            font-size: 1rem;
            opacity: 0.9;
        }
        .status-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header HTML
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🚀 AfiliadoHub Dashboard</div>
        <div class="header-subtitle">
            Sistema Completo de Gestão de Afiliados | {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
        
        <div style="margin-top: 1rem;">
            <span class="status-badge">✅ Online</span>
            <span class="status-badge">📊 {get_product_count()} Produtos</span>
            <span class="status-badge">🏪 7 Lojas</span>
            <span class="status-badge">🤖 Bot Ativo</span>
            <span class="status-badge">⚡ v1.0.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_product_count():
    """Obtém contagem de produtos (mock por enquanto)"""
    try:
        from dashboard.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        response = supabase.table("products").select("count", count="exact").execute()
        return f"{response.count:,}"
    except:
        return "N/A"
