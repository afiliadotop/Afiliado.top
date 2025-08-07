import pandas as pd
import requests
import json
import os

# Seu link do datafeed da Shopee
SHOPEE_DATAFEED_URL = os.environ.get('SHOPEE_DATAFEED_URL')

# Nome do arquivo CSV que será baixado temporariamente
CSV_FILENAME = 'shopee_datafeed.csv'
# Nome do arquivo JSON de saída que seu site vai consumir
JSON_FILENAME = 'produtos_shopee.json'

# Limite máximo de produtos para evitar arquivos grandes
# Ajuste este valor conforme necessário para a performance do seu site
MAX_PRODUCTS_LIMIT = 10000

def download_csv(url, filename):
    """Baixa o arquivo CSV do URL."""
    print(f"Baixando CSV de: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"CSV baixado para {filename} com sucesso.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar CSV: {e}")
        exit(1)

def process_csv_to_json(csv_filename, json_filename):
    """Lê o CSV, processa e salva como JSON."""
    print(f"Processando CSV: {csv_filename}")
    try:
        # Tenta ler o CSV, usando o delimitador correto (vírgula)
        # e o 'quotechar' para lidar com vírgulas e quebras de linha dentro de um campo.
        df = pd.read_csv(csv_filename, encoding='utf-8', sep=',', quotechar='"')
    except UnicodeDecodeError:
        # Se utf-8 falhar, tenta com latin1.
        df = pd.read_csv(csv_filename, encoding='latin1', sep=',', quotechar='"')
    except Exception as e:
        # Se o erro persistir, há um problema estrutural no arquivo.
        print(f"Erro final ao ler CSV: {e}. Verifique a estrutura do seu arquivo.")
        exit(1)

    print(f"CSV lido com sucesso. Colunas disponíveis: {df.columns.tolist()}")

    # Mapeamento das colunas do CSV para os nomes que você deseja no JSON do seu site.
    required_columns = {
        'title': 'nome',
        'image_link': 'imagem',
        'description': 'descricao',
        'product_link': 'link',
        'global_category1': 'categoria',
        'price': 'preco'
        # Adicione outras colunas úteis aqui, como 'sale_price', 'item_rating', etc.
    }

    # Verifica se todas as colunas necessárias estão presentes no CSV
    if not all(col_csv in df.columns for col_csv in required_columns.keys()):
        missing_cols = [col_csv for col_csv in required_columns.keys() if col_csv not in df.columns]
        print(f"Erro: Colunas essenciais faltando no CSV: {missing_cols}")
        exit(1)

    # Seleciona, renomeia e trata os dados
    df_selected = df[list(required_columns.keys())].rename(columns=required_columns)
    df_selected = df_selected.fillna('')
    df_selected['preco'] = pd.to_numeric(df_selected['preco'], errors='coerce').fillna(0.0)

    # Filtragem e Limitação de produtos para reduzir o tamanho do JSON
    df_selected = df_selected[df_selected['preco'] > 0]
    df_selected = df_selected[df_selected['link'] != '']
    
    if len(df_selected) > MAX_PRODUCTS_LIMIT:
        df_selected = df_selected.head(MAX_PRODUCTS_LIMIT)
        print(f"Limitando produtos para os primeiros {MAX_PRODUCTS_LIMIT} para reduzir o tamanho do JSON.")
    else:
        print(f"Total de produtos após filtros: {len(df_selected)}")

    # Converte o DataFrame para uma lista de dicionários (formato JSON)
    products_json = df_selected.to_dict(orient='records')

    # Salva o JSON no arquivo de saída
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(products_json, f, ensure_ascii=False, indent=2)

    print(f"Dados processados e salvos em {json_filename} com sucesso. Total de produtos no JSON: {len(products_json)}")

    
if __name__ == "__main__":
    if not SHOPEE_DATAFEED_URL:
        print("Erro: A variável de ambiente SHOPEE_DATAFEED_URL não está configurada.")
        print("Certifique-se de adicioná-la aos Secrets do GitHub Actions.")
        exit(1)

    download_csv(SHOPEE_DATAFEED_URL, CSV_FILENAME)
    process_csv_to_json(CSV_FILENAME, JSON_FILENAME)

    # Remove o arquivo CSV temporário para economizar espaço no repositório
    if os.path.exists(CSV_FILENAME):
        os.remove(CSV_FILENAME)
        print(f"Arquivo temporário {CSV_FILENAME} removido.")
