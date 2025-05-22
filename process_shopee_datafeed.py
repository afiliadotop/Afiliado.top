# process_shopee_datafeed.py

import pandas as pd
import requests
import json
import os

# Seu link do datafeed da Shopee
# SUBSTITUA PELO SEU LINK REAL DO DATAFEED!
SHOPEE_DATAFEED_URL = os.environ.get('SHOPEE_DATAFEED_URL')

# Nome do arquivo CSV que será baixado temporariamente
CSV_FILENAME = 'shopee_datafeed.csv'
# Nome do arquivo JSON de saída que seu site vai consumir
JSON_FILENAME = 'produtos_shopee.json'

def download_csv(url, filename):
    """Baixa o arquivo CSV do URL."""
    print(f"Baixando CSV de: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Lança um erro para requisições HTTP ruins (4xx ou 5xx)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"CSV baixado para {filename} com sucesso.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar CSV: {e}")
        exit(1) # Sai com erro se não conseguir baixar

def process_csv_to_json(csv_filename, json_filename):
    """Lê o CSV, processa e salva como JSON."""
    print(f"Processando CSV: {csv_filename}")
    try:
        # Tenta ler o CSV. A Shopee pode usar ',' ou ';' ou tab como delimitador.
        # Adicione 'encoding' se tiver problemas com caracteres especiais (ex: 'utf-8', 'latin1')
        # Testar com 'sep=',' ou 'sep=';' se a detecção automática falhar.
        try:
            df = pd.read_csv(csv_filename, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_filename, encoding='latin1')

        # === ESTA É A PARTE CRUCIAL ADAPTADA PARA SEUS NOMES DE COLUNAS ===
        # Mapeamento das colunas do CSV para os nomes que você deseja no JSON do seu site.
        required_columns = {
            'title': 'nome',                  # 'title' do CSV vira 'nome' no JSON
            'image_link': 'imagem',           # 'image_link' do CSV vira 'imagem' no JSON
            'description': 'descricao',       # 'description' do CSV vira 'descricao' no JSON
            'product_link': 'link',           # 'product_link' do CSV vira 'link' (seu link de afiliado) no JSON
            'global_category1': 'categoria',  # 'global_category1' do CSV vira 'categoria' no JSON
            'price': 'preco'                  # 'price' do CSV vira 'preco' no JSON
            # Você pode adicionar outras colunas que achar úteis, como 'shop_name', 'sale_price', etc.
            # Apenas adicione-as aqui no mapeamento.
        }

        # Verifica se todas as colunas necessárias estão presentes no CSV
        if not all(col_csv in df.columns for col_csv in required_columns.keys()):
            missing_cols = [col_csv for col_csv in required_columns.keys() if col_csv not in df.columns]
            print(f"Erro: Colunas essenciais faltando no CSV: {missing_cols}")
            print("Colunas disponíveis no CSV:", df.columns.tolist())
            exit(1) # Sai com erro se faltar colunas

        # Seleciona e renomeia as colunas
        df_selected = df[list(required_columns.keys())].rename(columns=required_columns)

        # Trata valores NaN (Not a Number) ou vazios, substituindo por string vazia
        df_selected = df_selected.fillna('')

        # Opcional: Filtrar produtos com base em 'product_link' não vazio
        # df_selected = df_selected[df_selected['link'] != '']

        # Opcional: Converter 'preco' para float se ele vier como string e precisar de cálculos
        # df_selected['preco'] = pd.to_numeric(df_selected['preco'], errors='coerce').fillna(0.0)


        # Converte o DataFrame para uma lista de dicionários (formato JSON)
        products_json = df_selected.to_dict(orient='records')

        # Salva o JSON no arquivo de saída
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(products_json, f, ensure_ascii=False, indent=2)

        print(f"Dados processados e salvos em {json_filename} com sucesso. Total de produtos: {len(products_json)}")

    except FileNotFoundError:
        print(f"Erro: Arquivo CSV '{csv_filename}' não encontrado. Certifique-se de que foi baixado.")
        exit(1)
    except Exception as e:
        print(f"Erro ao processar CSV para JSON: {e}")
        exit(1) # Sai com erro

if __name__ == "__main__":
    if not SHOPEE_DATAFEED_URL:
        print("Erro: A variável de ambiente SHOPEE_DATAFEED_URL não está configurada.")
        print("Certifique-se de adicioná-la aos Secrets do GitHub Actions.")
        exit(1)

    download_csv(SHOPEE_DATAFEED_URL, CSV_FILENAME)
    process_csv_to_json(CSV_FILENAME, JSON_FILENAME)
