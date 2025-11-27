"""
Processa o datafeed CSV da Shopee e gera JSON otimizado.
Usado pelo GitHub Actions para atualizar automaticamente as ofertas.
"""

import pandas as pd
import requests
import json
import os
from pathlib import Path

# URL do datafeed (vem de variável de ambiente / secret)
SHOPEE_DATAFEED_URL = os.environ.get('SHOPEE_DATAFEED_URL')

# Caminhos
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)

CSV_FILENAME = DATA_DIR / 'shopee_datafeed_temp.csv'
JSON_FILENAME = DATA_DIR / 'shopee_products.json'

MAX_PRODUCTS_LIMIT = 500  # limite para não explodir o HTML


def download_csv(url, filename):
    """Baixa o arquivo CSV do URL."""
    print(f"📥 Baixando CSV de: {url[:80]}...")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ CSV baixado em {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar CSV: {e}")
        return False


def process_csv_to_json(csv_filename, json_filename):
    """Lê o CSV, processa e salva como JSON."""
    print(f"⚙️ Lendo CSV: {csv_filename}")
    try:
        df = pd.read_csv(csv_filename, encoding='utf-8', sep=',', quotechar='"')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_filename, encoding='latin1', sep=',', quotechar='"')
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return False

    print(f"📊 Colunas disponíveis: {df.columns.tolist()}")

    required_columns = {
        'title': 'nome',
        'image_link': 'imagem',
        'description': 'descricao',
        'product_link': 'link',
        'global_category1': 'categoria',
        'price': 'preco',
        # se o datafeed tiver, aproveitamos:
        'sale_price': 'preco_promocional',
        'item_rating': 'avaliacao',
    }

    # Checa colunas essenciais mínimas
    essentials = ['title', 'image_link', 'product_link', 'price']
    missing_essentials = [c for c in essentials if c not in df.columns]
    if missing_essentials:
        print(f"❌ Colunas essenciais faltando no CSV: {missing_essentials}")
        return False

    # Mantém só as colunas que existem
    available_mapping = {k: v for k, v in required_columns.items() if k in df.columns}
    df_selected = df[list(available_mapping.keys())].rename(columns=available_mapping)

    df_selected = df_selected.fillna('')
    df_selected['preco'] = pd.to_numeric(df_selected['preco'], errors='coerce').fillna(0.0)

    # Se tiver preço promocional
    if 'preco_promocional' in df_selected.columns:
        df_selected['preco_promocional'] = pd.to_numeric(
            df_selected['preco_promocional'], errors='coerce'
        ).fillna(0.0)
        df_selected['desconto'] = df_selected.apply(
            lambda row: int(((row['preco'] - row['preco_promocional']) / row['preco']) * 100)
            if row['preco'] > 0 and row['preco_promocional'] > 0 and row['preco_promocional'] < row['preco']
            else 0,
            axis=1
        )
    else:
        df_selected['desconto'] = 0
        df_selected['preco_promocional'] = 0.0

    # Filtros básicos
    df_selected = df_selected[df_selected['preco'] > 0]
    df_selected = df_selected[df_selected['link'] != '']

    # Ordenar: maior desconto + melhor avaliação (se houver)
    if 'avaliacao' in df_selected.columns:
        df_selected['avaliacao'] = pd.to_numeric(df_selected['avaliacao'], errors='coerce').fillna(0.0)
        df_selected = df_selected.sort_values(by=['desconto', 'avaliacao'], ascending=[False, False])
    else:
        df_selected = df_selected.sort_values(by='desconto', ascending=False)

    # Limita número de produtos
    if len(df_selected) > MAX_PRODUCTS_LIMIT:
        print(f"⚠️ Limitando a {MAX_PRODUCTS_LIMIT} produtos (de {len(df_selected)})")
        df_selected = df_selected.head(MAX_PRODUCTS_LIMIT)
    else:
        print(f"📦 Total após filtros: {len(df_selected)} produtos")

    products_json = df_selected.to_dict(orient='records')

    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(products_json, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON salvo em {json_filename} ({len(products_json)} produtos)")
    return True


def main():
    if not SHOPEE_DATAFEED_URL:
        print("❌ Erro: SHOPEE_DATAFEED_URL não está configurada.")
        return False

    if not download_csv(SHOPEE_DATAFEED_URL, CSV_FILENAME):
        return False

    ok = process_csv_to_json(CSV_FILENAME, JSON_FILENAME)

    # Remove CSV temporário
    if CSV_FILENAME.exists():
        CSV_FILENAME.unlink()
        print(f"🗑️ Arquivo temporário removido: {CSV_FILENAME.name}")

    return ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
