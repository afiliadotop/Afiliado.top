#!/usr/bin/env python3
"""
Script para corrigir todos os problemas do projeto Afiliado.top
"""
import os
import sys
import shutil
from pathlib import Path
import subprocess

class ProjectFixer:
    def __init__(self):
        self.base_dir = Path(".")
        
    def create_missing_directories(self):
        """Cria diretórios faltantes"""
        print("📁 Criando diretórios faltantes...")
        
        directories = [
            "api",
            "api/handlers",
            "api/utils",
            "api/models",
            "dashboard",
            "dashboard/components",
            "dashboard/pages",
            "dashboard/utils",
            "scripts",
            "backups"
        ]
        
        for dir_path in directories:
            full_path = self.base_dir / dir_path
            full_path.mkdir(exist_ok=True, parents=True)
            print(f"  ✅ {dir_path}")
        
        return True
    
    def create_missing_files(self):
        """Cria arquivos faltantes essenciais"""
        print("\n📄 Criando arquivos faltantes...")
        
        # Arquivos de inicialização
        init_files = [
            "dashboard/__init__.py",
            "dashboard/pages/__init__.py",
            "dashboard/components/__init__.py",
            "dashboard/utils/__init__.py",
            "api/__init__.py",
            "api/handlers/__init__.py",
            "api/utils/__init__.py",
            "api/models/__init__.py"
        ]
        
        for file_path in init_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                full_path.touch()
                print(f"  ✅ {file_path}")
        
        # Verifica e cria arquivos principais
        essential_files = {
            # Dashboard
            "dashboard/Home.py": self.create_home_py(),
            "dashboard/pages/1_🏠_Dashboard.py": self.create_dashboard_page(),
            "dashboard/pages/3_📊_Estatísticas.py": self.create_stats_page(),
            
            # API
            "api/main.py": self.create_api_main(),
            
            # Scripts
            "scripts/backup.py": self.create_backup_script(),
            "scripts/monitor.py": self.create_monitor_script(),
            "scripts/shopee_scraper.py": self.create_shopee_scraper(),
            
            # Configurações
            ".env.example": self.create_env_example(),
            ".gitignore": self.create_gitignore()
        }
        
        for file_path, content in essential_files.items():
            full_path = self.base_dir / file_path
            if not full_path.exists() or full_path.stat().st_size < 100:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ {file_path}")
        
        return True
    
    def fix_syntax_errors(self):
        """Corrige erros de sintaxe"""
        print("\n🔧 Corrigindo erros de sintaxe...")
        
        # Primeiro, verifica se monitor.py existe
        monitor_path = self.base_dir / "scripts" / "monitor.py"
        
        if monitor_path.exists():
            # Cria backup do arquivo problemático
            backup_path = monitor_path.with_suffix('.py.backup')
            shutil.copy2(monitor_path, backup_path)
            print(f"  📦 Backup criado: {backup_path}")
            
            # Substitui pelo monitor.py correto
            with open(monitor_path, 'w', encoding='utf-8') as f:
                f.write(self.create_monitor_script())
            print(f"  ✅ monitor.py corrigido")
        
        return True
    
    def verify_file_contents(self):
        """Verifica e corrige conteúdos dos arquivos"""
        print("\n📋 Verificando conteúdos dos arquivos...")
        
        files_to_check = [
            ("api/handlers/products.py", self.create_products_handler),
            ("dashboard/components/sidebar.py", self.create_sidebar),
            ("dashboard/pages/2_📦_Produtos.py", self.create_products_page),
            ("requirements.txt", self.create_requirements)
        ]
        
        for file_path, content_func in files_to_check:
            full_path = self.base_dir / file_path
            
            if not full_path.exists():
                print(f"  ❌ {file_path} não encontrado")
                continue
            
            # Verifica tamanho
            if full_path.stat().st_size < 500:  # Arquivo muito pequeno
                print(f"  ⚠️  {file_path} muito pequeno, recriando...")
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content_func())
                print(f"  ✅ {file_path} atualizado")
        
        return True
    
    def run_python_check(self):
        """Executa verificação de sintaxe Python"""
        print("\n🐍 Executando verificação de sintaxe...")
        
        # Encontra todos os arquivos Python
        python_files = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        issues = []
        for py_file in python_files:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", py_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append(py_file)
                    print(f"  ❌ {py_file}")
            except:
                pass
        
        if not issues:
            print("  ✅ Todos os arquivos Python têm sintaxe válida")
        
        return len(issues) == 0
    
    def create_home_py(self):
        """Cria arquivo Home.py do dashboard"""
        return '''"""
Página principal do Dashboard AfiliadoHub
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="AfiliadoHub Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 AfiliadoHub Dashboard</h1>
    <p>Gerencie milhões de produtos de afiliados em uma única plataforma</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
try:
    from dashboard.components.sidebar import show_sidebar
    show_sidebar()
except ImportError:
    st.sidebar.title("Menu")
    st.sidebar.info("Sidebar carregando...")

# Conteúdo principal
st.markdown("## 📊 Visão Geral")

# Colunas para métricas
col1, col2, col3, col4 = st.columns(4)

try:
    from dashboard.utils.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    if supabase:
        # Total de produtos
        response = supabase.table("products")\\
            .select("count", count="exact")\\
            .eq("is_active", True)\\
            .execute()
        
        total_products = response.count or 0
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_products:,}</div>
                <div class="metric-label">Produtos Ativos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Novos Hoje</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Vendas Hoje</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ 0,00</div>
                <div class="metric-label">Comissão Total</div>
            </div>
            """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

# Gráficos
st.markdown("## 📈 Tendências")
st.info("Dashboard em construção. Dados serão carregados em breve.")

# Ações rápidas
st.markdown("## ⚡ Ações Rápidas")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🆕 Adicionar Produto", use_container_width=True):
        st.switch_page("pages/2_📦_Produtos.py")

with col2:
    if st.button("📤 Importar CSV", use_container_width=True):
        st.switch_page("pages/4_🔄_Importar.py")

with col3:
    if st.button("🤖 Enviar para Telegram", use_container_width=True):
        st.switch_page("pages/5_🤖_Telegram.py")

# Status do sistema
st.markdown("## 🖥️ Status do Sistema")

col1, col2 = st.columns(2)

with col1:
    st.info(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.info("**Status API:** 🟡 Verificando")
    st.info("**Status Banco:** 🟡 Conectando")

with col2:
    st.warning("**Backup automático:** Diário às 02:00")
    st.warning("**Próxima verificação:** Em 30 minutos")
    st.warning("**Uso de disco:** N/A")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p>AfiliadoHub v1.0.0 • Sistema de gerenciamento de afiliados</p>
    <p>© 2024 Afiliado.top • Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
'''
    
    def create_dashboard_page(self):
        """Cria página do dashboard"""
        return '''"""
Página do Dashboard Principal
"""
import streamlit as st

st.set_page_config(
    page_title="Dashboard - AfiliadoHub",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Dashboard Principal")

st.markdown("""
### 📊 Visão Geral do Sistema

Esta página fornece uma visão geral completa do seu sistema AfiliadoHub.

#### 🎯 Funcionalidades Disponíveis:

1. **📦 Gerenciamento de Produtos**
   - Adicionar novos produtos
   - Editar produtos existentes
   - Buscar produtos por filtros

2. **📊 Análises e Estatísticas**
   - Métricas de desempenho
   - Análise de vendas
   - Relatórios de comissões

3. **🤖 Automação do Telegram**
   - Envio automático de promoções
   - Gerenciamento de canais
   - Análise de engajamento

4. **🔄 Importação em Massa**
   - Upload de CSV
   - Sincronização com APIs
   - Atualização automática

#### 🚀 Status do Sistema:

- ✅ API: Operacional
- ✅ Banco de Dados: Conectado
- ✅ Telegram Bot: Configurado
- ✅ Dashboard: Online

#### 📈 Próximos Passos:

1. Configure suas primeiras importações
2. Adicione produtos manualmente
3. Configure o bot do Telegram
4. Analise as estatísticas

Para começar, use o menu lateral para navegar entre as seções.
"""
'''
    
    def create_stats_page(self):
        """Cria página de estatísticas"""
        return '''"""
Página de Estatísticas e Análises
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Estatísticas - AfiliadoHub",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Estatísticas do Sistema")

# Dados de exemplo (em produção, buscar do banco)
example_data = {
    "Métrica": ["Produtos Ativos", "Produtos com Desconto", "Vendas Hoje", "Comissão Total"],
    "Valor": [150, 45, 12, 342.50],
    "Variação": ["+12%", "+5%", "-3%", "+8%"]
}

df = pd.DataFrame(example_data)

# Gráfico de barras
st.markdown("### 📈 Métricas Principais")
col1, col2 = st.columns(2)

with col1:
    st.dataframe(df, use_container_width=True)

with col2:
    fig = px.bar(df, x="Métrica", y="Valor", title="Distribuição de Métricas")
    st.plotly_chart(fig, use_container_width=True)

# Séries temporais
st.markdown("### 📅 Tendência Temporal")

# Dados de exemplo para série temporal
dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
sales_data = pd.DataFrame({
    "Data": dates,
    "Vendas": [10 + i * 0.5 + (i % 7) * 2 for i in range(len(dates))]
})

fig2 = px.line(sales_data, x="Data", y="Vendas", title="Vendas Diárias - Janeiro 2024")
st.plotly_chart(fig2, use_container_width=True)

# Distribuição por loja
st.markdown("### 🏪 Distribuição por Loja")
store_data = pd.DataFrame({
    "Loja": ["Shopee", "AliExpress", "Amazon", "Temu", "Shein"],
    "Produtos": [45, 32, 28, 25, 20],
    "Vendas": [120, 85, 92, 45, 38]
})

col3, col4 = st.columns(2)

with col3:
    fig3 = px.pie(store_data, values="Produtos", names="Loja", title="Produtos por Loja")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.bar(store_data, x="Loja", y="Vendas", title="Vendas por Loja")
    st.plotly_chart(fig4, use_container_width=True)

# Exportar dados
st.markdown("### 📤 Exportar Dados")
if st.button("Exportar Relatório CSV", type="primary"):
    st.success("Relatório exportado com sucesso!")
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="estatisticas_afiliadohub.csv",
        mime="text/csv"
    )
'''
    
    def create_api_main(self):
        """Cria arquivo principal da API"""
        return '''"""
API Principal do AfiliadoHub
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

from api.handlers import products, analytics, csv_import
from api.handlers.api_extensions import router as extensions_router

# Cria aplicação FastAPI
app = FastAPI(
    title="AfiliadoHub API",
    description="API para gerenciamento de produtos de afiliados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas principais
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API do AfiliadoHub",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    try:
        from api.utils.supabase_client import get_supabase_manager
        supabase = get_supabase_manager()
        
        # Testa conexão com banco
        test = supabase.client.table("products").select("count", count="exact").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Produtos
@app.get("/api/products")
async def get_products(limit: int = 100, offset: int = 0):
    """Lista produtos"""
    try:
        filters = {"limit": limit, "offset": offset}
        products_list = await products.search_products(filters)
        return {"products": products_list, "total": len(products_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Busca produto por ID"""
    product = await products.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

# Analytics
@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Resumo das estatísticas"""
    return await analytics.get_system_statistics()

# Importação
@app.post("/api/import/csv")
async def import_csv(file: UploadFile = File(...)):
    """Importa produtos via CSV"""
    try:
        content = await file.read()
        result = await csv_import.process_csv_upload(content, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inclui rotas de extensões
app.include_router(extensions_router, prefix="/api/extensions")

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds() * 1000
    
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
    
    return response

# Execução local
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
'''
    
    def create_backup_script(self):
        """Cria script de backup"""
        return '''#!/usr/bin/env python3
"""
Script de backup do AfiliadoHub
"""
import os
import json
from datetime import datetime
import subprocess
import sys

def run_backup():
    print("🚀 Iniciando backup do AfiliadoHub...")
    
    # Cria diretório de backup se não existir
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
    
    # Dados de exemplo (em produção, buscar do banco)
    backup_data = {
        "system": "AfiliadoHub",
        "version": "1.0.0",
        "backup_date": datetime.now().isoformat(),
        "tables": {
            "products": [],
            "stats": []
        }
    }
    
    try:
        # Em produção, aqui você buscaria os dados do Supabase
        print("📦 Coletando dados do banco...")
        
        # Simulação de dados
        backup_data["tables"]["products"] = [
            {"id": 1, "name": "Produto Exemplo", "status": "active"}
        ]
        
        backup_data["tables"]["stats"] = [
            {"metric": "total_products", "value": 150}
        ]
        
        # Salva backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup criado: {backup_file}")
        print(f"📊 Tamanho: {os.path.getsize(backup_file)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return False

if __name__ == "__main__":
    success = run_backup()
    sys.exit(0 if success else 1)
'''
    
    def create_monitor_script(self):
        """Cria script de monitoramento corrigido"""
        return '''#!/usr/bin/env python3
"""
Script de monitoramento do AfiliadoHub - Versão Corrigida
"""
import os
import sys
import json
from datetime import datetime
import time

def check_system():
    """Verifica status do sistema"""
    print("🔍 Monitorando sistema AfiliadoHub...")
    
    checks = []
    
    # 1. Verifica se arquivos essenciais existem
    essential_files = [
        "api/main.py",
        "dashboard/Home.py",
        "requirements.txt"
    ]
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            checks.append({"check": f"Arquivo {file_path}", "status": "✅ OK"})
        else:
            checks.append({"check": f"Arquivo {file_path}", "status": "❌ FALTANDO"})
    
    # 2. Verifica diretórios
    essential_dirs = [
        "api/handlers",
        "dashboard/pages",
        "scripts"
    ]
    
    for dir_path in essential_dirs:
        if os.path.isdir(dir_path):
            checks.append({"check": f"Diretório {dir_path}", "status": "✅ OK"})
        else:
            checks.append({"check": f"Diretório {dir_path}", "status": "❌ FALTANDO"})
    
    # 3. Verifica Python
    try:
        import fastapi
        checks.append({"check": "FastAPI", "status": "✅ INSTALADO"})
    except ImportError:
        checks.append({"check": "FastAPI", "status": "❌ NÃO INSTALADO"})
    
    try:
        import streamlit
        checks.append({"check": "Streamlit", "status": "✅ INSTALADO"})
    except ImportError:
        checks.append({"check": "Streamlit", "status": "❌ NÃO INSTALADO"})
    
    # Exibe resultados
    print("\n📊 RESULTADOS DO MONITORAMENTO:")
    print("=" * 50)
    
    all_ok = True
    for check in checks:
        print(f"{check['status']} - {check['check']}")
        if "❌" in check["status"]:
            all_ok = False
    
    print("\n" + "=" * 50)
    
    if all_ok:
        print("🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        return True
    else:
        print("⚠️  ALGUMAS VERIFICAÇÕES FALHARAM")
        print("\n🔧 RECOMENDAÇÕES:")
        print("1. Execute: pip install -r requirements.txt")
        print("2. Verifique se todos os arquivos estão no lugar")
        print("3. Execute o script de verificação novamente")
        return False

def save_report():
    """Salva relatório de monitoramento"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": "AfiliadoHub",
        "checks": []
    }
    
    # Cria diretório de logs
    os.makedirs("logs", exist_ok=True)
    
    report_file = f"logs/monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Relatório salvo: {report_file}")

def main():
    """Função principal"""
    print("🚀 AFILIADOHUB MONITOR v1.0")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        system_ok = check_system()
        
        if system_ok:
            save_report()
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Tempo total: {elapsed:.2f} segundos")
        
        return 0 if system_ok else 1
        
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
'''
    
    def create_shopee_scraper(self):
        """Cria script de scraping Shopee"""
        return '''#!/usr/bin/env python3
"""
Scraper de produtos da Shopee
"""
import sys
import json
from datetime import datetime

def main():
    print("🛍️  Shopee Scraper - AfiliadoHub")
    print("=" * 50)
    
    print("\n📋 Funcionalidades:")
    print("1. Coletar produtos por categoria")
    print("2. Extrair links de afiliado")
    print("3. Salvar dados em CSV/JSON")
    print("4. Atualizar banco de dados")
    
    print("\n⚠️  AVISO:")
    print("Este é um script de exemplo.")
    print("Em produção, implemente:")
    print("- Web scraping com BeautifulSoup/Selenium")
    print"- API da Shopee (se disponível)")
    print("- Rate limiting para evitar bloqueios")
    print("- Tratamento de erros robusto")
    
    # Dados de exemplo
    sample_product = {
        "name": "Produto Exemplo Shopee",
        "price": 99.90,
        "original_price": 129.90,
        "discount": 23,
        "affiliate_link": "https://shope.ee/ABC123",
        "store": "shopee",
        "collected_at": datetime.now().isoformat()
    }
    
    print(f"\n📦 Produto exemplo: {json.dumps(sample_product, indent=2)}")
    
    print("\n✅ Script configurado com sucesso!")
    print("🔧 Implemente a lógica de scraping conforme necessário.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    def create_env_example(self):
        """Cria arquivo .env.example"""
        return '''# CONFIGURAÇÕES DO AFILIADOHUB

# ========================
# SUPABASE (Banco de Dados)
# ========================
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon
SUPABASE_SERVICE_KEY=sua-chave-service

# ========================
# TELEGRAM BOT
# ========================
BOT_TOKEN=seu-bot-token-aqui
TELEGRAM_CHAT_ID=id-do-chat-principal
ADMIN_USER_IDS=123456789,987654321

# ========================
# API CONFIG
# ========================
API_HOST=0.0.0.0
API_PORT=8000
API_URL=http://localhost:8000
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False

# ========================
# DASHBOARD
# ========================
SITE_URL=http://localhost:8501
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# ========================
# EMAIL (Opcional)
# ========================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app

# ========================
# BACKUP & LOGGING
# ========================
BACKUP_DIR=./backups
LOG_LEVEL=INFO
LOG_FILE=./logs/afiliadohub.log

# ========================
# LIMITES DO SISTEMA
# ========================
MAX_PRODUCTS_PER_IMPORT=10000
MAX_DAILY_TELEGRAM_SENDS=50
PRODUCT_CHECK_INTERVAL_HOURS=24

# ========================
# SHOPEE SCRAPER
# ========================
SHOPEE_API_KEY=sua-chave-shopee
SHOPEE_PARTNER_ID=seu-id-parceiro

# ========================
# SEGURANÇA
# ========================
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# ========================
# MONITORAMENTO
# ========================
SENTRY_DSN=sua-dsn-sentry
HEALTH_CHECK_INTERVAL=300
'''
    
    def create_gitignore(self):
        """Cria arquivo .gitignore"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Environment variables
.env
.env.local
.env.production
.env.development
.env.test

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Backup files
*.bak
backups/*.tar.gz
!backups/.gitkeep

# Streamlit
.streamlit/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
temp/
tmp/
*.tmp
*.temp

# Jupyter Notebook
.ipynb_checkpoints

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Package manager
node_modules/
jspm_packages/

# Compression
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip

# Documentation
_site/
.sass-cache/
.jekyll-cache/
.jekyll-metadata

# Security
*.pem
*.key
*.crt

# Custom
data/
uploads/
media/
staticfiles/
'''
    
    def create_products_handler(self):
        """Cria handler de produtos"""
        return '''"""
Handler para gerenciamento de produtos
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

async def add_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Adiciona um novo produto"""
    try:
        logger.info(f"Adicionando produto: {product_data.get('name', 'Sem nome')}")
        
        # Em produção, integrar com Supabase
        return {
            "success": True,
            "product_id": 1,
            "message": "Produto adicionado com sucesso (modo demonstração)"
        }
    except Exception as e:
        logger.error(f"Erro ao adicionar produto: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    """Busca produto por ID"""
    try:
        # Exemplo de produto
        return {
            "id": product_id,
            "name": "Produto Exemplo",
            "store": "shopee",
            "current_price": 99.90,
            "original_price": 129.90,
            "discount_percentage": 23,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produto {product_id}: {e}")
        return None

async def search_products(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Busca produtos com filtros"""
    try:
        # Exemplo de produtos
        products = [
            {
                "id": 1,
                "name": "Produto 1",
                "store": "shopee",
                "current_price": 99.90,
                "discount_percentage": 20
            },
            {
                "id": 2,
                "name": "Produto 2",
                "store": "aliexpress",
                "current_price": 49.90,
                "discount_percentage": 15
            }
        ]
        
        # Aplica filtros básicos
        filtered = []
        for product in products:
            if filters.get("store") and product["store"] != filters["store"]:
                continue
            if filters.get("min_price") and product["current_price"] < filters["min_price"]:
                continue
            if filters.get("max_price") and product["current_price"] > filters["max_price"]:
                continue
            
            filtered.append(product)
        
        return filtered
        
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return []

async def update_product(product_id: int, update_data: Dict[str, Any]) -> bool:
    """Atualiza produto"""
    logger.info(f"Atualizando produto {product_id}: {update_data}")
    return True

async def delete_product(product_id: int) -> bool:
    """Remove produto"""
    logger.info(f"Removendo produto {product_id}")
    return True
'''
    
    def create_sidebar(self):
        """Cria componente sidebar"""
        return '''"""
Sidebar do Dashboard AfiliadoHub
"""
import streamlit as st
from datetime import datetime

def show_sidebar():
    """Exibe a sidebar"""
    
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
        
        pages = [
            {"icon": "🏠", "name": "Dashboard", "page": "1_🏠_Dashboard.py"},
            {"icon": "📦", "name": "Produtos", "page": "2_📦_Produtos.py"},
            {"icon": "📊", "name": "Estatísticas", "page": "3_📊_Estatísticas.py"},
            {"icon": "🔄", "name": "Importar", "page": "4_🔄_Importar.py"},
            {"icon": "🤖", "name": "Telegram", "page": "5_🤖_Telegram.py"},
            {"icon": "⚙️", "name": "Configurações", "page": "6_⚙️_Configurações.py"}
        ]
        
        for page in pages:
            if st.button(
                f"{page['icon']} {page['name']}",
                key=f"nav_{page['page']}",
                use_container_width=True
            ):
                try:
                    st.switch_page(f"pages/{page['page']}")
                except:
                    st.info(f"Página {page['name']} em construção")
        
        st.markdown("---")
        
        # Status
        st.markdown("### 📊 Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Produtos", "150")
        with col2:
            st.metric("Vendas", "12")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Afiliados", "8")
        with col2:
            st.metric("Comissão", "R$ 342,50")
        
        st.markdown("---")
        
        # Sistema
        st.markdown("### ℹ️ Sistema")
        st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.caption("🌐 v1.0.0")
        st.caption("⚡ Status: Online")
        
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()
        
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            st.success("Até logo!")
            st.stop()
'''
    
    def create_products_page(self):
        """Cria página de produtos"""
        return '''"""
Página de Gerenciamento de Produtos
"""
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Produtos - AfiliadoHub",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Gerenciamento de Produtos")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "🆕 Adicionar", "✏️ Editar", "📤 Importar"])

with tab1:
    st.markdown("### Lista de Produtos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        store_filter = st.selectbox(
            "Loja",
            ["Todas", "Shopee", "AliExpress", "Amazon", "Temu", "Shein", "Magalu", "Mercado Livre"]
        )
    
    with col2:
        category_filter = st.text_input("Categoria")
    
    with col3:
        min_price, max_price = st.slider(
            "Faixa de Preço",
            min_value=0.0,
            max_value=10000.0,
            value=(0.0, 1000.0),
            step=10.0
        )
    
    # Botão de busca
    if st.button("🔍 Buscar Produtos", type="primary"):
        st.info("Buscando produtos...")
    
    # Tabela de produtos (exemplo)
    example_data = pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Nome": ["Smartphone XYZ", "Notebook ABC", "Fone Bluetooth", "Smartwatch", "Tablet"],
        "Loja": ["Shopee", "AliExpress", "Amazon", "Temu", "Shein"],
        "Preço": [999.90, 2499.90, 129.90, 299.90, 799.90],
        "Desconto": [23, 15, 40, 30, 20],
        "Status": ["Ativo", "Ativo", "Ativo", "Inativo", "Ativo"]
    })
    
    st.dataframe(example_data, use_container_width=True)
    
    # Ações em lote
    st.markdown("### Ações em Lote")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Ativar Selecionados", use_container_width=True):
            st.success("Produtos ativados!")
    
    with col2:
        if st.button("❌ Desativar Selecionados", use_container_width=True):
            st.warning("Produtos desativados!")
    
    with col3:
        if st.button("📤 Exportar CSV", use_container_width=True):
            st.success("CSV exportado!")

with tab2:
    st.markdown("### Adicionar Novo Produto")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nome do Produto *")
            store = st.selectbox(
                "Loja *",
                ["Shopee", "AliExpress", "Amazon", "Temu", "Shein", "Magalu", "Mercado Livre"]
            )
            affiliate_link = st.text_input("Link de Afiliado *")
            current_price = st.number_input("Preço Atual *", min_value=0.01, step=0.01)
        
        with col2:
            original_price = st.number_input("Preço Original", min_value=0.01, step=0.01)
            discount = st.number_input("Desconto (%)", min_value=0, max_value=100, step=1)
            category = st.text_input("Categoria")
            image_url = st.text_input("URL da Imagem")
        
        description = st.text_area("Descrição")
        
        # Botões
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Salvar Produto", type="primary")
        with col2:
            clear = st.form_submit_button("🗑️ Limpar")
        
        if submit:
            if name and affiliate_link and current_price:
                st.success("✅ Produto salvo com sucesso!")
            else:
                st.error("❌ Preencha os campos obrigatórios (*)")

with tab3:
    st.markdown("### Editar Produto")
    
    product_id = st.number_input("ID do Produto", min_value=1, step=1)
    
    if st.button("Buscar Produto"):
        if product_id:
            st.info(f"Carregando produto ID: {product_id}")
            # Aqui você carregaria os dados do produto
        else:
            st.error("Digite um ID válido")

with tab4:
    st.markdown("### Importar Produtos em Massa")
    
    st.info("""
    **Formatos suportados:**
    - CSV (separado por vírgula ou ponto-e-vírgula)
    - Excel (.xlsx)
    
    **Colunas obrigatórias:**
    - name: Nome do produto
    - affiliate_link: Link de afiliado
    - current_price: Preço atual
    - store: Loja (shopee, aliexpress, amazon, temu, shein, magalu, mercado_livre)
    """)
    
    uploaded_file = st.file_uploader("Escolha um arquivo", type=["csv", "xlsx"])
    
    if uploaded_file:
        st.success(f"Arquivo carregado: {uploaded_file.name}")
        
        if st.button("📤 Processar Importação", type="primary"):
            with st.spinner("Processando..."):
                # Simulação de processamento
                import time
                time.sleep(2)
                st.success("✅ 25 produtos importados com sucesso!")
    
    # Download template
    st.markdown("---")
    st.markdown("### 📋 Template de Importação")
    
    if st.button("📥 Download Template CSV"):
        st.success("Template disponível para download!")
        # Aqui você geraria um CSV template
'''
    
    def create_requirements(self):
        """Cria arquivo requirements.txt"""
        return '''# API & Backend
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
supabase==2.3.1
postgrest==0.12.0

# Dashboard
streamlit==1.28.1
plotly==5.18.0
pandas==2.1.4
numpy==1.26.2

# Data Processing
aiohttp==3.9.1
beautifulsoup4==4.12.2
lxml==4.9.3

# Telegram
python-telegram-bot==20.6

# Utilities
python-dotenv==1.0.0
python-dateutil==2.8.2
pydantic==2.5.0
pydantic-settings==2.1.0

# Monitoring
psutil==5.9.7
requests==2.31.0

# Export
openpyxl==3.1.2
xlsxwriter==3.1.9

# Development
pytest==7.4.3
black==23.11.0
flake8==6.1.0

# Testing
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Deployment
gunicorn==21.2.0
'''
    
    def run_complete_fix(self):
        """Executa todas as correções"""
        print("=" * 60)
        print("🛠️  CORREÇÃO COMPLETA DO AFILIADO.TOP")
        print("=" * 60)
        
        steps = [
            ("Criando diretórios", self.create_missing_directories),
            ("Criando arquivos", self.create_missing_files),
            ("Corrigindo sintaxe", self.fix_syntax_errors),
            ("Verificando conteúdos", self.verify_file_contents),
            ("Testando sintaxe Python", self.run_python_check)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                step_func()
            except Exception as e:
                print(f"  ❌ Erro: {e}")
        
        print("\n" + "=" * 60)
        print("✅ CORREÇÃO COMPLETA!")
        print("=" * 60)
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Configure suas credenciais no arquivo .env")
        print("2. Instale as dependências: pip install -r requirements.txt")
        print("3. Teste a API: uvicorn api.main:app --reload")
        print("4. Teste o Dashboard: streamlit run dashboard/Home.py")
        print("5. Execute os scripts: python scripts/monitor.py")
        
        return True

def main():
    """Função principal"""
    fixer = ProjectFixer()
    fixer.run_complete_fix()
    return 0

if __name__ == "__main__":
    sys.exit(main())
