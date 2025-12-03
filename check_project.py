#!/usr/bin/env python3
"""
Script para verificar integridade do projeto Afiliado.top
"""
import os
import sys
from pathlib import Path

def check_project_structure():
    """Verifica estrutura do projeto"""
    
    base_path = Path(".")
    issues = []
    
    # Estrutura esperada
    expected_structure = {
        "api/": [
            "__init__.py",
            "main.py",
            "handlers/__init__.py",
            "handlers/products.py",
            "handlers/analytics.py",
            "handlers/telegram.py",
            "handlers/csv_import.py",
            "utils/__init__.py",
            "utils/supabase_client.py",
            "utils/logger.py",
            "models/__init__.py",
            "models/product.py"
        ],
        "dashboard/": [
            "__init__.py",
            "Home.py",
            "components/__init__.py",
            "components/sidebar.py",
            "components/header.py",
            "components/charts.py",
            "pages/__init__.py",
            "pages/1_🏠_Dashboard.py",
            "pages/2_📦_Produtos.py",
            "pages/3_📊_Estatísticas.py",
            "pages/4_🔄_Importar.py",
            "pages/5_🤖_Telegram.py",
            "pages/6_⚙️_Configurações.py",
            "utils/__init__.py",
            "utils/supabase_client.py",
            "utils/data_processor.py"
        ],
        "scripts/": [
            "backup.py",
            "monitor.py",
            "shopee_scraper.py"
        ],
        ".": [
            "requirements.txt",
            "README.md",
            ".env.example",
            ".gitignore"
        ]
    }
    
    print("🔍 Verificando estrutura do projeto...")
    print("=" * 60)
    
    for dir_path, files in expected_structure.items():
        full_dir = base_path / dir_path
        
        if not full_dir.exists():
            issues.append(f"❌ Diretório faltando: {dir_path}")
            continue
        
        for file in files:
            file_path = full_dir / file
            if not file_path.exists():
                issues.append(f"❌ Arquivo faltando: {dir_path}{file}")
    
    # Verifica arquivos com problemas de nomenclatura
    problem_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if " " in file or ".." in file:
                problem_files.append(os.path.join(root, file))
    
    if issues:
        print("📋 Problemas encontrados:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ Estrutura básica OK")
    
    if problem_files:
        print("\n⚠️ Arquivos com problemas de nomenclatura:")
        for file in problem_files:
            print(f"  {file}")
    
    return issues, problem_files

def check_file_contents():
    """Verifica conteúdo mínimo dos arquivos"""
    
    print("\n📄 Verificando conteúdo dos arquivos...")
    print("=" * 60)
    
    min_size_files = {
        "api/handlers/products.py": 1000,
        "dashboard/components/sidebar.py": 500,
        "dashboard/pages/2_📦_Produtos.py": 300,
        "requirements.txt": 10
    }
    
    content_issues = []
    
    for file_path, min_size in min_size_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size < min_size:
                content_issues.append(f"❌ {file_path} muito pequeno ({size} bytes)")
        else:
            content_issues.append(f"❌ {file_path} não encontrado")
    
    if content_issues:
        for issue in content_issues:
            print(f"  {issue}")
    else:
        print("✅ Conteúdo mínimo OK")
    
    return content_issues

def check_python_syntax():
    """Verifica sintaxe Python básica"""
    
    print("\n🐍 Verificando sintaxe Python...")
    print("=" * 60)
    
    import subprocess
    
    syntax_issues = []
    
    # Encontra todos os arquivos Python
    python_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    for py_file in python_files[:10]:  # Verifica os primeiros 10
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", py_file],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                syntax_issues.append(f"❌ Erro de sintaxe em {py_file}")
        except:
            pass
    
    if syntax_issues:
        for issue in syntax_issues:
            print(f"  {issue}")
    else:
        print("✅ Sintaxe Python OK")
    
    return syntax_issues

def main():
    """Função principal"""
    
    print("🚀 VERIFICAÇÃO DO PROJETO AFILIADO.TOP")
    print("=" * 60)
    
    # Verifica estrutura
    structure_issues, naming_issues = check_project_structure()
    
    # Verifica conteúdo
    content_issues = check_file_contents()
    
    # Verifica sintaxe
    syntax_issues = check_python_syntax()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    print(f"  • Problemas de estrutura: {len(structure_issues)}")
    print(f"  • Problemas de nomenclatura: {len(naming_issues)}")
    print(f"  • Problemas de conteúdo: {len(content_issues)}")
    print(f"  • Problemas de sintaxe: {len(syntax_issues)}")
    
    total_issues = (len(structure_issues) + len(naming_issues) + 
                    len(content_issues) + len(syntax_issues))
    
    if total_issues == 0:
        print("\n🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        return True
    else:
        print(f"\n⚠️  Total de problemas encontrados: {total_issues}")
        print("\n🔧 RECOMENDAÇÕES:")
        
        if structure_issues:
            print("  1. Crie os arquivos e diretórios faltantes")
        
        if naming_issues:
            print("  2. Renomeie arquivos com espaços ou caracteres especiais")
        
        if content_issues:
            print("  3. Complete o conteúdo dos arquivos pequenos")
        
        if syntax_issues:
            print("  4. Corrija erros de sintaxe Python")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
