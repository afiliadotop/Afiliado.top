"""
Processa o datafeed da Shopee (CSV/TSV) e gera JSON otimizado
para a página estática de ofertas.
Versão robusta: tenta múltiplos formatos automaticamente.
"""

import pandas as pd
import requests
import json
import os
import csv
from pathlib import Path

SHOPEE_DATAFEED_URL = os.environ.get('SHOPEE_DATAFEED_URL')

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)

CSV_FILENAME = DATA_DIR / 'shopee_datafeed_temp.csv'
JSON_FILENAME = DATA_DIR / 'shopee_products.json'

MAX_PRODUCTS_LIMIT = 500


def download_csv(url, filename):
    print(f"📥 Baixando datafeed de: {url[:80]}...")
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"✅ Arquivo baixado em {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar datafeed: {e}")
        return False


def read_csv_smart(filename):
    """
    Tenta ler o CSV/TSV com múltiplas estratégias até dar certo.
    """
    print(f"⚙️ Lendo arquivo de forma inteligente: {filename}")

    # Estratégias: (sep, quoting, descrição)
    strategies = [
        (",", csv.QUOTE_MINIMAL, "CSV com vírgula e aspas padrão"),
        (",", csv.QUOTE_ALL, "CSV com vírgula e todas as aspas"),
        (",", csv.QUOTE_NONE, "CSV com vírgula sem aspas"),
        ("\t", csv.QUOTE_MINIMAL, "TSV com tab e aspas padrão"),
        ("\t", csv.QUOTE_NONE, "TSV com tab sem aspas"),
    ]

    for sep, quoting, desc in strategies:
        try:
            print(f"🧪 Tentando: {desc}...")
            df = pd.read_csv(
                filename,
                sep=sep,
                encoding="utf-8",
                engine="python",
                quoting=quoting,
                on_bad_lines="skip",
            )
            
            # Valida se realmente leu colunas (não uma coluna gigante)
            if len(df.columns) > 5:  # esperamos pelo menos 6+ colunas
                print(f"✅ Sucesso com: {desc}")
                print(f"📊 Colunas detectadas ({len(df.columns)}): {df.columns.tolist()[:10]}...")
                print(f"🔢 Linhas lidas: {len(df)}")
                return df
            else:
                print(f"⚠️ Leu apenas {len(df.columns)} coluna(s), tentando próxima estratégia...")
        except Exception as e:
            print(f"❌ Falhou com {desc}: {e}")

    print("❌ Não foi possível ler o arquivo com nenhuma estratégia.")
    return None


def process_csv_to_json(csv_filename, json_filename):
    # Verifica se não é HTML
    with open(csv_filename, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline().strip().lower()
        if first_line.startswith("<!doctype") or first_line.startswith("<html"):
            print("❌ O arquivo retornado é HTML (provavelmente login/erro da Shopee).")
            return False

    df = read_csv_smart(csv_filename)
    if df is None or df.empty:
        print("❌ DataFrame vazio ou não pôde ser lido.")
        return False

    # Normaliza nomes de colunas (remove espaços, lowercase)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    print(f"📊 Colunas normalizadas: {df.columns.tolist()[:10]}...")

    def get_col(col_name):
        col_lower = col_name.lower().replace(" ", "_")
        return df[col_lower] if col_lower in df.columns else None

    df_out = pd.DataFrame()

    # Campos básicos
    title_col = get_col("title")
    if title_col is not None:
        df_out["nome"] = title_col
    else:
        print("⚠️ Coluna 'title' não encontrada.")
        df_out["nome"] = ""

    image_col = get_col("image_link")
    if image_col is not None:
        df_out["imagem"] = image_col
    else:
        df_out["imagem"] = ""

    desc_col = get_col("description")
    if desc_col is not None:
        df_out["descricao"] = desc_col
    else:
        df_out["descricao"] = ""

    cat_col = get_col("global_category1")
    if cat_col is not None:
        df_out["categoria"] = cat_col
    else:
        df_out["categoria"] = "Geral"

    # Link: prioriza product_short_link
    link_short = get_col("product_short_link")
    link_normal = get_col("product_link")
    if link_short is not None:
        df_out["link"] = link_short
    elif link_normal is not None:
        df_out["link"] = link_normal
    else:
        df_out["link"] = ""

    # Preços
    price_col = get_col("price")
    if price_col is not None:
        df_out["preco"] = pd.to_numeric(price_col, errors="coerce").fillna(0.0)
    else:
        df_out["preco"] = 0.0

    sale_col = get_col("sale_price")
    if sale_col is not None:
        df_out["preco_promocional"] = pd.to_numeric(sale_col, errors="coerce").fillna(0.0)
    else:
        df_out["preco_promocional"] = 0.0

    # Avaliação
    rating_col = get_col("item_rating")
    if rating_col is not None:
        df_out["avaliacao"] = pd.to_numeric(rating_col, errors="coerce").fillna(0.0)
    else:
        df_out["avaliacao"] = 0.0

    # Desconto
    discount_col = get_col("discount_percentage")
    if discount_col is not None:
        df_out["desconto"] = pd.to_numeric(discount_col, errors="coerce").fillna(0).astype(int)
    else:
        def calc_desconto(row):
            preco = row["preco"]
            promo = row["preco_promocional"]
            if preco > 0 and promo > 0 and promo < preco:
                return int(((preco - promo) / preco) * 100)
            return 0

        df_out["desconto"] = df_out.apply(calc_desconto, axis=1)

    # Limpeza
    df_out = df_out.fillna("")
    df_out = df_out[df_out["preco"] > 0]
    df_out = df_out[df_out["link"] != ""]

    # Ordenação
    df_out = df_out.sort_values(
        by=["desconto", "avaliacao"], ascending=[False, False]
    )

    total = len(df_out)
    if total > MAX_PRODUCTS_LIMIT:
        print(f"⚠️ Limitando produtos de {total} para {MAX_PRODUCTS_LIMIT}")
        df_out = df_out.head(MAX_PRODUCTS_LIMIT)
    else:
        print(f"📦 Total de produtos após filtros: {total}")

    products_json = df_out.to_dict(orient="records")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(products_json, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON salvo em {json_filename} com {len(products_json)} produtos.")
    return True


def main():
    if not SHOPEE_DATAFEED_URL:
        print("❌ SHOPEE_DATAFEED_URL não está configurada.")
        return False

    if not download_csv(SHOPEE_DATAFEED_URL, CSV_FILENAME):
        return False

    ok = process_csv_to_json(CSV_FILENAME, JSON_FILENAME)

    if CSV_FILENAME.exists():
        CSV_FILENAME.unlink()
        print(f"🗑️ Arquivo temporário removido: {CSV_FILENAME.name}")

    return ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
