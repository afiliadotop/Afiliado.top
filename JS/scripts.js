document.addEventListener('DOMContentLoaded', () => {
    console.log('Afiliado.Top - Site carregado com sucesso!');

    // --- Lógica Unificada do Botão "Voltar ao Topo" ---
    const btnTopo = document.getElementById('btn-topo'); // Busca o botão pelo ID

    if (btnTopo) { // Garante que o botão existe no HTML
        // Mostra/Esconde o botão ao rolar a página
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) { // Mostra após rolar 300px
                if (btnTopo.style.display === 'none' || btnTopo.style.display === '') {
                    btnTopo.style.display = 'block';
                    // Adicionar animação de entrada com Anime.js se quiser
                    anime({
                        targets: btnTopo,
                        opacity: [0,1],
                        translateY: [20,0],
                        duration: 500,
                        easing: 'easeOutQuad'
                    });
                }
            } else {
                if (btnTopo.style.display === 'block') {
                    anime({
                        targets: btnTopo,
                        opacity: [1,0],
                        translateY: [0,20],
                        duration: 500,
                        easing: 'easeOutQuad',
                        complete: () => {
                            btnTopo.style.display = 'none';
                        }
                    });
                }
            }
        });

        // Comportamento de clique para voltar ao topo
        btnTopo.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    } else {
        console.warn("Botão 'Voltar ao Topo' (#btn-topo) não encontrado no HTML.");
    }
});

// A função showProductInfo (usada para pop-ups de produtos)
// pode ficar aqui se for usada globalmente, ou ser movida para shopee.html se for específica de lá.
// Se usada em ambos, considere um arquivo 'utils.js' e importá-lo.
function showProductInfo(nomeProduto) {
    Swal.fire({
        title: nomeProduto,
        html: 'Você será redirecionado para a página de compra.<br>Ao comprar, você apoia nosso projeto!',
        icon: 'info',
        confirmButtonText: 'Entendi',
        didOpen: (popup) => {
            anime({
                targets: popup,
                scale: [0.5, 1],
                opacity: [0, 1],
                duration: 800,
                easing: 'easeOutElastic(1, .8)'
            });
        }
    });
}
