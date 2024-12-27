// Initialize GSAP ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

// Utility function for stagger animations
const staggerElements = (selector, options = {}) => {
    const defaults = {
        y: 30,
        duration: 0.8,
        opacity: 0,
        ease: 'power3.out',
        stagger: 0.2,
        scrollTrigger: {
            trigger: selector,
            start: 'top center+=100',
            toggleActions: 'play none none reverse'
        },
        ...options
    };
    return gsap.from(selector, defaults);
};

// Hero section animations
const heroTimeline = gsap.timeline({ defaults: { ease: 'power3.out' } });

heroTimeline
    .from('.hero h1 span', {
        y: 50,
        opacity: 0,
        duration: 1,
        stagger: 0.2
    })
    .from('.hero p', {
        y: 30,
        opacity: 0,
        duration: 0.8
    }, '-=0.5')
    .from('.hero .btn-primary', {
        y: 20,
        opacity: 0,
        duration: 0.6
    }, '-=0.3')
    .from('.hero pre', {
        y: 20,
        opacity: 0,
        duration: 0.6,
        scale: 0.95
    }, '-=0.3');

// Navbar scroll effect
const navbar = document.querySelector('nav');
ScrollTrigger.create({
    start: 'top -80',
    end: 99999,
    toggleClass: {
        className: 'backdrop-blur-lg shadow-lg',
        targets: navbar
    }
});

// Features section animations
const featureCards = document.querySelectorAll('.feature-card');
featureCards.forEach((card, index) => {
    gsap.from(card, {
        scrollTrigger: {
            trigger: card,
            start: 'top center+=100',
            toggleActions: 'play none none reverse'
        },
        y: 50,
        opacity: 0,
        duration: 0.8,
        delay: index * 0.2
    });
});

// Documentation section animations
const docTimeline = gsap.timeline({
    scrollTrigger: {
        trigger: '#documentation',
        start: 'top center',
        toggleActions: 'play none none reverse'
    }
});

docTimeline
    .from('.doc-sidebar', {
        x: -30,
        opacity: 0,
        duration: 0.8
    })
    .from('.doc-content', {
        x: 30,
        opacity: 0,
        duration: 0.8
    }, '-=0.6');

// Code block animations
document.querySelectorAll('pre code').forEach((block) => {
    gsap.from(block, {
        scrollTrigger: {
            trigger: block,
            start: 'top center+=100',
            toggleActions: 'play none none reverse'
        },
        opacity: 0,
        y: 20,
        duration: 0.6,
        ease: 'power2.out'
    });
});

// Smooth scroll animation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            gsap.to(window, {
                duration: 1,
                scrollTo: {
                    y: target,
                    offsetY: 80
                },
                ease: 'power3.inOut'
            });
        }
    });
});

// Dark mode toggle animation
const darkModeToggle = document.querySelector('[x-data]');
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        gsap.to('body', {
            backgroundColor: document.documentElement.classList.contains('dark') ? '#111827' : '#f9fafb',
            color: document.documentElement.classList.contains('dark') ? '#f3f4f6' : '#111827',
            duration: 0.3
        });
    });
}

// Initialize Prism.js
Prism.highlightAll();
