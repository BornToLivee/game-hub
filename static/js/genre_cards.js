document.addEventListener("DOMContentLoaded", function () {
    const genreCards = document.querySelectorAll(".genre-card");
    genreCards.forEach(card => {
        card.addEventListener("click", function () {
            const url = card.dataset.url;
            window.location.href = url;
        });
    });
});