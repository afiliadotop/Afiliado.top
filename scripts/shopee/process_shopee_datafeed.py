"""
Processa o datafeed da Shopee (TSV com tabs) e gera JSON otimizado
para a página estática de ofertas.
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


def read_tsv_loose(filename):
    """
    Lê o TSV de forma bem permissiva:
    - separador: TAB
    - não trata aspas como especiais (ignora)
    - pula linhas muito quebradas
    """
    print(f"⚙️ Lendo TSV (modo tolerante) de: {filename}")
    try:
        df = pd.read_csv(
            filename,
            sep="\t",
            encoding="utf-8",
            engine="python",
            quoting=csv.QUOTE_NONE,   # não tratar aspas
            on_bad_lines="skip",      # pular linhas que não batem com o header
        )
        print(f"✅ TSV lido com sucesso em modo tolerante.")
        print(f"📊 Colunas detectadas: {df.columns.tolist()}")
        print(f"🔢 Linhas lidas: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler TSV em modo tolerante: {e}")
        return None


def process_csv_to_json(csv_filename, json_filename):
    # Verifica se não é HTML por engano
    with open(csv_filename, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline().strip().lower()
        if first_line.startswith("<!doctype") or first_line.startswith("<html"):
            print("❌ O arquivo retornado é HTML (provavelmente login/erro da Shopee).")
            print("Verifique se o link do datafeed é realmente público ou se não exige login.")
            return False

    df = read_tsv_loose(csv_filename)
    if df is None or df.empty:
        print("❌ DataFrame vazio ou não pôde ser lido.")
        return False

    # Aqui usamos as colunas que você mostrou do feed:
    # shop_rating	itemid	sale_price	item_rating	global_category3	cb_option
    # discount_percentage	global_catid2	price	description	title	global_category1
    # image_link_3	global_catid1	global_catid3	like	condition	global_category2
    # model_ids	image_link	model_names	shop_name	product_link	product_short link

    def get_col(col_name):
        return df[col_name] if col_name in df.columns else None

    df_out = pd.DataFrame()

    # Campos básicos
    df_out["nome"] = get_col("title")
    df_out["imagem"] = get_col("image_link")
    df_out["descricao"] = get_col("description")
    df_out["categoria"] = get_col("global_category1")

    # Link: prioriza product_short link
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

    # Desconto: se houver discount_percentage, usamos
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

    # Limpeza básica
    df_out = df_out.fillna("")
    df_out = df_out[df_out["preco"] > 0]
    df_out = df_out[df_out["link"] != ""]

    # Ordenação: maior desconto + melhor avaliação
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
