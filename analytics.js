// Google Analytics 4
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-QPJC7X9N5H');

// Tracking de cliques em produtos
document.addEventListener('DOMContentLoaded', () => {
    const productLinks = document.querySelectorAll('a[href*="shopee"], a[href*="aliexpress"]');
    
    productLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const productName = link.getAttribute('onclick')?.match(/'([^']+)'/)?.[1] || 'Produto desconhecido';
            
            gtag('event', 'product_click', {
                'event_category': 'Affiliate',
                'event_label': productName,
                'value': 1
            });
        });
    });
});
