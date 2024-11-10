document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-div');

    flashMessages.forEach(flashMessage => {
        const progressBar = flashMessage.querySelector('.progress-bar');

        // Animate the progress bar to fill over 5 seconds
        progressBar.style.width = '100%';

        // Set a timeout to fade out and remove the flash message after 5 seconds
        setTimeout(function() {
            flashMessage.style.transition = 'opacity 0.5s ease';
            flashMessage.style.opacity = '0'; // Fade out
            setTimeout(() => flashMessage.style.display = 'none', 500); // Hide after fade-out
        }, 5000);

        // Close button event listener
        flashMessage.querySelector('.close-btn').addEventListener('click', function() {
            flashMessage.style.transition = 'opacity 0.5s ease';
            flashMessage.style.opacity = '0';
            setTimeout(() => flashMessage.style.display = 'none', 500);
        });
    });
});
