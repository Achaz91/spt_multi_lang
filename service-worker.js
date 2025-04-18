const CACHE_NAME = 'spt-calculator-cache-v1';
const urlsToCache = [
  '.',
  'manifest.json',
  'icon-192x192.png',
  'icon-512x512.png',
  // Ajoutez ici d'autres ressources statiques si nécessaire (CSS, JS spécifiques)
];

self.addEventListener('install', function(event) {
  // Perform install steps
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request).then(
          function(res) {
            // Check if we received a valid response
            if(!res || res.status !== 200 || res.type !== 'basic') {
              return res;
            }

            // IMPORTANT: Clone the response. A response is a stream
            // and because we want the response to be consumed by the cache
            // and the app, we need to clone it.
            var responseToCache = res.clone();

            caches.open(CACHE_NAME)
              .then(function(cache) {
                cache.put(event.request, responseToCache);
              });

            // Return the original response
            return res;
          }
        );
      })
    );
});

self.addEventListener('activate', function(event) {
  var cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
