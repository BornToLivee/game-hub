document.addEventListener("DOMContentLoaded", function() {
  const userRating = document.getElementById("user-rating");
  const stars = userRating.querySelectorAll("i");
  const ratingScore = document.getElementById("rating-score");
  const userScore = parseInt(userRating.getAttribute("data-score")) || 0;

  function updateStars(rating) {
    stars.forEach((star, index) => {
      if (index < rating) {
        star.classList.remove("far");
        star.classList.add("fas");
      } else {
        star.classList.remove("fas");
        star.classList.add("far");
      }
    });
  }

  updateStars(userScore);

  stars.forEach((star) => {
    star.addEventListener("click", function() {
      const rating = parseInt(this.getAttribute("data-value"));
      ratingScore.value = rating;
      updateStars(rating);
    });
  });
});
