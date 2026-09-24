(function() {
    // Restore the user's saved theme (default: light). Never force one.
    try {
        var stored = localStorage.getItem('theme') || 'light';
        var root = document.documentElement;
        root.classList.toggle('dark', stored === 'dark');
        root.classList.toggle('light', stored !== 'dark');
        root.style.colorScheme = stored;
    } catch(e) {}

    if (typeof window !== 'undefined' && window.ResizeObserver) {
        var _roProto = window.ResizeObserver.prototype;
        var _origObserve = _roProto.observe;
        _roProto.observe = function(target, options) {
            if (target && target instanceof Element) {
                return _origObserve.call(this, target, options);
            }
        };
        var _origUnobserve = _roProto.unobserve;
        _roProto.unobserve = function(target) {
            if (target && target instanceof Element) {
                return _origUnobserve.call(this, target);
            }
        };
    }
})();
