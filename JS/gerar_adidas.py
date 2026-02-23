"""
gerar_adidas.py
Baixa o datafeed Adidas da Awin (CSV gzip), filtra produtos e gera Ofertas_Adidas.html
"""

import gzip, csv, io, urllib.request, html, os, json, re

# === Carrega API key do .env (nunca expor no GitHub!) ===
def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env

_env = load_env(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
API_KEY = _env.get('AWIN_API_KEY', '')

if not API_KEY:
    raise SystemExit('❌ AWIN_API_KEY não encontrada no arquivo JS/.env')

FEED_URL = (
    f"https://productdata.awin.com/datafeed/download/apikey/{API_KEY}/language/pt/"
    "fid/95015/bid/63213/"
    "columns/aw_deep_link,product_name,aw_product_id,merchant_product_id,"
    "merchant_image_url,description,merchant_category,search_price,merchant_name,"
    "merchant_id,category_name,category_id,aw_image_url,currency,store_price,"
    "delivery_cost,merchant_deep_link,language,last_updated,display_price,data_feed_id"
    "/format/csv/delimiter/%2C/compression/gzip/adultcontent/1/"
)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "Ofertas_Adidas.html")
MAX_PRODUCTS = 200  # quantos produtos no máximo gerar

print("⬇️  Baixando datafeed Adidas da Awin...")
req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=120) as resp:
    compressed = resp.read()
print(f"✅ Baixado: {len(compressed):,} bytes comprimidos")

print("📦 Descomprimindo...")
raw = gzip.decompress(compressed).decode("utf-8", errors="replace")
print(f"✅ CSV: {len(raw):,} chars")

reader = csv.DictReader(io.StringIO(raw))
products = []
for row in reader:
    try:
        price = float(row.get("search_price", 0) or 0)
        store_price = float(row.get("store_price", 0) or 0)
        if price <= 0:
            continue
        image = (row.get("aw_image_url") or row.get("merchant_image_url") or "").strip()
        if not image:
            continue
        link = (row.get("aw_deep_link") or "").strip()
        if not link:
            continue
        name = (row.get("product_name") or "").strip()
        if not name:
            continue
        desc = (row.get("description") or "").strip()
        cat = (row.get("merchant_category") or row.get("category_name") or "").strip()
        disc = 0
        if store_price > price:
            disc = round((1 - price / store_price) * 100)
        products.append({
            "name": name,
            "price": price,
            "store_price": store_price,
            "discount": disc,
            "image": image,
            "link": link,
            "desc": desc[:200] if desc else "",
            "cat": cat,
        })
    except Exception:
        continue
    if len(products) >= MAX_PRODUCTS:
        break

print(f"🛍️  Produtos válidos: {len(products)}")

# Gerar cards HTML
def card(p):
    badge = f'<span class="badge-discount">-{p["discount"]}%</span>' if p["discount"] >= 5 else ""
    store_str = f'<span class="text-gray-500 line-through text-sm">R$ {p["store_price"]:.2f}</span>' if p["store_price"] > p["price"] else ""
    cat_html = f'<p class="text-xs text-green-400 font-semibold mb-1">{html.escape(p["cat"])}</p>' if p["cat"] else ""
    desc_html = f'<p class="text-gray-400 text-xs mb-3 flex-1 line-clamp-3">{html.escape(p["desc"])}</p>' if p["desc"] else '<p class="flex-1"></p>'
    return f"""
                    <a href="{html.escape(p['link'])}" target="_blank" rel="sponsored"
                        class="product-card bg-gray-800 rounded-xl overflow-hidden shadow-lg flex flex-col">
                        <div class="relative overflow-hidden h-48 bg-gray-900">
                            <img src="{html.escape(p['image'])}" alt="{html.escape(p['name'])}"
                                class="w-full h-full object-contain p-3" loading="lazy"
                                onerror="this.src='assets/logo.png'">
                            {badge}
                        </div>
                        <div class="p-4 flex flex-col flex-1">
                            {cat_html}
                            <h3 class="card-title font-bold text-sm mb-1 leading-snug">{html.escape(p['name'])}</h3>
                            {desc_html}
                            <div class="flex items-center gap-2 mb-3">
                                {store_str}
                                <span class="text-green-400 font-bold text-lg">R$ {p['price']:.2f}</span>
                            </div>
                            <button class="btn-outlet w-full bg-green-600 text-white text-sm font-bold py-2 rounded-lg">
                                Comprar na Adidas →
                            </button>
                        </div>
                    </a>"""

cards_html = "\n".join(card(p) for p in products)
total = len(products)

template = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Outlet Adidas - Tênis e Roupas com até 50% Off | Afiliado.Top</title>
    <meta name="description" content="Compre no outlet oficial da Adidas com os melhores preços. {total} produtos atualizados via datafeed. Links reais de afiliado.">
    <link rel="icon" href="assets/favicon.ico" type="image/x-icon">
    <link rel="stylesheet" href="/CSS/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        @media (hover: hover) {{
            .product-card:hover {{ transform: translateY(-6px); box-shadow: 0 20px 40px rgba(0,168,98,0.2); border-color: rgba(0,168,98,0.5); }}
            .product-card:hover .card-title {{ color: #00a862; }}
            .product-card:hover .btn-outlet {{ background-color: #007a48; }}
        }}
        @media (hover: none) {{ .product-card {{ transform: none !important; }} }}
        .product-card {{ border: 1px solid transparent; transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease; }}
        .card-title {{ transition: color 0.3s ease; }}
        .btn-outlet {{ transition: background-color 0.3s ease; }}
        .badge-discount {{ position:absolute; top:8px; right:8px; background:#00a862; color:white; font-weight:bold; font-size:.72rem; padding:2px 8px; border-radius:999px; }}
        .hero-adidas {{ background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 40%, #0d2b1a 100%); }}
        #bar1,#bar2,#bar3 {{ display:block;width:24px;height:2px;background:white;transition:transform .3s ease,opacity .3s ease; }}
        #bar1,#bar2 {{ margin-bottom:5px; }}
        .line-clamp-3 {{ display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
        html {{ scroll-behavior:smooth; }}
    </style>
</head>
<body class="bg-gray-900 text-white font-sans antialiased">

    <!-- HEADER -->
    <header class="bg-gray-800/95 backdrop-blur shadow-lg py-4 px-4 md:px-10 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <a href="index.html" class="flex items-center space-x-3 shrink-0">
                <img src="assets/logo.png" alt="Afiliado.Top Logo" class="h-10 w-auto">
                <div>
                    <span class="text-xl md:text-2xl font-bold text-white tracking-tight">Afiliado.<span class="text-orange-400">Top</span></span>
                    <p class="text-xs text-gray-300 hidden sm:block">Ofertas selecionadas diariamente</p>
                </div>
            </a>
            <nav class="hidden md:block">
                <ul class="flex items-center space-x-6 text-sm">
                    <li><a href="index.html" class="text-gray-300 hover:text-white transition font-medium">Início</a></li>
                    <li><a href="Ofertas_Shopee.html" class="text-gray-300 hover:text-white transition font-medium">Shopee</a></li>
                    <li><a href="Ofertas_Adidas.html" class="text-green-400 font-semibold hover:text-green-300 transition">Adidas</a></li>
                    <li><a href="contato.html" class="text-gray-300 hover:text-white transition font-medium">Contato</a></li>
                </ul>
            </nav>
            <button id="menu-toggle" class="md:hidden flex flex-col justify-center items-center p-2 rounded-lg hover:bg-gray-700 transition" aria-label="Abrir menu">
                <span id="bar1"></span><span id="bar2"></span><span id="bar3"></span>
            </button>
        </div>
        <nav id="mobile-menu" class="hidden md:hidden mt-3 pb-3 border-t border-gray-700">
            <ul class="flex flex-col gap-1 pt-3 px-2 text-sm">
                <li><a href="index.html" class="block py-2 px-3 rounded-lg text-gray-300 hover:bg-gray-700 transition">🏠 Início</a></li>
                <li><a href="Ofertas_Shopee.html" class="block py-2 px-3 rounded-lg text-gray-300 hover:bg-gray-700 transition">🛍️ Shopee</a></li>
                <li><a href="Ofertas_Adidas.html" class="block py-2 px-3 rounded-lg text-green-400 font-semibold hover:bg-gray-700 transition">👟 Adidas Outlet</a></li>
                <li><a href="contato.html" class="block py-2 px-3 rounded-lg text-gray-300 hover:bg-gray-700 transition">✉️ Contato</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section class="hero-adidas py-14 px-4 md:py-20 md:px-10 text-center">
            <div class="max-w-4xl mx-auto">
                <span class="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-green-900/60 border border-green-600/50 text-green-300 text-xs mb-4">
                    👟 {total} produtos · Atualizado via datafeed Awin · Link oficial Adidas
                </span>
                <h1 class="text-3xl sm:text-5xl md:text-6xl font-extrabold leading-tight mb-4">
                    Outlet <span class="text-green-400">Adidas</span>
                </h1>
                <p class="text-base md:text-xl text-gray-300 mb-6 max-w-2xl mx-auto">
                    Tênis, roupas e acessórios com <strong class="text-white">até 50% de desconto</strong> no outlet oficial. Preços reais do datafeed Awin.
                </p>
                <div class="flex flex-col sm:flex-row justify-center gap-4 mb-4">
                    <input type="text" id="searchAdidas" placeholder="🔍 Buscar produto Adidas..."
                        class="w-full sm:w-96 p-3 rounded-lg bg-gray-800 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500">
                </div>
            </div>
        </section>

        <section class="py-10 px-4 md:px-10 bg-gray-900">
            <div class="max-w-7xl mx-auto">
                <p class="text-gray-400 text-xs text-center mb-6">
                    Mostrando {total} produtos · Links de afiliado via <strong>Awin</strong> · Clique e compre no site oficial da Adidas
                </p>
                <div id="adidasGrid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
{cards_html}
                </div>
                <p id="no-results" class="hidden text-center text-gray-400 mt-8">Nenhum produto encontrado.</p>
            </div>
        </section>
    </main>

    <footer class="bg-gray-800 py-8 px-6 text-center text-gray-400">
        <div class="max-w-7xl mx-auto">
            <p>&copy; 2025 Afiliado.Top - Todos os direitos reservados.</p>
            <p class="text-sm mt-2">Links de afiliado Awin. Ao comprar, podemos receber comissão sem custo adicional para você.</p>
            <div class="mt-4 flex justify-center space-x-6 text-sm">
                <a href="index.html" class="hover:text-white transition">Início</a>
                <span>|</span>
                <a href="Ofertas_Shopee.html" class="hover:text-white transition">Shopee</a>
                <span>|</span>
                <a href="contato.html" class="hover:text-white transition">Contato</a>
            </div>
        </div>
    </footer>

    <script src="/JS/scripts.js"></script>
    <script>
        // Hamburguer
        var mt=document.getElementById('menu-toggle'),mm=document.getElementById('mobile-menu'),b1=document.getElementById('bar1'),b2=document.getElementById('bar2'),b3=document.getElementById('bar3');
        if(mt&&mm){{mt.addEventListener('click',function(){{var o=!mm.classList.contains('hidden');mm.classList.toggle('hidden');if(o){{b1.style.transform='';b2.style.opacity='1';b3.style.transform='';}}else{{b1.style.transform='translateY(7px) rotate(45deg)';b2.style.opacity='0';b3.style.transform='translateY(-7px) rotate(-45deg)';}}}});mm.querySelectorAll('a').forEach(function(l){{l.addEventListener('click',function(){{mm.classList.add('hidden');b1.style.transform='';b2.style.opacity='1';b3.style.transform='';}})}});}}

        // Busca
        var search=document.getElementById('searchAdidas'),cards=[...document.querySelectorAll('#adidasGrid > a')],noResults=document.getElementById('no-results');
        if(search){{search.addEventListener('input',function(){{var q=this.value.toLowerCase().trim(),vis=0;cards.forEach(function(c){{var txt=c.innerText.toLowerCase();var show=!q||txt.includes(q);c.style.display=show?'':'none';if(show)vis++;}});noResults.classList.toggle('hidden',vis>0);}});}}
    </script>
</body>
</html>"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(template)

print(f"✅ Arquivo gerado: {OUTPUT_FILE}")
print(f"📄 Tamanho: {os.path.getsize(OUTPUT_FILE):,} bytes")
print(f"🛍️  Total de produtos: {total}")
