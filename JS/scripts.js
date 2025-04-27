// scripts.js
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const filter = this.dataset.filter;
    document.querySelectorAll('.offer-card').forEach(card => {
      card.style.display = (filter === 'all' || card.dataset.category === filter) 
        ? 'block' 
        : 'none';
    });
  });
});
