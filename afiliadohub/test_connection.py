import os
from supabase import create_client

# Novas credenciais fornecidas
URL = "https://ledvjvqitscytsnourfs.supabase.co"
KEY = "sb_publishable_f65GNfFj_h5stAL8-O2Wcg_u7ajODOD"

print(f"🔌 Tentando conectar em: {URL}")
print(f"🔑 Usando chave: {KEY}")

try:
    client = create_client(URL, KEY)
    response = client.table("products").select("count", count="exact").limit(1).execute()
    
    print("\n✅ SUCESSO! Conexão estabelecida.")
    print(f"📦 Total de produtos: {response.count}")
    
except Exception as e:
    print("\n❌ FALHA.")
    print(e)
