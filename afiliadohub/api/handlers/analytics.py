"""
Handler para analytics básicos
"""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

from api.utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)

async def get_system_statistics() -> Dict[str, Any]:
    """Retorna estatísticas gerais do sistema"""
    try:
        supabase = get_supabase_manager()
        
        # Total de produtos
        total_response = supabase.client.table("products")\
            .select("count", count="exact")\
            .execute()
        
        # Produtos ativos
        active_response = supabase.client.table("products")\
            .select("count", count="exact")\
            .eq("is_active", True)\
            .execute()
        
        # Produtos com desconto
        discount_response = supabase.client.table("products")\
            .select("count", count="exact")\
            .gt("discount_percentage", 0)\
            .eq("is_active", True)\
            .execute()
        
        # Contagem por loja
        stores_response = supabase.client.table("products")\
            .select("store, count")\
            .eq("is_active", True)\
            .group("store")\
            .execute()
        
        # Estatísticas de envio
        telegram_response = supabase.client.table("product_stats")\
            .select("telegram_send_count")\
            .execute()
        
        total_sends = sum([s.get("telegram_send_count", 0) for s in telegram_response.data]) \
            if telegram_response.data else 0
        
        return {
            "total_products": total_response.count or 0,
            "active_products": active_response.count or 0,
            "products_with_discount": discount_response.count or 0,
            "stores": {item["store"]: item["count"] for item in stores_response.data} \
                if stores_response.data else {},
            "telegram_sends": total_sends,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return {
            "total_products": 0,
            "active_products": 0,
            "products_with_discount": 0,
            "stores": {},
            "telegram_sends": 0,
            "updated_at": datetime.now().isoformat(),
            "error": str(e)
        }

async def get_daily_statistics(date: datetime.date = None) -> Dict[str, Any]:
    """Retorna estatísticas do dia"""
    try:
        if not date:
            date = datetime.now().date()
        
        date_str = date.isoformat()
        
        supabase = get_supabase_manager()
        
        # Produtos adicionados hoje
        added_response = supabase.client.table("products")\
            .select("count", count="exact")\
            .gte("created_at", f"{date_str}T00:00:00")\
            .lte("created_at", f"{date_str}T23:59:59")\
            .execute()
        
        # Envios hoje
        sends_response = supabase.client.table("product_stats")\
            .select("telegram_send_count")\
            .gte("last_sent", f"{date_str}T00:00:00")\
            .lte("last_sent", f"{date_str}T23:59:59")\
            .execute()
        
        sends_today = sum([s.get("telegram_send_count", 0) for s in sends_response.data]) \
            if sends_response.data else 0
        
        return {
            "date": date_str,
            "products_added": added_response.count or 0,
            "telegram_sends": sends_today,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas diárias: {e}")
        return {
            "date": date.isoformat() if date else datetime.now().date().isoformat(),
            "products_added": 0,
            "telegram_sends": 0,
            "error": str(e)
        }

async def get_product_analytics(product_id: int) -> Dict[str, Any]:
    """Retorna analytics de um produto específico"""
    try:
        supabase = get_supabase_manager()
        
        # Busca produto
        product_response = supabase.client.table("products")\
            .select("*")\
            .eq("id", product_id)\
            .single()\
            .execute()
        
        if not product_response.data:
            return {"error": "Produto não encontrado"}
        
        # Busca estatísticas
        stats_response = supabase.client.table("product_stats")\
            .select("*")\
            .eq("product_id", product_id)\
            .single()\
            .execute()
        
        # Busca histórico de preços
        logs_response = supabase.client.table("product_logs")\
            .select("*")\
            .eq("product_id", product_id)\
            .eq("change_type", "price_change")\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        
        product = product_response.data
        stats = stats_response.data if stats_response.data else {}
        price_history = logs_response.data if logs_response.data else []
        
        # Calcula métricas
        price_change = 0
        if price_history and len(price_history) >= 2:
            latest_price = price_history[0]["new_price"]
            oldest_price = price_history[-1]["old_price"]
            price_change = ((latest_price - oldest_price) / oldest_price) * 100
        
        return {
            "product": {
                "id": product["id"],
                "name": product["name"],
                "store": product["store"],
                "current_price": product["current_price"],
                "original_price": product.get("original_price"),
                "discount_percentage": product.get("discount_percentage")
            },
            "stats": {
                "view_count": stats.get("view_count", 0),
                "click_count": stats.get("click_count", 0),
                "telegram_send_count": stats.get("telegram_send_count", 0),
                "last_sent": stats.get("last_sent")
            },
            "price_analytics": {
                "price_change_percent": price_change,
                "price_history": price_history,
                "current_price": product["current_price"],
                "original_price": product.get("original_price"),
                "is_on_sale": bool(product.get("discount_percentage", 0) > 0)
            },
            "performance_score": calculate_performance_score(stats, product)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics do produto {product_id}: {e}")
        return {"error": str(e)}

def calculate_performance_score(stats: Dict, product: Dict) -> float:
    """Calcula score de performance do produto"""
    score = 0
    
    # Pontos por views
    score += min(stats.get("view_count", 0) * 0.1, 10)
    
    # Pontos por cliques
    score += min(stats.get("click_count", 0) * 0.5, 20)
    
    # Pontos por envios
    score += min(stats.get("telegram_send_count", 0) * 1, 30)
    
    # Pontos por desconto
    discount = product.get("discount_percentage", 0)
    if discount > 0:
        score += min(discount, 40)
    
    # Pontos por preço competitivo
    price = product.get("current_price", 0)
    if price < 100:
        score += 10
    elif price < 500:
        score += 5
    
    return min(score, 100)  # Limita a 100 pontos
