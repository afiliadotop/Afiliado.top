// Afiliado.Top — scripts.js
// v2.0 — Social Media Ready 🚀

// =============================================
// 1. UTM TRACKING — captura e persiste UTMs
// =============================================
(function () {
    var params = new URLSearchParams(window.location.search);
    var utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
    var utmData = {};

    utmKeys.forEach(function (key) {
        var val = params.get(key);
        if (val) {
            sessionStorage.setItem(key, val);
            utmData[key] = val;
        } else {
            var stored = sessionStorage.getItem(key);
            if (stored) utmData[key] = stored;
        }
    });

    window._utmData = utmData;
})();

// =============================================
// 2. BARRA DE PERSONALIZAÇÃO POR REDE SOCIAL
// Aparece automaticamente quando utm_source é reconhecido
// =============================================
(function () {
    var src = (window._utmData && window._utmData.utm_source) || '';
    var socialSources = ['tiktok', 'instagram', 'facebook', 'whatsapp', 'twitter', 'youtube'];
    if (!src || socialSources.indexOf(src.toLowerCase()) === -1) return;

    var msgs = {
        tiktok:    '🎵 Você veio do TikTok! Veja as ofertas que estão viralizando →',
        instagram: '📸 Você veio do Instagram! Confira as ofertas em destaque hoje →',
        facebook:  '👍 Você veio do Facebook! Veja as melhores promoções do dia →',
        whatsapp:  '💬 Oferta compartilhada no WhatsApp! Não perca, é por tempo limitado →',
        youtube:   '▶️ Você veio do YouTube! Confira as ofertas que separamos para você →',
        twitter:   '🐦 Você veio do X/Twitter! Veja o que está em alta agora →'
    };

    var msg = msgs[src.toLowerCase()] || '🔥 Oferta especial para você! Confira as melhores promoções →';

    document.addEventListener('DOMContentLoaded', function () {
        var bar = document.createElement('div');
        bar.id = 'social-banner';
        bar.style.cssText = [
            'background:linear-gradient(90deg,#7c3aed,#4f46e5)',
            'color:#fff',
            'text-align:center',
            'padding:10px 40px 10px 16px',
            'font-size:.85rem',
            'font-weight:600',
            'cursor:pointer',
            'position:relative',
            'z-index:49'
        ].join(';');

        bar.innerHTML = msg +
            '<button onclick="this.parentElement.remove()" title="Fechar" ' +
            'style="position:absolute;right:12px;top:50%;transform:translateY(-50%);' +
            'background:none;border:none;color:#fff;font-size:1.2rem;cursor:pointer;line-height:1;">×</button>';

        bar.addEventListener('click', function (e) {
            if (e.target.tagName !== 'BUTTON') {
                var lojasEl = document.getElementById('lojas');
                if (lojasEl) lojasEl.scrollIntoView({ behavior: 'smooth' });
            }
        });

        var body = document.body;
        body.insertBefore(bar, body.firstElementChild);
    });
})();

// =============================================
// 3. TIKTOK PIXEL — eventos de conversão
// =============================================
(function () {
    document.addEventListener('DOMContentLoaded', function () {
        if (!window.ttq) return;

        // ViewContent quando vem de fonte social
        var src = (window._utmData && window._utmData.utm_source) || '';
        if (src) {
            window.ttq.track('ViewContent', {
                content_name: 'Homepage Afiliado.Top',
                content_category: 'Ofertas e Descontos',
                utm_source: src
            });
        }

        // Rastreia cliques em CTAs de lojas afiliadas
        document.querySelectorAll('a[rel*="sponsored"]').forEach(function (link) {
            link.addEventListener('click', function () {
                var nameEl = this.querySelector('strong, h4, h3');
                var storeName = nameEl ? nameEl.textContent.trim() : 'Loja Parceira';
                window.ttq.track('ClickButton', {
                    content_name: 'CTA — ' + storeName,
                    content_category: 'Afiliado'
                });
            });
        });
    });
})();

// =============================================
// 4. BOTÃO WHATSAPP SHARE (mobile flutuante)
// Aparece apenas em dispositivos móveis
// =============================================
(function () {
    document.addEventListener('DOMContentLoaded', function () {
        if (window.innerWidth >= 768) return; // desktop não precisa

        var pageUrl = encodeURIComponent(
            window.location.origin + window.location.pathname +
            '?utm_source=whatsapp&utm_medium=social&utm_campaign=share_organico'
        );
        var text = encodeURIComponent('🔥 Achei essas ofertas incríveis no Afiliado.Top! Dá uma olhada: ');

        var btn = document.createElement('a');
        btn.href = 'https://wa.me/?text=' + text + pageUrl;
        btn.target = '_blank';
        btn.rel = 'noopener noreferrer';
        btn.id = 'whatsapp-share-btn';
        btn.setAttribute('aria-label', 'Compartilhar ofertas no WhatsApp');

        btn.innerHTML = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" ',
            'style="width:20px;height:20px;flex-shrink:0">',
            '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15',
            '-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475',
            '-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52',
            '.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207',
            '-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372',
            '-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487',
            '.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413',
            '.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004',
            'a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374',
            'a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898',
            'a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884',
            'm8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892',
            'c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005',
            'c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>',
            '</svg>',
            '<span>Compartilhar</span>'
        ].join('');

        btn.style.cssText = [
            'position:fixed',
            'bottom:72px',
            'right:16px',
            'z-index:1000',
            'background:#25D366',
            'color:#fff',
            'display:flex',
            'align-items:center',
            'gap:8px',
            'padding:10px 16px',
            'border-radius:50px',
            'font-weight:700',
            'font-size:.82rem',
            'box-shadow:0 4px 20px rgba(37,211,102,.5)',
            'text-decoration:none',
            'transition:transform .2s,box-shadow .2s'
        ].join(';');

        btn.addEventListener('touchstart', function () {
            this.style.transform = 'scale(0.96)';
        }, { passive: true });
        btn.addEventListener('touchend', function () {
            this.style.transform = '';
        });

        document.body.appendChild(btn);
    });
})();

// =============================================
// 5. CONTADOR AO VIVO REALISTA
// O elemento com id="live-count" no HTML é atualizado
// =============================================
(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var el = document.getElementById('live-count');
        if (!el) return;

        // Base varia com a hora do dia (mais realista)
        var hour = new Date().getHours();
        var base = hour >= 19 ? 380 : hour >= 17 ? 290 : hour >= 12 ? 210 : hour >= 9 ? 150 : 80;
        var count = base + Math.floor(Math.random() * 70);
        el.textContent = count;

        // Pequenas variações a cada 10-18 segundos
        function fluctuate() {
            var delta = Math.floor(Math.random() * 7) - 3;
            count = Math.max(40, Math.min(600, count + delta));
            el.textContent = count;
            setTimeout(fluctuate, 10000 + Math.random() * 8000);
        }
        setTimeout(fluctuate, 10000 + Math.random() * 8000);
    });
})();

// =============================================
// 6. FUNCIONALIDADES ORIGINAIS DO SITE
// =============================================
document.addEventListener('DOMContentLoaded', function () {

    // Torna imagens dos produtos clicáveis (overlay)
    document.querySelectorAll('#productsGrid > div').forEach(function (card) {
        var buyLink = card.querySelector('a[href]');
        var imgWrapper = card.querySelector('.relative');

        if (buyLink && imgWrapper) {
            var href = buyLink.getAttribute('href');
            var productName = (card.querySelector('img') || {}).alt || '';

            var overlay = document.createElement('a');
            overlay.href = href;
            overlay.target = '_blank';
            overlay.rel = 'noopener noreferrer sponsored';
            overlay.title = productName;
            overlay.setAttribute('aria-label', 'Ver ' + productName + ' na loja');
            overlay.style.cssText = 'position:absolute;inset:0;z-index:10;display:block;cursor:pointer;';

            imgWrapper.style.position = 'relative';
            imgWrapper.appendChild(overlay);
        }
    });

    // Botão "Voltar ao Topo"
    var btnTopo = document.getElementById('btn-topo');
    if (btnTopo) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                btnTopo.style.display = 'block';
                if (window.anime) {
                    anime({ targets: btnTopo, opacity: [0, 1], translateY: [20, 0], duration: 500, easing: 'easeOutQuad' });
                } else {
                    btnTopo.style.opacity = '1';
                }
            } else {
                if (window.anime) {
                    anime({
                        targets: btnTopo, opacity: [1, 0], translateY: [0, 20], duration: 500,
                        easing: 'easeOutQuad', complete: function () { btnTopo.style.display = 'none'; }
                    });
                } else {
                    btnTopo.style.opacity = '0';
                    btnTopo.style.display = 'none';
                }
            }
        });

        btnTopo.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

// =============================================
// 7. POP-UP PRODUTO (função global)
// =============================================
function showProductInfo(nomeProduto) {
    if (!window.Swal) {
        alert(nomeProduto + '\n\nVocê será redirecionado para a página de compra.\nAo comprar, você apoia nosso projeto!');
        return;
    }
    Swal.fire({
        title: nomeProduto,
        html: 'Você será redirecionado para a página de compra.<br>Ao comprar, você apoia nosso projeto! 💜',
        icon: 'info',
        confirmButtonText: 'Entendi',
        didOpen: function (popup) {
            if (window.anime) {
                anime({ targets: popup, scale: [0.5, 1], opacity: [0, 1], duration: 800, easing: 'easeOutElastic(1, .8)' });
            }
        }
    });
}
