#!/usr/bin/env python3
import sys
import os
# Adiciona raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils.supabase_client import get_supabase_manager
import json
from datetime import datetime

async def main():
    print("💾 Iniciando Backup...")
    db = get_supabase_manager()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup Produtos
    try:
        data = db.client.table("products").select("*").execute()
        filename = f"backups/products_{timestamp}.json"
        os.makedirs("backups", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data.data, f)
        print(f"✅ Backup salvo: {filename}")
    except Exception as e:
        print(f"❌ Erro no backup: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
