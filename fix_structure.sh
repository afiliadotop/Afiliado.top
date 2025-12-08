#!/bin/bash
echo "🚧 Iniciando Reorganização do Projeto AfiliadoHub..."

# 1. Criar Diretórios Principais
echo "📂 Criando pastas..."
mkdir -p api/handlers api/utils api/models
mkdir -p dashboard/components dashboard/pages dashboard/utils
mkdir -p scripts
mkdir -p sql
mkdir -p .streamlit

# 2. Mover arquivos da API (Backend)
# O monitor espera api/main.py, mas você tinha index.py
if [ -f "index.py" ]; then
    echo "mv index.py -> api/main.py"
    mv index.py api/main.py
fi

# Mover handlers soltos para api/handlers
mv products.py api/handlers/ 2>/dev/null
mv telegram.py api/handlers/ 2>/dev/null
mv analytics.py api/handlers/ 2>/dev/null
mv advanced_analytics.py api/handlers/ 2>/dev/null
mv commission.py api/handlers/ 2>/dev/null
mv competition_analysis.py api/handlers/ 2>/dev/null
mv csv_import.py api/handlers/ 2>/dev/null
mv export_reports.py api/handlers/ 2>/dev/null
mv telegram_recommendations.py api/handlers/ 2>/dev/null

# Mover utils soltos para api/utils
mv supabase_client.py api/utils/ 2>/dev/null
mv link_processor.py api/utils/ 2>/dev/null
mv scheduler.py api/utils/ 2>/dev/null
mv logger.py api/utils/ 2>/dev/null

# Mover models para api/models
mv product.py api/models/ 2>/dev/null

# 3. Mover arquivos do Dashboard (Frontend)
# O monitor espera dashboard/Home.py, mas você tinha main.py
if [ -f "main.py" ]; then
    echo "mv main.py -> dashboard/Home.py (Entry point do Streamlit)"
    mv main.py dashboard/Home.py
fi

# Mover componentes do Dashboard
mv header.py dashboard/components/ 2>/dev/null
mv sidebar.py dashboard/components/ 2>/dev/null
mv charts.py dashboard/components/ 2>/dev/null

# Mover utils do Dashboard
mv data_processor.py dashboard/utils/ 2>/dev/null
# Nota: O dashboard tem seu próprio supabase_client ou usa o da API?
# Se houver duplicata, o Python resolve, mas vamos garantir que o utils exista
cp api/utils/supabase_client.py dashboard/utils/ 2>/dev/null

# Mover páginas do Dashboard
# O Streamlit usa a numeração para ordenar (2_, 3_, etc)
mv "2_📦_Produtos.py" dashboard/pages/ 2>/dev/null
mv "3_📊_Estatísticas.py" dashboard/pages/ 2>/dev/null
mv "4_🔄_Importar.py" dashboard/pages/ 2>/dev/null
mv "5_🤖_Telegram.py" dashboard/pages/ 2>/dev/null
mv "6_⚙️_Configurações.py" dashboard/pages/ 2>/dev/null

# 4. Mover Scripts DevOps
mv backup.py scripts/ 2>/dev/null
mv monitor.py scripts/ 2>/dev/null
mv shopee_scraper.py scripts/ 2>/dev/null
mv deploy.sh scripts/ 2>/dev/null
mv import_csv.sh scripts/ 2>/dev/null
mv migrate_and_update.sh scripts/ 2>/dev/null
mv deploy_streamlit.sh scripts/ 2>/dev/null

# 5. Criar arquivos vazios necessários se não existirem (para evitar erro de import)
touch api/__init__.py api/handlers/__init__.py api/utils/__init__.py api/models/__init__.py
touch dashboard/__init__.py dashboard/components/__init__.py dashboard/pages/__init__.py dashboard/utils/__init__.py

# 6. Criar .env.example se não existir
if [ ! -f ".env.example" ]; then
    echo "Criando .env.example..."
    echo "SUPABASE_URL=sua_url" > .env.example
    echo "SUPABASE_KEY=sua_key" >> .env.example
    echo "BOT_TOKEN=seu_token" >> .env.example
fi

# 7. Criar .gitignore se não existir
if [ ! -f ".gitignore" ]; then
    echo "Criando .gitignore..."
    echo ".env" > .gitignore
    echo ".env.production" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "venv/" >> .gitignore
    echo ".streamlit/secrets.toml" >> .gitignore
fi

echo "✅ Reorganização concluída!"
echo "📂 Estrutura atual:"
ls -R | grep ":$" | head -n 10
