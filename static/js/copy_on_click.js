document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('copyEmail').addEventListener('click', function(event) {
        event.preventDefault();
        const email = this.textContent;
        const el = document.createElement('textarea');
        el.value = email;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);

        const copyNotification = document.getElementById('copyNotification');
        const copiedEmail = document.getElementById('copiedEmail');
        const copyInfo = document.getElementById('copyInfo');

        copiedEmail.textContent = email;
        copyNotification.style.display = 'block';
        copyInfo.style.display = 'inline-block';

        setTimeout(function() {
            copyNotification.style.display = 'none';
            copyInfo.style.display = 'none';
        }, 3000);
    });
});
