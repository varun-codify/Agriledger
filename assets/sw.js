/* AgriLedger service worker.
 *
 * Kept intentionally minimal: it exists so the app qualifies as installable,
 * but does not intercept or cache any requests. The browser keeps using its
 * default network behavior, so nothing can break or serve stale content.
 * Offline support can be layered on later with a proper precache strategy.
 */
const VERSION = "1.0.0";

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", () => {
  // Intentionally empty — pass-through. Let the network handle everything.
});
