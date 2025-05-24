import iop
import os
import json
import hashlib
import hmac
import time
import urllib.parse

# --- Configuração de Credenciais e Parâmetros da API ---
ALIEXPRESS_API_URL = os.environ.get('ALIEXPRESS_API_URL', 'https://api-sg.aliexpress.com/rest')
ALIEXPRESS_APP_KEY = os.environ.get('ALIEXPRESS_APP_KEY')
ALIEXPRESS_APP_SECRET = os.environ.get('ALIEXPRESS_APP_SECRET')
ALIEXPRESS_TRACKING_ID = os.environ.get('ALIEXPRESS_TRACKING_ID', 'default')

JSON_FILENAME = 'aliexpress_products.json'
MAX_PRODUCTS_TO_SAVE = 10000

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

def fetch_aliexpress_products():
    if not ALIEXPRESS_API_URL or not ALIEXPRESS_APP_KEY or not ALIEXPRESS_APP_SECRET:
        print("Erro: Credenciais da API do AliExpress não configuradas.")
        return

    client = iop.IopClient(ALIEXPRESS_API_URL, ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET)
    request = iop.IopRequest('aliexpress.affiliate.hotproduct.query')

    api_params = {
        'category_ids': '100003070,200001075', # AJUSTE CONFORME SEU NICHO
        'fields': 'product_id,product_title,product_image_url,product_detail_url,original_price,sale_price,discount,evaluate_rate,commission_rate',
        'keywords': 'smartphone,fones de ouvido,moda feminina', # AJUSTE SUAS PALAVRAS-CHAVE
        'max_sale_price': '1000.00',
        'min_sale_price': '10.00',
        'page_no': '1',
        'page_size': '50',
        'platform_product_type': 'ALL',
        'sort': 'ORDERS_DESC',
        'target_currency': 'BRL',
        'target_language': 'PT',
        'tracking_id': ALIEXPRESS_TRACKING_ID,
        'delivery_days': '15',
        'ship_to_country': 'BR',
        'promotion_name': 'Ofertas Imperdíveis do Dia',
    }

    app_signature, timestamp, sign_method = generate_aliexpress_signature(
        ALIEXPRESS_APP_SECRET, 'aliexpress.affiliate.hotproduct.query', api_params.copy()
    )

    request.add_api_param('sign', app_signature)
    request.add_api_param('timestamp', timestamp)
    request.add_api_param('sign_method', sign_method)
    for key, value in api_params.items():
        request.add_api_param(key, value)

    print(f"Fazendo requisição para aliexpress.affiliate.hotproduct.query com parâmetros: {api_params}")

    try:
        response = client.execute(request)
        if response.type == 'json' and response.body:
            data = json.loads(response.body)
            if 'error_code' in data:
                print(f"Erro da API: Código {data.get('error_code')} - Msg: {data.get('error_message')}")
                return
            products_list = data.get('result', {}).get('products', [])
            if products_list:
                if len(products_list) > MAX_PRODUCTS_TO_SAVE:
                    products_list = products_list[:MAX_PRODUCTS_TO_SAVE]
                with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
                    json.dump(products_list, f, ensure_ascii=False, indent=2)
                print(f"Dados de produtos salvos em {JSON_FILENAME}. Total: {len(products_list)} produtos.")
            else:
                print("Nenhum produto encontrado na resposta.")
        else:
            print(f"Resposta da API não é JSON ou está vazia. Tipo: {response.type}, Corpo: {response.body}")
    except iop.IopApiException as e:
        print(f"Erro na API: Código {e.error_code} - Msg: {e.error_message}")
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON: {response.body}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    fetch_aliexpress_products()
                                                                             
