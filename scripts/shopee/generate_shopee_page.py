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


def translate_category(cat_en):
    """Traduz categoria do inglês para português."""
    return CATEGORY_LABELS.get(cat_en, cat_en)


def format_price(value):
    """Formata preço para padrão brasileiro (R$ X.XXX,XX)."""
    if not value:
        return "R$ 0,00"
    try:
        val = float(value)
        # Se o valor vier em centavos (ex: 1999 = R$ 19,99), divida por 100
        # Caso contrário, comente a linha abaixo
        # val = val / 100
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


def product_card_html(p):
    nome = p.get('nome', 'Produto sem título')
    imagem = p.get('imagem', 'assets/placeholder.png')
    descricao = p.get('descricao', '')
    
   # Usa sempre o link vindo do JSON (já é o link de afiliado da Shopee)
    
    link = p.get('link', '#')
    
    # Categoria traduzida
    categoria_raw = p.get('categoria', 'Geral')
    categoria = translate_category(categoria_raw)
    
    # Preços
    preco = float(p.get('preco', 0) or 0)
    preco_promo = float(p.get('preco_promocional', 0) or 0)
    desconto = int(p.get('desconto', 0) or 0)
    avaliacao = p.get('avaliacao', '')

    # Define preço final
    preco_final = preco_promo if preco_promo > 0 and preco_promo < preco else preco

    # HTML do preço original (riscado)
    preco_original_html = ''
    if preco_promo > 0 and preco_promo < preco:
        preco_original_html = f'<span class="text-gray-400 line-through text-sm">{format_price(preco)}</span><br>'

    # Badge de desconto
    desconto_badge = ''
    if desconto > 0:
        desconto_badge = f'<span class="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">-{desconto}%</span>'

    # Avaliação (estrelas)
    rating_html = ''
    if avaliacao not in ('', '0', 0):
        rating_html = f'<span class="text-yellow-400 text-sm">⭐ {avaliacao}</span>'

    # Sanitiza nome para onclick
    safe_nome_onclick = nome.replace("'", "").replace('"', '')

    return f"""
        <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300" data-category="{categoria}">
            <div class="relative">
                <img src="{imagem}" alt="{nome}" class="w-full h-48 object-cover" loading="lazy">
                {desconto_badge}
                <span class="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-semibold">{categoria}</span>
            </div>
            <div class="p-4 flex flex-col h-full">
                <h3 class="text-lg font-semibold text-white mb-2 line-clamp-2 h-14">{nome}</h3>
                <p class="text-gray-400 text-sm mb-3 line-clamp-3 flex-grow">{descricao}</p>
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


def generate_html():
    if not DATA_FILE.exists():
        print(f"❌ Arquivo {DATA_FILE} não encontrado.")
        return False

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)

    if not products:
        print("⚠️ Nenhum produto encontrado em shopee_products.json")
        return False

    # Categorias únicas (já traduzidas)
    categories_raw = sorted(set(p.get('categoria', 'Geral') for p in products))
    categories = sorted(set(translate_category(c) for c in categories_raw))

    category_buttons = "\n".join(
        f'<button class="category-btn px-3 py-1.5 rounded-full bg-gray-700 hover:bg-orange-500 text-sm" data-category="{cat}">{cat}</button>'
        for cat in categories
    )

    cards_html = "\n".join(product_card_html(p) for p in products)

    last_update = datetime.now().strftime('%d/%m/%Y às %H:%M')

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  
  <title>Ofertas Shopee - Afiliado.Top | Melhores Promoções e Descontos</title>
  <meta name="description" content="Encontre as melhores ofertas da Shopee diretamente no Afiliado.Top! Produtos com desconto, atualizados automaticamente pelo datafeed.">
  <meta name="keywords" content="shopee, ofertas shopee, descontos shopee, promoções, afiliado top">
  <meta name="author" content="Afiliado.Top">

  <link rel="canonical" href="https://afiliadotop.github.io/Afiliado.top/Ofertas_Shopee.html">
  <link rel="icon" href="assets/favicon.ico" type="image/x-icon">

  <!-- Tailwind local -->
  <link rel="stylesheet" href="CSS/styles.css" />

  <!-- SweetAlert + Anime.js -->
  <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>

  <!-- Google Translate -->
  <script>
    function googleTranslateElementInit() {{
      new google.translate.TranslateElement(
        {{pageLanguage: 'pt', includedLanguages: 'en,es,fr,it,de,pt'}},
        'google_translate_element'
      );
    }}
  </script>
  <script src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>

  <!-- Google Ads -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9910874980055059"
     crossorigin="anonymous"></script>
</head>

<body class="bg-gray-900 text-white font-sans antialiased">

  <!-- HEADER -->
  <header class="bg-gray-800/95 backdrop-blur shadow-lg py-4 px-6 md:px-10 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto flex justify-between items-center">
      <a href="index.html" class="flex items-center space-x-3">
        <img src="assets/logo.png" alt="Afiliado.Top Logo" class="h-10 w-auto">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-white tracking-tight leading-tight">
            Afiliado.<span class="text-orange-400">Top</span>
          </h1>
          <p class="text-xs md:text-sm text-gray-300 -mt-1">Ofertas selecionadas da Shopee</p>
        </div>
      </a>

      <nav>
        <ul class="flex items-center space-x-6 text-sm md:text-base">
          <li><a href="index.html" class="text-gray-300 hover:text-white transition-colors">Início</a></li>
          <li><a href="Ofertas_Shopee.html" class="text-orange-400 font-semibold border-b-2 border-orange-400">Shopee</a></li>
          <li><a href="Ofertas_AliExpress.html" class="text-gray-300 hover:text-white transition-colors">AliExpress</a></li>
          <li><a href="contato.html" class="text-gray-300 hover:text-white transition-colors">Contato</a></li>
          <li class="hidden md:block">
            <div id="google_translate_element" class="bg-gray-700 p-2 rounded-md text-xs shadow-sm"></div>
          </li>
        </ul>
      </nav>
    </div>
  </header>

  <main class="max-w-7xl mx-auto py-10 px-4 md:px-6">
    <!-- HERO -->
    <section class="text-center mb-8">
      <h2 class="text-3xl md:text-4xl font-extrabold mb-2">🛍️ Ofertas Exclusivas Shopee</h2>
      <p class="text-lg text-gray-200 mb-2">
        As melhores promoções da Shopee, atualizadas automaticamente via datafeed.
      </p>
      <p class="text-sm text-gray-400">
        Última atualização: <strong>{last_update}</strong> &middot; Total de ofertas: <strong>{len(products)}</strong>
      </p>
    </section>

    <!-- FILTROS -->
    <section class="mb-8">
      <div class="flex flex-col md:flex-row items-center justify-between gap-4">
        <input
          type="text"
          id="searchBar"
          placeholder="Buscar por nome ou descrição..."
          class="flex-grow p-3 rounded-lg bg-gray-800 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        <div class="flex flex-wrap gap-2 justify-center md:justify-end">
          <button class="category-btn px-3 py-1.5 rounded-full bg-orange-500 hover:bg-orange-600 text-sm" data-category="all">
            Todas
          </button>
          {category_buttons}
        </div>
      </div>
    </section>

    <!-- LISTA DE PRODUTOS -->
    <section>
      <div id="productsGrid" class="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {cards_html}
      </div>
    </section>
  </main>

  <!-- FOOTER -->
  <footer class="bg-gray-800 text-center p-4 mt-10 shadow-inner">
    <p class="text-gray-400 text-sm">
      &copy; 2025 Afiliado.Top - Todos os direitos reservados.<br>
      Ao clicar nos links de afiliado e realizar uma compra, podemos receber uma comissão sem custo adicional para você.
    </p>
  </footer>

  <!-- Botão voltar ao topo -->
  <button
    id="btn-topo"
    class="fixed bottom-6 right-6 z-40 p-3 rounded-full bg-orange-600 text-white shadow-xl hover:bg-orange-700 transition-all duration-300 transform hover:scale-110 hidden opacity-0"
  >
    ⬆️
  </button>

  <!-- Scripts globais -->
  <script src="JS/scripts.js"></script>

  <script>
    // Filtro por categoria + busca
    const searchBar = document.getElementById('searchBar');
    const cards = Array.from(document.querySelectorAll('#productsGrid > div[data-category]'));
    const categoryButtons = document.querySelectorAll('.category-btn');

    function applyFilters() {{
      const term = searchBar.value.toLowerCase();
      const activeCategoryBtn = document.querySelector('.category-btn.active') || document.querySelector('.category-btn[data-category="all"]');
      const category = activeCategoryBtn ? activeCategoryBtn.getAttribute('data-category') : 'all';

      cards.forEach(card => {{
        const cardCategory = card.getAttribute('data-category') || 'Geral';
        const text = card.innerText.toLowerCase();

        const matchText = text.includes(term);
        const matchCategory = category === 'all' || cardCategory === category;

        card.style.display = (matchText && matchCategory) ? 'block' : 'none';
      }});
    }}

    categoryButtons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        categoryButtons.forEach(b => b.classList.remove('active', 'bg-orange-600'));
        btn.classList.add('active', 'bg-orange-600');
        applyFilters();
      }});
    }});

    searchBar.addEventListener('input', applyFilters);

    // Função global para popup de info
    function showProductInfo(nomeProduto) {{
      if (window.Swal && window.anime) {{
        Swal.fire({{
          title: nomeProduto,
          html: 'Você será redirecionado para a página de compra.<br>Ao comprar, você apoia nosso projeto!',
          icon: 'info',
          confirmButtonText: 'Entendi',
          didOpen: (popup) => {{
            anime({{
              targets: popup,
              scale: [0.5, 1],
              opacity: [0, 1],
              duration: 800,
              easing: 'easeOutElastic(1, .8)'
            }});
          }}
        }});
      }} else {{
        alert(nomeProduto + '\\n\\nVocê será redirecionado para a página de compra. Ao comprar, você apoia nosso projeto!');
      }}
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Página Shopee gerada em {OUTPUT_FILE} com {len(products)} produtos.")
    return True


if __name__ == "__main__":
    ok = generate_html()
    exit(0 if ok else 1)
