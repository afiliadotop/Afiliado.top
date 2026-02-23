"""
gerar_monte_carlo.py
Baixa o datafeed Monte Carlo Joias da Awin (CSV zip), filtra produtos e gera Ofertas_MonteCarlo.html
"""

import zipfile, csv, io, urllib.request, html, os, re

# === Carrega .env ===
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
FID     = _env.get('MONTE_CARLO_FID', '96100')
BID     = _env.get('MONTE_CARLO_BID', '64323,65873,66027,64329,66795,63485,67481,67871,64201,68801')

if not API_KEY:
    raise SystemExit('❌ AWIN_API_KEY não encontrada no arquivo JS/.env')

COLS = (
    "aw_deep_link,product_name,aw_product_id,merchant_product_id,merchant_image_url,"
    "description,merchant_category,search_price,merchant_name,merchant_id,category_name,"
    "category_id,aw_image_url,currency,store_price,delivery_cost,merchant_deep_link,language,"
    "last_updated,display_price,data_feed_id,brand_name,colour,product_short_description,"
    "specifications,condition,product_model,rrp_price,saving,savings_percent,base_price,"
    "large_image,merchant_thumb_url,aw_thumb_url,reviews,average_rating,number_available"
)

FEED_URL = (
    f"https://productdata.awin.com/datafeed/download/apikey/{API_KEY}/language/pt/"
    f"fid/{FID}/bid/{BID}/"
    f"columns/{COLS}"
    "/format/csv/delimiter/%2C/compression/zip/adultcontent/1/"
)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "Ofertas_MonteCarlo.html")
MAX_PRODUCTS = 200

print("⬇️  Baixando datafeed Monte Carlo da Awin...")
req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=120) as resp:
    zip_bytes = resp.read()
print(f"✅ Baixado: {len(zip_bytes):,} bytes comprimidos")

print("📦 Descomprimindo ZIP...")
with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
    csv_name = next(n for n in zf.namelist() if n.endswith('.csv'))
    raw = zf.read(csv_name).decode('utf-8', errors='replace')
print(f"✅ CSV: {len(raw):,} chars ({csv_name})")

reader = csv.DictReader(io.StringIO(raw))
products = []
seen_names = set()

for row in reader:
    try:
        price = float(row.get("search_price", 0) or 0)
        if price <= 0:
            continue
        # Prefere large_image, depois aw_image_url, depois merchant_image_url
        image = (
            row.get("large_image") or
            row.get("aw_image_url") or
            row.get("merchant_image_url") or
            row.get("merchant_thumb_url") or ""
        ).strip()
        if not image:
            continue
        link = (row.get("aw_deep_link") or "").strip()
        if not link:
            continue
        name = (row.get("product_name") or "").strip()
        if not name or name in seen_names:
            continue
        seen_names.add(name)

        rrp   = float(row.get("rrp_price", 0) or 0)
        store = float(row.get("store_price", 0) or 0)
        # Calcula desconto: prefere savings_percent do feed, senão calcula
        disc_pct = 0
        sp = (row.get("savings_percent") or "").strip().replace('%','')
        if sp:
            try: disc_pct = int(float(sp))
            except: pass
        if disc_pct == 0 and rrp > price:
            disc_pct = round((1 - price / rrp) * 100)
        if disc_pct == 0 and store > price:
            disc_pct = round((1 - price / store) * 100)

        ref_price = rrp if rrp > price else (store if store > price else 0)

        cat    = (row.get("merchant_category") or row.get("category_name") or "").strip()
        desc   = (row.get("product_short_description") or row.get("description") or "").strip()
        colour = (row.get("colour") or "").strip()
        brand  = (row.get("brand_name") or "Monte Carlo").strip()
        rating = (row.get("average_rating") or "").strip()
        try:
            rating_f = float(rating)
            stars = "⭐" * min(5, round(rating_f))
        except:
            stars = ""

        products.append({
            "name": name,
            "price": price,
            "ref_price": ref_price,
            "discount": disc_pct,
            "image": image,
            "link": link,
            "desc": desc[:200] if desc else "",
            "cat": cat,
            "colour": colour,
            "brand": brand,
            "stars": stars,
        })
    except Exception:
        continue
    if len(products) >= MAX_PRODUCTS:
        break

print(f"🛍️  Produtos válidos: {len(products)}")

# Gerar cards HTML
def card(p):
    badge = f'<span class="badge-discount">-{p["discount"]}%</span>' if p["discount"] >= 5 else ""
    ref_str = (f'<span class="text-gray-500 line-through text-sm">R$ {p["ref_price"]:.2f}</span>'
               if p["ref_price"] > p["price"] else "")
    cat_html = f'<p class="text-xs text-yellow-400 font-semibold mb-1">{html.escape(p["cat"])}</p>' if p["cat"] else ""
    desc_html = (f'<p class="text-gray-400 text-xs mb-2 flex-1 line-clamp-3">{html.escape(p["desc"])}</p>'
                 if p["desc"] else '<p class="flex-1"></p>')
    colour_html = (f'<p class="text-xs text-gray-500 mb-2">{html.escape(p["colour"])}</p>'
                   if p["colour"] else "")
    stars_html = f'<span class="text-yellow-300 text-xs mr-1">{p["stars"]}</span>' if p["stars"] else ""
    return f"""
                    <a href="{html.escape(p['link'])}" target="_blank" rel="sponsored"
                        class="product-card bg-gray-800 rounded-xl overflow-hidden shadow-lg flex flex-col">
                        <div class="relative bg-gray-900" style="aspect-ratio:1/1">
                            <img src="{html.escape(p['image'])}" alt="{html.escape(p['name'])}"
                                class="w-full h-full object-contain p-2" loading="lazy"
                                onerror="this.src='assets/logo.png'">
                            {badge}
                        </div>
                        <div class="p-4 flex flex-col flex-1">
                            {cat_html}
                            <h3 class="card-title font-bold text-sm mb-1 leading-snug">{html.escape(p['name'])}</h3>
                            {colour_html}
                            {desc_html}
                            <div class="flex items-center gap-2 mb-3 flex-wrap">
                                {stars_html}
                                {ref_str}
                                <span class="text-yellow-400 font-bold text-lg">R$ {p['price']:.2f}</span>
                            </div>
                            <button class="btn-mc w-full bg-yellow-600 hover:bg-yellow-700 text-gray-900 text-sm font-bold py-2 rounded-lg transition">
                                Ver na Monte Carlo →
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
    <title>Monte Carlo Joias - Relógios e Joias com Desconto | Afiliado.Top</title>
    <meta name="description" content="Compre relógios e joias Monte Carlo com os melhores preços. {total} produtos atualizados via datafeed Awin.">
    <link rel="icon" href="assets/favicon.ico" type="image/x-icon">
    <link rel="stylesheet" href="/CSS/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        @media (hover: hover) {{
            .product-card:hover {{ transform: translateY(-6px); box-shadow: 0 20px 40px rgba(202,138,4,0.25); border-color: rgba(202,138,4,0.5); }}
            .product-card:hover .card-title {{ color: #f59e0b; }}
            .product-card:hover .card-img img {{ transform: scale(1.06); }}
        }}
        @media (hover: none) {{ .product-card {{ transform: none !important; }} }}
        .product-card {{ border: 1px solid transparent; transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease; }}
        .card-title {{ transition: color 0.3s ease; }}
        .card-img {{ aspect-ratio:1/1; background:#111; display:flex; align-items:center; justify-content:center; overflow:hidden; }}
        .card-img img {{ width:100%; height:100%; object-fit:contain; padding:8px; transition:transform 0.4s ease; }}
        .badge-discount {{ position:absolute; top:8px; right:8px; background:#ca8a04; color:white; font-weight:bold; font-size:.72rem; padding:2px 8px; border-radius:999px; }}
        .hero-mc {{ background: linear-gradient(135deg, #0a0a0a 0%, #1a1500 40%, #2a1f00 100%); }}
        #bar1,#bar2,#bar3 {{ display:block;width:24px;height:2px;background:white;transition:transform .3s ease,opacity .3s ease; }}
        #bar1,#bar2 {{ margin-bottom:5px; }}
        .line-clamp-3 {{ display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
        html {{ scroll-behavior:smooth; }}
        .btn-mc {{ transition: background-color 0.3s ease; }}
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
                    <li><a href="Ofertas_Adidas.html" class="text-gray-300 hover:text-white transition font-medium">Adidas</a></li>
                    <li><a href="Ofertas_MonteCarlo.html" class="text-yellow-400 font-semibold hover:text-yellow-300 transition">Monte Carlo</a></li>
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
                <li><a href="Ofertas_Adidas.html" class="block py-2 px-3 rounded-lg text-gray-300 hover:bg-gray-700 transition">Adidas</a></li>
                <li><a href="Ofertas_MonteCarlo.html" class="block py-2 px-3 rounded-lg text-yellow-400 font-semibold hover:bg-gray-700 transition">Monte Carlo</a></li>
                <li><a href="contato.html" class="block py-2 px-3 rounded-lg text-gray-300 hover:bg-gray-700 transition">✉️ Contato</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section class="hero-mc py-14 px-4 md:py-20 md:px-10 text-center">
            <div class="max-w-4xl mx-auto">
                <span class="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-yellow-900/40 border border-yellow-600/50 text-yellow-300 text-xs mb-4">
                    💍 {total} produtos · Atualizado via datafeed Awin · Monte Carlo Joias Oficial
                </span>
                <h1 class="text-3xl sm:text-5xl md:text-6xl font-extrabold leading-tight mb-4">
                    <span class="text-yellow-400">Monte Carlo</span> Joias
                </h1>
                <p class="text-base md:text-xl text-gray-300 mb-6 max-w-2xl mx-auto">
                    Relógios, anéis, brincos e pulseiras com <strong class="text-white">os melhores preços</strong>. Produtos reais do datafeed oficial Awin.
                </p>
                <div class="flex flex-col sm:flex-row justify-center gap-4 mb-4">
                    <input type="text" id="searchMC" placeholder="🔍 Buscar joia ou relógio..."
                        class="w-full sm:w-96 p-3 rounded-lg bg-gray-800 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-500">
                </div>
            </div>
        </section>

        <section class="py-10 px-4 md:px-10 bg-gray-900">
            <div class="max-w-7xl mx-auto">
                <p class="text-gray-400 text-xs text-center mb-6">
                    Mostrando {total} produtos · Links de afiliado via <strong>Awin</strong> · Clique e compre no site oficial da Monte Carlo
                </p>
                <div id="mcGrid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
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
                <a href="Ofertas_Adidas.html" class="hover:text-white transition">Adidas</a>
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
        var search=document.getElementById('searchMC'),cards=[...document.querySelectorAll('#mcGrid > a')],noResults=document.getElementById('no-results');
        if(search){{search.addEventListener('input',function(){{var q=this.value.toLowerCase().trim(),vis=0;cards.forEach(function(c){{var txt=c.innerText.toLowerCase();var show=!q||txt.includes(q);c.style.display=show?'':'none';if(show)vis++;}});noResults.classList.toggle('hidden',vis>0);}});}}
    </script>
</body>
</html>"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(template)

print(f"✅ Arquivo gerado: {OUTPUT_FILE}")
print(f"📄 Tamanho: {os.path.getsize(OUTPUT_FILE):,} bytes")
print(f"🛍️  Total de produtos: {total}")
