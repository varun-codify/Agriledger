(function() {
    // Scroll-reveal for landing sections: elements with .reveal-on-scroll
    // fade/slide in once when they enter the viewport.
    function init() {
        var els = document.querySelectorAll('.reveal-on-scroll:not(.is-visible)');
        if (!('IntersectionObserver' in window)) {
            els.forEach(function(el) { el.classList.add('is-visible'); });
            return;
        }
        var io = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        els.forEach(function(el) { io.observe(el); });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    // Re-scan shortly after load in case Reflex hydrates late.
    window.addEventListener('load', function() { setTimeout(init, 100); });
})();
