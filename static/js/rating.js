document.addEventListener('DOMContentLoaded', function() {
  const userRating = document.getElementById('user-rating');
  const stars = userRating.querySelectorAll('i');
  const ratingScore = document.getElementById('rating-score');
  const userScore = parseInt(userRating.getAttribute('data-score')) || 0;

  stars.forEach((star, index) => {
    if (index < userScore) {
      star.classList.add('fas');
    } else {
      star.classList.add('far');
    }

    star.addEventListener('click', function() {
      const rating = parseInt(this.getAttribute('data-value'));
      ratingScore.value = rating;

      stars.forEach((s, i) => {
        if (i < rating) {
          s.classList.remove('far');
          s.classList.add('fas');
        } else {
          s.classList.remove('fas');
          s.classList.add('far');
        }
      });
    });
  });
});
