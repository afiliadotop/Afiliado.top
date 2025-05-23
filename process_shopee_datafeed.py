# process_shopee_datafeed.py

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

# >>> NOVO: LIMITE MÁXIMO DE PRODUTOS PARA EVITAR ARQUIVOS GRANDES <<<
# Ajuste este valor conforme necessário para ficar abaixo de 100MB e para a performance do seu site
MAX_PRODUCTS_LIMIT = 10000 
# Note: Um CSV de 174MB com cerca de 3 milhões de inserções significa muitos produtos.
# 10.000 produtos é uma estimativa inicial para ficar abaixo de 100MB.
# Você pode precisar ajustar para mais ou menos, dependendo do tamanho das informações de cada produto.


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
        try:
            # Recomendo tentar com 'sep=',' primeiro se não tiver certeza do delimitador.
            df = pd.read_csv(csv_filename, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_filename, encoding='latin1')
        except Exception as e:
            print(f"Erro ao ler CSV com utf-8 ou latin1: {e}. Tentando com delimitador ';'")
            try:
                df = pd.read_csv(csv_filename, encoding='utf-8', sep=';')
            except UnicodeDecodeError:
                df = pd.read_csv(csv_filename, encoding='latin1', sep=';')
            except Exception as e_sep:
                print(f"Erro final ao ler CSV: {e_sep}. Verifique o delimitador e encoding do seu CSV.")
                exit(1)


        # Imprima para depuração (descomente se precisar ver as colunas reais)
        # print("Colunas disponíveis no CSV:", df.columns.tolist())

        # Mapeamento das colunas do CSV para os nomes que você deseja no JSON do seu site.
        required_columns = {
            'title': 'nome',
            'image_link': 'imagem',
            'description': 'descricao',
            'product_link': 'link',
            'global_category1': 'categoria',
            'price': 'preco'
            # Você pode adicionar outras colunas úteis aqui, como 'sale_price', 'item_rating', 'shop_name'
            # Ex: 'sale_price': 'preco_promocional',
            # Ex: 'item_rating': 'avaliacao',
            # Ex: 'shop_name': 'nome_loja'
        }

        # Verifica se todas as colunas necessárias estão presentes no CSV
        if not all(col_csv in df.columns for col_csv in required_columns.keys()):
            missing_cols = [col_csv for col_csv in required_columns.keys() if col_csv not in df.columns]
            print(f"Erro: Colunas essenciais faltando no CSV: {missing_cols}")
            print("Colunas disponíveis no CSV:", df.columns.tolist())
            exit(1)

        # Seleciona e renomeia as colunas
        df_selected = df[list(required_columns.keys())].rename(columns=required_columns)

        # Trata valores NaN (Not a Number) ou vazios, substituindo por string vazia
        df_selected = df_selected.fillna('')

        # Opcional: Converter 'preco' para float se ele vier como string e precisar de cálculos
        df_selected['preco'] = pd.to_numeric(df_selected['preco'], errors='coerce').fillna(0.0)

        # === NOVO: FILTRAGEM E LIMITAÇÃO DE PRODUTOS PARA REDUZIR O TAMANHO DO JSON ===

        # Exemplo de filtragem: Remover produtos com preço zero ou links vazios
        df_selected = df_selected[df_selected['preco'] > 0]
        df_selected = df_selected[df_selected['link'] != '']

        # Exemplo de filtragem por avaliação (se você adicionar 'item_rating' no required_columns)
        # if 'avaliacao' in df_selected.columns:
        #    df_selected = df_selected[df_selected['avaliacao'] >= 4.0] # Apenas produtos com 4 estrelas ou mais

        # Limita o número de produtos
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

    except FileNotFoundError:
        print(f"Erro: Arquivo CSV '{csv_filename}' não encontrado. Certifique-se de que foi baixado.")
        exit(1)
    except Exception as e:
        print(f"Erro ao processar CSV para JSON: {e}")
        exit(1)

if __name__ == "__main__":
    if not SHOPEE_DATAFEED_URL:
        print("Erro: A variável de ambiente SHOPEE_DATAFEED_URL não está configurada.")
        print("Certifique-se de adicioná-la aos Secrets do GitHub Actions.")
        exit(1)

    download_csv(SHOPEE_DATAFEED_URL, CSV_FILENAME)
    process_csv_to_json(CSV_FILENAME, JSON_FILENAME)

    # >>> NOVO: REMOVE O ARQUIVO CSV TEMPORÁRIO PARA ECONOMIZAR ESPAÇO NO REPOSITÓRIO <<<
    if os.path.exists(CSV_FILENAME):
        os.remove(CSV_FILENAME)
        print(f"Arquivo temporário {CSV_FILENAME} removido.")

