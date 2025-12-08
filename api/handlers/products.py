import logging
from typing import Dict, List, Any, Optional
from api.utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)
db = get_supabase_manager()

async def add_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = db.client.table("products").insert(product_data).execute()
        return {"success": True, "product": response.data[0] if response.data else {}}
    except Exception as e:
        logger.error(f"Erro DB: {e}")
        return {"success": False, "error": str(e)}

async def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    try:
        response = db.client.table("products").select("*").eq("id", product_id).single().execute()
        return response.data
    except Exception:
        return None

async def search_products(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    return await db.get_products(filters)

async def get_random_product(min_discount: int = 0) -> Optional[Dict[str, Any]]:
    return await db.get_random_product(min_discount)
