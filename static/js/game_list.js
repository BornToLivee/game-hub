document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", function () {
        const url = this.querySelector("a").getAttribute("href");
        window.location.href = url;
    });
});

document.querySelectorAll(".card-img-top").forEach(image => {
    image.addEventListener("mouseenter", function () {
        this.style.transform = "scale(1.1)";
        this.style.transition = "transform 0.3s";
    });

    image.addEventListener("mouseleave", function () {
        this.style.transform = "scale(1)";
        this.style.transition = "transform 0.3s";
    });
});
