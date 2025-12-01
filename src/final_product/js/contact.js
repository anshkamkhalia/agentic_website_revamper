document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.querySelector('.contact-form');
    const successMessage = document.querySelector('.success-message');
    const errorMessage = document.querySelector('.error-message');

    if (contactForm) {
        contactForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent default form submission

            // Simulate form submission success/failure
            const isSuccess = Math.random() > 0.3; // 70% chance of success for demo

            if (isSuccess) {
                successMessage.style.display = 'block';
                errorMessage.style.display = 'none';
                contactForm.reset(); // Clear the form
            } else {
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
            }

            // Hide messages after a few seconds
            setTimeout(() => {
                successMessage.style.display = 'none';
                errorMessage.style.display = 'none';
            }, 5000);
        });
    }
});
