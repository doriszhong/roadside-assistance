/* MechanicGo PWA service worker: cache-first for static pages, network-first for API */
const CACHE = 'mechanicgo-v1';
const PRECACHE = ['/', '/dashboard', '/mechanic', '/admin', '/manifest.json', '/static/icon-192.png', '/static/icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/api/')) {
    // API: network only, never cache
    return;
  }
  // Static pages/assets: cache-first with network fallback
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((resp) => {
      if (resp.ok && e.request.method === 'GET') {
        const clone = resp.clone();
        caches.open(CACHE).then((c) => c.put(e.request, clone));
      }
      return resp;
    }).catch(() => caches.match('/')))
  );
});
