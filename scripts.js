// Este script deve ser carregado APÓS o DOM estar pronto
// (se estiver no final do <body>, ou dentro de DOMContentLoaded)

document.addEventListener('DOMContentLoaded', () => {
    console.log('Site afiliado.top carregado com sucesso!');

    // --- Lógica Unificada do Botão "Voltar ao Topo" ---
    const btnTopo = document.getElementById('btn-topo'); // Busca o botão pelo ID

    if (btnTopo) { // Garante que o botão existe no HTML
        // Mostra/Esconde o botão ao rolar a página
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) { // Mostra após rolar 300px
                btnTopo.style.display = 'block';
                // Opcional: Adicionar animação de entrada com Anime.js ou Tailwind
                // anime({ targets: btnTopo, opacity: [0,1], translateY: [20,0], duration: 500 });
            } else {
                btnTopo.style.display = 'none';
                // Opcional: Adicionar animação de saída
            }
        });

        // Comportamento de clique para voltar ao topo
        btnTopo.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    } else {
        console.warn("Botão 'Voltar ao Topo' (#btn-topo) não encontrado no HTML.");
    }

    // --- Animações ao Rolar (se você estiver usando Intersection Observer para cards de produto) ---
    // A lógica de Intersection Observer deve ser mantida na página onde os produtos são carregados (ex: shopee.html)
    // Se você tiver cards animados também na index.html, mantenha o observador aqui e observe os elementos.

    // Exemplo de como você observaria elementos na index.html se eles existirem
    // const animatedElements = document.querySelectorAll('.animated-item'); // Se houver elementos com essa classe
    // const observer = new IntersectionObserver((entries) => { ... }, { threshold: 0.1 });
    // animatedElements.forEach(element => observer.observe(element));

    // --- (Removido: Lógica de scroll suave para Ofertas_Shopee.html - não é uma âncora) ---
    // Links para outras páginas funcionam com o 'href' padrão do HTML
});

// A função showProductInfo do SweetAlert2/Anime.js pode ficar aqui ou em um arquivo js separado
// Se você a usa tanto na index.html quanto na shopee.html, considere colocá-la em um arquivo 'utils.js'
// e importá-la em ambas as páginas.
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
