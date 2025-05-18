// Amazon Clone JavaScript (static/js/main.js)

document.addEventListener('DOMContentLoaded', function () {
    // Simulating cart functionality 
    const addToCartButtons = document.querySelectorAll('.box-content p');
    const cartCount = document.querySelector('.cart-count');
    let count = 0;

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            count++;
            cartCount.textContent = count;

            // Animation effect for cart count
            cartCount.style.transform = 'scale(1.3)';
            setTimeout(() => {
                cartCount.style.transform = 'scale(1)';
            }, 300);
        });
    });

    // Mobile menu toggle functionality
    const mobileMenu = document.querySelector('.mobile-menu');
    mobileMenu.addEventListener('click', function () {
        alert('Mobile menu clicked! Add your mobile menu implementation here.');
    });

    // Smooth scroll for "Back to Top"
    document.querySelector('.footer-panel1').addEventListener('click', function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});