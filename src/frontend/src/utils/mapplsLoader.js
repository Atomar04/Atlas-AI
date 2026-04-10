let mapPromise = null;

export function loadMappls() {
  if (window.mappls) return Promise.resolve(window.mappls);

  if (mapPromise) return mapPromise;

  mapPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");

    script.src = `https://apis.mappls.com/advancedmaps/api/${import.meta.env.VITE_MAPPLS_API_KEY}/map_sdk?layer=vector&v=3.0`;

    script.onload = () => resolve(window.mappls);
    script.onerror = reject;

    document.body.appendChild(script);
  });

  return mapPromise;
}