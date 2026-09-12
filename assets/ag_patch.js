(function() {
    try {
        localStorage.setItem('theme', 'light');
        if (document.documentElement) {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
            document.documentElement.style.colorScheme = 'light';
        }
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
