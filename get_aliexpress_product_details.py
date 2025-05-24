import iop
import os
import json
import hashlib
import hmac
import time
import urllib.parse

# --- Configuração de Credenciais ---
ALIEXPRESS_API_URL = os.environ.get('ALIEXPRESS_API_URL', 'https://api-sg.aliexpress.com/rest')
ALIEXPRESS_APP_KEY = os.environ.get('ALIEXPRESS_APP_KEY')
ALIEXPRESS_APP_SECRET = os.environ.get('ALIEXPRESS_APP_SECRET')
ALIEXPRESS_TRACKING_ID = os.environ.get('ALIEXPRESS_TRACKING_ID', 'default')

def generate_aliexpress_signature(app_secret, api_name, api_params):
    """Gera a assinatura SHA256 para a API do AliExpress."""
    params_for_signature = api_params.copy()
    params_for_signature['app_key'] = ALIEXPRESS_APP_KEY
    params_for_signature['timestamp'] = str(int(time.time() * 1000))
    params_for_signature['sign_method'] = 'sha256'
    params_for_signature['method'] = api_name

    processed_params = {}
    for key, value in params_for_signature.items():
        processed_params[key] = str(value) if value is not None else ''

    sorted_params = sorted(processed_params.items())
    sign_string = api_name + ''.join(f"{k}{v}" for k, v in sorted_params)

    signature = hmac.new(
        app_secret.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()

    return signature, params_for_signature['timestamp'], params_for_signature['sign_method']

def fetch_aliexpress_product_details(product_id_to_fetch):
    """Busca os detalhes de um produto específico da API do AliExpress DS."""
    if not ALIEXPRESS_API_URL or not ALIEXPRESS_APP_KEY or not ALIEXPRESS_APP_SECRET:
        print("Erro: Credenciais da API do AliExpress não configuradas.")
        return None

    client = iop.IopClient(ALIEXPRESS_API_URL, ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET)
    request = iop.IopRequest('aliexpress.ds.product.get')

    api_params = {
        'product_id': str(product_id_to_fetch),
        'fields': 'product_id,product_title,product_image_url,product_detail_url,original_price,sale_price,discount,evaluate_rate,commission_rate,description,seller_id,seller_name,store_url',
        'target_currency': 'BRL',
        'target_language': 'PT',
        'tracking_id': ALIEXPRESS_TRACKING_ID,
        'ship_to_country': 'BR',
    }

    app_signature, timestamp, sign_method = generate_aliexpress_signature(
        ALIEXPRESS_APP_SECRET, 'aliexpress.ds.product.get', api_params.copy()
    )

    request.add_api_param('sign', app_signature)
    request.add_api_param('timestamp', timestamp)
    request.add_api_param('sign_method', sign_method)
    for key, value in api_params.items():
        request.add_api_param(key, value)

    print(f"Fazendo requisição para aliexpress.ds.product.get para o produto ID: {product_id_to_fetch}")

    try:
        response = client.execute(request)
        if response.type == 'json' and response.body:
            data = json.loads(response.body)
            if 'error_code' in data:
                print(f"Erro da API: Código {data.get('error_code')} - Msg: {data.get('error_message')}")
                return None
            product_details = data.get('aliexpress_ds_product_get_response', {}).get('resp_result', {}).get('result', {})
            if product_details:
                print(f"Detalhes do produto {product_id_to_fetch} obtidos com sucesso.")
                return product_details
            else:
                print(f"Nenhum detalhe encontrado para o produto ID: {product_id_to_fetch}. Resposta: {response.body}")
                return None
        else:
            print(f"Resposta da API não é JSON ou está vazia. Tipo: {response.type}, Corpo: {response.body}")
            return None
    except iop.IopApiException as e:
        print(f"Erro na API: Código {e.error_code} - Msg: {e.error_message}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON: {response.body}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

if __name__ == "__main__":
    test_product_id = 'SEU_PRODUTO_ID_AQUI' # Substitua por um ID real para testar
    if test_product_id != 'SEU_PRODUTO_ID_AQUI':
        details = fetch_aliexpress_product_details(test_product_id)
        if details:
            print("\n--- Resumo dos Detalhes do Produto ---")
            print(f"Título: {details.get('product_title')}")
            print(f"Preço Original: {details.get('original_price')}")
            print(f"Preço de Venda: {details.get('sale_price')}")
            print(f"URL da Imagem: {details.get('product_image_url')}")
            print(f"URL do Detalhe: {details.get('product_detail_url')}")
            print(f"Avaliação: {details.get('evaluate_rate')}")
            print(f"Comissão: {details.get('commission_rate')}")
            print(f"Nome do Vendedor: {details.get('seller_name')}")
            
