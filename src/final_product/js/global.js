// Global JavaScript for common functionalities
document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll for anchor links (if not using scroll-behavior: smooth in CSS)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add sticky class to header on scroll (if not using position: sticky in CSS)
    // For this design, position: sticky is used directly in CSS, so this JS might be redundant
    const header = document.querySelector('.main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 0) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // Example for a simple mobile navigation toggle if needed
    // (Not implemented in current HTML, assuming CSS handles basic responsiveness)
    const navToggle = document.querySelector('.nav-toggle'); // e.g., a hamburger icon
    const mainNav = document.querySelector('.main-nav');
    if (navToggle && mainNav) {
        navToggle.addEventListener('click', () => {
            mainNav.classList.toggle('nav-open');
            navToggle.classList.toggle('open');
        });
    }
});
