import streamlit as st
import sys
import os

# --- Ajuste de Path (Crucial para não dar erro de import) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir)) # Raiz afiliadohub
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

st.set_page_config(
    page_title="Dashboard - AfiliadoHub",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Dashboard Principal")

st.markdown("""
### 📊 Visão Geral do Sistema

Bem-vindo ao painel central do **AfiliadoHub**. Aqui você gerencia toda sua operação de afiliado.

#### 🎯 Status Rápido:
""")

# Exemplo de métricas (Placeholder - Futuramente conectar com Supabase)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Produtos Ativos", "150", "+12")
col2.metric("Vendas Hoje", "5", "+2")
col3.metric("Cliques no Bot", "1,234", "+5%")
col4.metric("Comissão Estimada", "R$ 450,00", "+10%")

st.markdown("""
---
#### 🚀 Acesso Rápido:

1. **📦 Gerenciamento de Produtos**: Adicione, edite ou remova links de afiliados.
2. **🤖 Automação Telegram**: Configure o envio automático para seus canais.
3. **🔄 Importação**: Suba planilhas CSV com centenas de produtos de uma vez.

Use o menu lateral (Sidebar) para navegar entre as ferramentas.
""")
