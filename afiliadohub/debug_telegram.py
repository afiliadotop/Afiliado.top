import os
import requests
import json
from supabase import create_client

# --- CONFIGURE SEUS DADOS AQUI PARA O TESTE ---
# (Pegue do seu .streamlit/secrets.toml)
SUPABASE_URL = "https://ledvjvqitscytsnourfs.supabase.co" 
SUPABASE_KEY = "sb_secret_aBpN0hsDwDf4eP1SbX79wQ_V5EyjjQ6" # Cole a chave sb_secret_... ou eyJ... (service_role)

# Dados do Bot (Preencha para testar)
BOT_TOKEN = "7436127848:AAE4a_W_OMRribiXe0NKFsQfNslNgchTMnw"
CHAT_ID = "-1002499912192" # Ex: -100123456789

def teste_banco():
    print("\n1. 🗄️ Testando Gravação no Banco...")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Dados de teste
        config_data = {
            "bot_token": BOT_TOKEN,
            "group_chat_id": CHAT_ID,
            "teste": "funciona"
        }
        
        # Tenta salvar (Upsert)
        data = client.table("settings").upsert({
            "key": "telegram_config_teste",
            "value": config_data,
            "description": "Teste de script"
        }).execute()
        
        print("✅ Sucesso! Configuração salva no Supabase.")
        print(f"   Dados retornados: {data.data}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
        return False

def teste_telegram():
    print("\n2. 🤖 Testando Envio Telegram...")
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Pulei teste do Telegram (Token ou ID vazios).")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🚀 Teste de conexão do AfiliadoHub! Se você ler isso, funcionou.",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        res_json = response.json()
        
        if response.status_code == 200 and res_json.get("ok"):
            print("✅ Sucesso! Mensagem enviada para o grupo.")
        else:
            print(f"❌ Erro no Telegram: {res_json}")
            print("   Dica: Verifique se o bot é ADM do grupo e se o ID começa com -100")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    print("🔍 INICIANDO DIAGNÓSTICO...")
    banco_ok = teste_banco()
    if banco_ok:
        teste_telegram()
