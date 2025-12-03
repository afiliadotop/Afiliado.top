"""
Handler para gerenciamento de produtos
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from api.utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)

async def add_product(product_data: Dict[str, Any]) -> int:
    """Adiciona um novo produto ao banco"""
    try:
        supabase = get_supabase_manager()
        
        # Validação básica
        required_fields = ['store', 'name', 'affiliate_link', 'current_price']
        for field in required_fields:
            if field not in product_data:
                raise ValueError(f"Campo obrigatório faltando: {field}")
        
        # Insere no banco
        result = await supabase.insert_product(product_data)
        return result["id"]
        
    except Exception as e:
        logger.error(f"Erro ao adicionar produto: {e}")
        raise

async def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    """Busca um produto por ID"""
    try:
        supabase = get_supabase_manager()
        
        # Usa o cliente Supabase diretamente para buscar
        response = supabase.client.table("products")\
            .select("*")\
            .eq("id", product_id)\
            .single()\
            .execute()
        
        return response.data if response.data else None
        
    except Exception as e:
        logger.error(f"Erro ao buscar produto {product_id}: {e}")
        return None

async def update_product(product_id: int, update_data: Dict[str, Any]) -> bool:
    """Atualiza um produto existente"""
    try:
        supabase = get_supabase_manager()
        
        # Adiciona timestamp de atualização
        update_data['updated_at'] = datetime.now().isoformat()
        
        response = supabase.client.table("products")\
            .update(update_data)\
            .eq("id", product_id)\
            .execute()
        
        return len(response.data) > 0
        
    except Exception as e:
        logger.error(f"Erro ao atualizar produto {product_id}: {e}")
        return False

async def delete_product(product_id: int, soft_delete: bool = True) -> bool:
    """Remove um produto (soft ou hard delete)"""
    try:
        supabase = get_supabase_manager()
        
        if soft_delete:
            # Marca como inativo
            response = supabase.client.table("products")\
                .update({"is_active": False, "updated_at": datetime.now().isoformat()})\
                .eq("id", product_id)\
                .execute()
        else:
            # Remove permanentemente
            response = supabase.client.table("products")\
                .delete()\
                .eq("id", product_id)\
                .execute()
        
        return len(response.data) > 0
        
    except Exception as e:
        logger.error(f"Erro ao remover produto {product_id}: {e}")
        return False

async def search_products(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Busca produtos com filtros"""
    try:
        return await get_supabase_manager().get_products(filters)
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return []

async def get_random_product(min_discount: int = 0, max_sent_last_days: int = 7) -> Optional[Dict[str, Any]]:
    """Busca um produto aleatório que não foi enviado recentemente"""
    try:
        supabase = get_supabase_manager()
        
        # Query para produto não enviado recentemente
        query = f"""
        SELECT p.* 
        FROM products p
        LEFT JOIN product_stats ps ON p.id = ps.product_id
        WHERE p.is_active = true
        AND p.discount_percentage >= {min_discount}
        AND (ps.last_sent IS NULL OR ps.last_sent < NOW() - INTERVAL '{max_sent_last_days} days')
        ORDER BY RANDOM()
        LIMIT 1
        """
        
        # Executa query raw (simplificado - na prática usar prepared statements)
        response = supabase.client.table("products")\
            .select("*")\
            .eq("is_active", True)\
            .gte("discount_percentage", min_discount)\
            .order("RANDOM()")\
            .limit(1)\
            .execute()
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"Erro ao buscar produto aleatório: {e}")
        return None

async def bulk_update_prices(updates: List[Dict[str, Any]]) -> Dict[str, int]:
    """Atualiza preços em massa"""
    try:
        supabase = get_supabase_manager()
        
        success_count = 0
        error_count = 0
        
        for update in updates:
            product_id = update.get("product_id")
            new_price = update.get("new_price")
            
            if product_id and new_price:
                success = await supabase.update_product_price(product_id, new_price)
                if success:
                    success_count += 1
                else:
                    error_count += 1
        
        return {
            "total": len(updates),
            "success": success_count,
            "errors": error_count
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preços em massa: {e}")
        return {"total": 0, "success": 0, "errors": 0}
