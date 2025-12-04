"""
Gera a página HTML estática de ofertas da Shopee a partir de shopee_products.json.
"""

import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_FILE = PROJECT_ROOT / 'data' / 'shopee_products.json'
OUTPUT_FILE = PROJECT_ROOT / 'Ofertas_Shopee.html'

# Mapeamento de categorias EN → PT-BR
CATEGORY_LABELS = {
    "Watches": "Relógios",
    "Home Appliances": "Eletrodomésticos",
    "Men Bags": "Bolsas Masculinas",
    "Men Clothes": "Roupas Masculinas",
    "Women Clothes": "Roupas Femininas",
    "Women Shoes": "Sapatos Femininos",
    "Men Shoes": "Sapatos Masculinos",
    "Mobile & Gadgets": "Celulares e Gadgets",
    "Health": "Saúde",
    "Beauty": "Beleza",
    "Home & Living": "Casa e Decoração",
    "Hobbies & Collections": "Hobbies e Coleções",
    "Food & Beverages": "Alimentos e Bebidas",
    "Pet Care": "Pet Care",
    "Sports & Outdoors": "Esportes",
    "Gaming & Consoles": "Games e Consoles",
    "Toys & Games": "Brinquedos",
    "Baby & Kids": "Bebês e Crianças",
    "Automotive": "Automotivo",
    "Travel & Luggage": "Viagem e Bagagem",
    "Stationery": "Papelaria",
    "Accessories": "Acessórios",
    "Electronics": "Eletrônicos",
}


def translate_category(cat_en: str) -> str:
    """Traduz categoria do inglês para português."""
    return CATEGORY_LABELS.get(cat_en, cat_en)


def format_price(value) -> str:
    """Formata preço para padrão brasileiro (R$ X.XXX,XX)."""
    if not value:
        return "R$ 0,00"
    try:
        val = float(value)
        # Se o valor vier em centavos (ex: 1999 = R$ 19,99), descomente:
        # val = val / 100
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def product_card_html(p: dict) -> str:
    nome = p.get('nome', 'Produto sem título')
    imagem = p.get('imagem', 'assets/placeholder.png')
    descricao = p.get('descricao', '')

    # Link de afiliado vindo do JSON
    link = p.get('link', '#')

    # Categoria traduzida
    categoria_raw = p.get('categoria', 'Geral')
    categoria = translate_category(categoria_raw)

    # Preços
    preco = float(p.get('preco', 0) or 0)
    preco_promo = float(p.get('preco_promocional', 0) or 0)
    desconto = int(p.get('desconto', 0) or 0)
    avaliacao = p.get('avaliacao', '')

    preco_final = preco_promo if preco_promo > 0 and preco_promo < preco else preco

    preco_original_html = ''
    if preco_promo > 0 and preco_promo < preco:
        preco_original_html = (
            f'<span class="text-gray-400 line-through text-sm">'
            f'{format_price(preco)}</span><br>'
        )

    desconto_badge = ''
    if desconto > 0:
        desconto_badge = (
            f'<span class="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 '
            f'rounded-full text-xs font-bold">-{desconto}%</span>'
        )

    rating_html = ''
    if avaliacao not in ('', '0', 0):
        rating_html = f'<span class="text-yellow-400 text-sm">⭐ {avaliacao}</span>'

    safe_nome_onclick = nome.replace("'", "").replace('"', '')

    return f"""
        <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300" data-category="{categoria}">
            <div class="relative">
                <a href="{link}" target="_blank" rel="noopener noreferrer sponsored"
                   onclick="showProductInfo('{safe_nome_onclick}')">
                    <img src="{imagem}" alt="{nome}" class="w-full h-48 object-cover" loading="lazy">
                </a>
                {desconto_badge}
                <span class="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-semibold">{categoria}</span>
            </div>
            <div class="p-4 flex flex-col h-full">
                <h3 class="text-lg font-semibold text-white mb-2 line-clamp-2 h-14">{nome}</h3>
                <p class="text-gray-400 text-sm mb-3 flex-grow line-clamp-3 cursor-pointer description-collapsible">
                    {descricao}
                </p>
                <div class="flex items-center justify-between mb-3">
                    <div>
                        {preco_original_html}
                        <span class="text-green-400 font-bold text-xl">{format_price(preco_final)}</span>
                    </div>
                    {rating_html}
                </div>
                <a href="{link}" target="_blank" rel="noopener noreferrer sponsored"
                   onclick="showProductInfo('{safe_nome_onclick}')"
                   class="mt-auto block w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded text-center transition-colors duration-300">
                    Comprar na Shopee
                </a>
            </div>
        </div>
    """
