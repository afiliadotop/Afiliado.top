// Afiliado.Top - scripts globais

document.addEventListener('DOMContentLoaded', () => {
    console.log('Afiliado.Top - Site carregado com sucesso!');

    // --- Torna as imagens dos produtos clicáveis (redirecionam para a Shopee) ---
    document.querySelectorAll('#productsGrid > div').forEach(card => {
        const buyLink = card.querySelector('a[href]');
        const imgWrapper = card.querySelector('.relative');

        if (buyLink && imgWrapper) {
            const href = buyLink.getAttribute('href');
            const productName = (card.querySelector('img') || {}).alt || '';

            // Overlay transparente sobre toda a área da imagem (cobre também os badges)
            const overlay = document.createElement('a');
            overlay.href = href;
            overlay.target = '_blank';
            overlay.rel = 'noopener noreferrer sponsored';
            overlay.title = productName;
            overlay.setAttribute('aria-label', 'Ver ' + productName + ' na Shopee');
            overlay.style.cssText = 'position:absolute;inset:0;z-index:10;display:block;cursor:pointer;';

            imgWrapper.style.position = 'relative';
            imgWrapper.appendChild(overlay);
        }
    });

    // --- Botão "Voltar ao Topo" ---
    const btnTopo = document.getElementById('btn-topo');

    if (btnTopo) {
        // Mostrar / esconder botão conforme o scroll
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                if (btnTopo.style.display === 'none' || btnTopo.style.display === '') {
                    btnTopo.style.display = 'block';

                    // Animação de entrada com Anime.js (se carregado)
                    if (window.anime) {
                        anime({
                            targets: btnTopo,
                            opacity: [0, 1],
                            translateY: [20, 0],
                            duration: 500,
                            easing: 'easeOutQuad'
                        });
                    } else {
                        btnTopo.style.opacity = '1';
                    }
                }
            } else {
                if (btnTopo.style.display === 'block') {
                    if (window.anime) {
                        anime({
                            targets: btnTopo,
                            opacity: [1, 0],
                            translateY: [0, 20],
                            duration: 500,
                            easing: 'easeOutQuad',
                            complete: () => {
                                btnTopo.style.display = 'none';
                            }
                        });
                    } else {
                        btnTopo.style.opacity = '0';
                        btnTopo.style.display = 'none';
                    }
                }
            }
        });

        // Clique para voltar ao topo
        btnTopo.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    } else {
        console.warn("Botão 'Voltar ao Topo' (#btn-topo) não encontrado no HTML.");
    }
});

/**
 * Exibe um pop-up com informações do produto.
 * Pode ser usada em qualquer página (Shopee, Amazon, etc.).
 * Depende de SweetAlert2 (Swal) e, opcionalmente, de Anime.js.
 */
function showProductInfo(nomeProduto) {
    if (!window.Swal) {
        alert(nomeProduto + "\n\nVocê será redirecionado para a página de compra.\nAo comprar, você apoia nosso projeto!");
        return;
    }

    Swal.fire({
        title: nomeProduto,
        html: 'Você será redirecionado para a página de compra.<br>Ao comprar, você apoia nosso projeto! 💜',
        icon: 'info',
        confirmButtonText: 'Entendi',
        didOpen: (popup) => {
            if (window.anime) {
                anime({
                    targets: popup,
                    scale: [0.5, 1],
                    opacity: [0, 1],
                    duration: 800,
                    easing: 'easeOutElastic(1, .8)'
                });
            }
        }
    });
}
