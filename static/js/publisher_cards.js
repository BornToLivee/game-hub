// This JavaScript may not be necessary since we are using anchor tags now
document.addEventListener("DOMContentLoaded", function() {
    const cards = document.querySelectorAll(".publisher-card");

    cards.forEach(card => {
        card.addEventListener("click", function() {
            window.location.href = this.closest(".card-link").href;
        });
    });
});
