document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.fade-in-section');

    const fadeInOnScroll = () => {
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            const triggerPoint = window.innerHeight - 100; // Adjust this value as needed

            if (sectionTop < triggerPoint) {
                section.classList.add('fade-in');
            }
        });
    };

    window.addEventListener('scroll', fadeInOnScroll);
    fadeInOnScroll(); // trigger the function on page load
});

// const block1 = document.querySelector('.landing-block-1')
// const block2 = document.querySelector('.landing-block-2')
// const block3 = document.querySelector('.landing-block-3')

// document.addEventListener('DOMContentLoaded', function() {
//     if (document.body.scrollTop > 300) {
//         block1.classList.add('fadeIn')
//     }
//     else {
//         block1.classList.remove('fadeIn')
//     }
// })