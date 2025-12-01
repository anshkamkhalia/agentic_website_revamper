document.addEventListener('DOMContentLoaded', () => {
    // Intersection Observer for scroll animations
    const animateElements = document.querySelectorAll('.animate-fade-in, .animate-slide-up');

    const observerOptions = {
        root: null, // viewport
        rootMargin: '0px',
        threshold: 0.1 // 10% of the item visible
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // Stop observing once animated
            }
        });
    }, observerOptions);

    animateElements.forEach(element => {
        observer.observe(element);
    });

    // CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        /* Fade In Animation */
        .animate-fade-in {
            opacity: 0;
            transition: opacity 1s ease-out;
        }
        .animate-fade-in.is-visible {
            opacity: 1;
        }

        /* Slide Up Animation */
        .animate-slide-up {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.8s ease-out, transform 0.8s ease-out;
        }
        .animate-slide-up.is-visible {
            opacity: 1;
            transform: translateY(0);
        }

        /* Hamburger animation */
        .hamburger {
            display: flex; /* Override hidden on mobile view */
        }
        .hamburger.open span:nth-child(1) {
            transform: translateY(11px) rotate(45deg);
        }
        .hamburger.open span:nth-child(2) {
            opacity: 0;
        }
        .hamburger.open span:nth-child(3) {
            transform: translateY(-11px) rotate(-45deg);
        }
    `;
    document.head.appendChild(style);

    // Testimonial Carousel functionality (for Home page)
    const testimonialCarousel = document.querySelector('.testimonial-carousel');
    if (testimonialCarousel) {
        let scrollInterval;

        const startScrolling = () => {
            scrollInterval = setInterval(() => {
                if (testimonialCarousel.scrollWidth - testimonialCarousel.scrollLeft === testimonialCarousel.clientWidth) {
                    testimonialCarousel.scrollTo({ left: 0, behavior: 'smooth' });
                } else {
                    testimonialCarousel.scrollBy({ left: testimonialCarousel.clientWidth / 3, behavior: 'smooth' });
                }
            }, 3000); // Scrolls every 3 seconds
        };

        const stopScrolling = () => {
            clearInterval(scrollInterval);
        };

        testimonialCarousel.addEventListener('mouseenter', stopScrolling);
        testimonialCarousel.addEventListener('mouseleave', startScrolling);
        testimonialCarousel.addEventListener('touchstart', stopScrolling);
        testimonialCarousel.addEventListener('touchend', startScrolling);

        startScrolling(); // Start auto-scrolling on load
    }
});
