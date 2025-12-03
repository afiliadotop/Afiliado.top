import csv
import io
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from api.utils.supabase_client import get_supabase_manager
from api.utils.link_processor import normalize_link, detect_store, extract_product_info

logger = logging.getLogger(__name__)

class CSVImporter:
    def __init__(self):
        self.supabase = get_supabase_manager()
        self.processed_count = 0
        self.error_count = 0
        self.import_stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    async def process_csv_upload(self, file_content: io.BytesIO, store: str, replace_existing: bool = False):
        """Processa upload de CSV"""
        try:
            # Lê o CSV
            df = pd.read_csv(file_content)
            
            logger.info(f"📥 CSV recebido: {len(df)} linhas, loja: {store}")
            
            # Processa linha por linha
            products = []
            for _, row in df.iterrows():
                try:
                    product = self._parse_csv_row(row, store)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Erro ao processar linha: {e}")
                    self.error_count += 1
            
            # Insere no banco
            if products:
                result = await self.supabase.bulk_insert_products(products)
                
                self.import_stats.update({
                    'total': len(products),
                    'imported': result['inserted'],
                    'errors': result['errors']
                })
                
                logger.info(f"✅ CSV processado: {result['inserted']} produtos importados")
                return self.import_stats
            else:
                logger.warning("⚠️ Nenhum produto válido encontrado no CSV")
                return self.import_stats
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar CSV: {e}")
            raise
    
    def _parse_csv_row(self, row: pd.Series, default_store: str) -> Optional[Dict[str, Any]]:
        """Parse uma linha do CSV para produto"""
        try:
            # Detecta colunas (flexível para diferentes formatos)
            row_dict = row.to_dict()
            
            # Extrai informações básicas
            name = self._extract_field(row_dict, ['name', 'product', 'title', 'nome', 'produto'])
            link = self._extract_field(row_dict, ['link', 'url', 'affiliate_link', 'product_url'])
            
            if not name or not link:
                return None
            
            # Detecta loja do link
            store = detect_store(link) or default_store
            
            # Normaliza link
            affiliate_link = normalize_link(link)
            
            # Extrai preços
            current_price = self._extract_price(row_dict, ['price', 'current_price', 'preco', 'valor'])
            original_price = self._extract_price(row_dict, ['original_price', 'old_price', 'preco_original'])
            
            # Calcula desconto
            discount = None
            if current_price and original_price and original_price > current_price:
                discount = int(((original_price - current_price) / original_price) * 100)
            
            # Extrai outras informações
            category = self._extract_field(row_dict, ['category', 'categoria', 'department'])
            image_url = self._extract_field(row_dict, ['image', 'image_url', 'imagem', 'thumbnail'])
            coupon_code = self._extract_field(row_dict, ['coupon', 'cupom', 'voucher', 'discount_code'])
            
            # Cria objeto produto
            product = {
                'store': store,
                'name': name[:500],  # Limita tamanho
                'affiliate_link': affiliate_link,
                'original_link': link,
                'current_price': float(current_price) if current_price else 0.0,
                'original_price': float(original_price) if original_price else None,
                'discount_percentage': discount,
                'category': category,
                'image_url': image_url,
                'coupon_code': coupon_code,
                'source': 'csv_import',
                'source_file': 'uploaded.csv',
                'is_active': True,
                'tags': self._extract_tags(row_dict, name)
            }
            
            return product
            
        except Exception as e:
            logger.warning(f"Erro ao parse linha: {e}")
            return None
    
    def _extract_field(self, row_dict: Dict, possible_keys: List[str]) -> Optional[str]:
        """Extrai campo de dicionário tentando várias chaves"""
        for key in possible_keys:
            if key in row_dict:
                value = row_dict[key]
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
        return None
    
    def _extract_price(self, row_dict: Dict, possible_keys: List[str]) -> Optional[float]:
        """Extrai preço e converte para float"""
        price_str = self._extract_field(row_dict, possible_keys)
        if price_str:
            try:
                # Remove símbolos e converte
                price_str = price_str.replace('R$', '').replace('$', '').replace(',', '.').strip()
                return float(price_str)
            except:
                return None
        return None
    
    def _extract_tags(self, row_dict: Dict, name: str) -> List[str]:
        """Extrai tags do produto"""
        tags = []
        
        # Tenta extrair tags de coluna específica
        tags_field = self._extract_field(row_dict, ['tags', 'keywords'])
        if tags_field:
            tags.extend([tag.strip() for tag in tags_field.split(',')[:5]])
        
        # Adiciona tags baseadas no nome (ex: "Smartphone" → "smartphone")
        name_lower = name.lower()
        common_tags = {
            'smartphone': 'celular',
            'notebook': 'laptop',
            'fone': 'headphone',
            'bluetooth': 'wireless',
            'relogio': 'watch',
            'tenis': 'sneaker',
            'camiseta': 'tshirt'
        }
        
        for word, tag in common_tags.items():
            if word in name_lower:
                tags.append(tag)
        
        return list(set(tags))[:10]  # Limita a 10 tags

# Função principal de importação
async def process_csv_upload(file_content, store: str, replace_existing: bool = False):
    """Processa upload de CSV em background"""
    importer = CSVImporter()
    
    try:
        stats = await importer.process_csv_upload(file_content, store, replace_existing)
        
        # Log do resultado
        logger.info(f"""
        📊 Importação Concluída:
        Total processado: {stats['total']}
        Importados: {stats['imported']}
        Atualizados: {stats['updated']}
        Erros: {stats['errors']}
        Loja: {store}
        """)
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Falha na importação: {e}")
        raise

# Função para importação da Shopee diária
async def import_shopee_daily_csv(url: str):
    """Importa CSV diário da Shopee"""
    import requests
    
    try:
        logger.info(f"🔄 Baixando CSV diário da Shopee: {url}")
        
        # Baixa o CSV
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Processa o CSV
        file_content = io.BytesIO(response.content)
        importer = CSVImporter()
        
        stats = await importer.process_csv_upload(
            file_content,
            store='shopee',
            replace_existing=False
        )
        
        logger.info(f"✅ CSV Shopee importado: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao importar CSV Shopee: {e}")
        return None
