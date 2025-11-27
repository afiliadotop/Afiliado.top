"""
Processa o datafeed da Shopee (TSV com tabs) e gera JSON otimizado
para gerar a página estática de ofertas.
"""

import pandas as pd
import requests
import json
import os
from pathlib import Path

SHOPEE_DATAFEED_URL = os.environ.get('SHOPEE_DATAFEED_URL')

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)

CSV_FILENAME = DATA_DIR / 'shopee_datafeed_temp.tsv'
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


def process_csv_to_json(csv_filename, json_filename):
    print(f"⚙️ Lendo datafeed TS V: {csv_filename}")

    # Seu feed é TAB-SEPARATED (delimitador = '\t')
    try:
        df = pd.read_csv(
            csv_filename,
            sep="\t",
            encoding="utf-8",
            engine="python"
        )
    except Exception as e:
        print(f"❌ Erro ao ler TSV: {e}")
        return False

    print(f"📊 Colunas detectadas: {df.columns.tolist()}")

    # Normaliza nomes (só por segurança)
    df.columns = [str(c).strip() for c in df.columns]

    # Conferindo colunas que vamos usar
    needed = ["title", "image_link", "description", "global_category1", "price",
              "sale_price", "item_rating", "discount_percentage", "product_link", "product_short link"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        print(f"⚠️ Algumas colunas não existem (isso é esperado em alguns feeds): {missing}")

    # Construção do DataFrame final, usando .get em cada coluna
    def get_col(col_name):
        return df[col_name] if col_name in df.columns else None

    df_out = pd.DataFrame()

    # Campos básicos
    df_out["nome"] = get_col("title")
    df_out["imagem"] = get_col("image_link")
    df_out["descricao"] = get_col("description")
    df_out["categoria"] = get_col("global_category1")

    # Link: prioriza product_short link, senão product_link
    if "product_short link" in df.columns:
        df_out["link"] = df["product_short link"]
    elif "product_link" in df.columns:
        df_out["link"] = df["product_link"]
    else:
        df_out["link"] = ""

    # Preços
    df_out["preco"] = pd.to_numeric(get_col("price"), errors="coerce").fillna(0.0)
    if "sale_price" in df.columns:
        df_out["preco_promocional"] = pd.to_numeric(
            get_col("sale_price"), errors="coerce"
        ).fillna(0.0)
    else:
        df_out["preco_promocional"] = 0.0

    # Avaliação
    if "item_rating" in df.columns:
        df_out["avaliacao"] = pd.to_numeric(
            get_col("item_rating"), errors="coerce"
        ).fillna(0.0)
    else:
        df_out["avaliacao"] = 0.0

    # Desconto: se vier pronto, usamos; senão calculamos
    if "discount_percentage" in df.columns:
        df_out["desconto"] = pd.to_numeric(
            get_col("discount_percentage"), errors="coerce"
        ).fillna(0).astype(int)
    else:
        def calc_desconto(row):
            preco = row["preco"]
            promo = row["preco_promocional"]
            if preco > 0 and promo > 0 and promo < preco:
                return int(((preco - promo) / preco) * 100)
            return 0

        df_out["desconto"] = df_out.apply(calc_desconto, axis=1)

    # Limpa NaNs/string vazia
    df_out = df_out.fillna("")
    df_out = df_out[df_out["preco"] > 0]
    df_out = df_out[df_out["link"] != ""]

    # Ordenar: maior desconto + melhor rating
    df_out = df_out.sort_values(
        by=["desconto", "avaliacao"], ascending=[False, False]
    )

    # Limitar para não ficar gigante
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

    # Remove arquivo temporário
    if CSV_FILENAME.exists():
        CSV_FILENAME.unlink()
        print(f"🗑️ Arquivo temporário removido: {CSV_FILENAME.name}")

    return ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
