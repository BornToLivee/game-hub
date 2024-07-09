// static/js/rating.js

$(document).ready(function(){
    var userScore = parseInt($('#user-rating').data('score'));
    $('#user-rating i').each(function(){
        var ratingValue = $(this).data('value');
        if(ratingValue <= userScore){
            $(this).removeClass('far').addClass('fas');
        }
    });

    $('#user-rating i').on('click', function(){
        var ratingValue = $(this).data('value');
        $('#rating-score').val(ratingValue);
        $('#user-rating i').each(function(){
            var starValue = $(this).data('value');
            if(starValue <= ratingValue){
                $(this).removeClass('far').addClass('fas');
            } else {
                $(this).removeClass('fas').addClass('far');
            }
        });
    });

    $('#rating-form').on('submit', function(e){
        e.preventDefault();
        var score = $('#rating-score').val();
        $.ajax({
            url: window.location.href,
            method: "POST",
            data: {
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val(),
                'score': score
            },
            success: function(response){
                alert('Rating submitted successfully!');
                location.reload();
            },
            error: function(response){
                alert('An error occurred. Please try again.');
            }
        });
    });
});
