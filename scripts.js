// Pequenas interações na página

document.addEventListener('DOMContentLoaded', () => {
    console.log('Site afiliado.top carregado com sucesso!');

    // Scroll suave para âncoras
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Botão de volta ao topo (opcional)
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '⬆️';
    backToTopBtn.id = 'backToTop';
    backToTopBtn.style.position = 'fixed';
    backToTopBtn.style.bottom = '20px';
    backToTopBtn.style.right = '20px';
    backToTopBtn.style.padding = '10px';
    backToTopBtn.style.display = 'none';
    backToTopBtn.style.borderRadius = '50%';
    backToTopBtn.style.backgroundColor = '#00c3ff';
    backToTopBtn.style.color = '#fff';
    backToTopBtn.style.border = 'none';
    backToTopBtn.style.cursor = 'pointer';
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
