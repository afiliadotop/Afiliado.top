import streamlit as st
import asyncio
from api.handlers.advanced_analytics import AdvancedAnalytics
from api.handlers.export_reports import ReportExporter

# Configuração da página
st.set_page_config(page_title="AfiliadoHub Admin", layout="wide")

st.title("🚀 AfiliadoHub - Command Center")

# Instancia as classes de lógica
analytics = AdvancedAnalytics()

# --- ABA DE RELATÓRIOS ---
tab1, tab2 = st.tabs(["📊 Funil & Stats", "📥 Exportar Relatórios"])

with tab1:
    st.header("Performance do Negócio")
    
    # Executa função assíncrona no Streamlit
    days = st.slider("Período (dias)", 7, 90, 30)
    
    # Loop assíncrono para buscar dados
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    funnel_data = loop.run_until_complete(analytics.get_sales_funnel_analysis(days=days))
    
    if "error" not in funnel_data:
        col1, col2, col3 = st.columns(3)
        col1.metric("Produtos Adicionados", funnel_data['funnel']['products_added'])
        col2.metric("Produtos Visualizados", funnel_data['funnel']['products_viewed'])
        col3.metric("Vendas Totais", f"R$ {funnel_data['funnel']['total_sales']:.2f}")
        
        # Gráfico do Funil
        st.subheader("Funil de Conversão")
        funnel_dict = funnel_data['funnel']
        st.bar_chart({
            "Adicionados": funnel_dict['products_added'],
            "Visualizados": funnel_dict['products_viewed'],
            "Clicados": funnel_dict['products_clicked'],
            "Vendidos": funnel_dict['products_sold']
        })
    else:
        st.error(f"Erro ao carregar dados: {funnel_data.get('error')}")

with tab2:
    st.header("Gerar Relatórios PDF/Excel")
    exporter = ReportExporter()
    
    col1, col2 = st.columns(2)
    if col1.button("📄 Baixar Relatório PDF"):
        # Lógica para gerar e oferecer download
        pass
