let mapPromise = null;

export function loadMappls() {
  if (window.mappls) {
    return Promise.resolve(window.mappls);
  }

  if (mapPromise) {
    return mapPromise;
  }

  const apiKey = import.meta.env.VITE_MAPPLS_API_KEY;
  console.log("Mappls API Key:", apiKey);

  if (!apiKey || apiKey === "YOUR_MAPPLS_API_KEY") {
    return Promise.reject(
      new Error("Missing VITE_MAPPLS_API_KEY in frontend environment.")
    );
  }

  mapPromise = new Promise((resolve, reject) => {
    const existingScript = document.querySelector('script[data-mappls-sdk="true"]');

    if (existingScript) {
      console.log("Mappls script already present");

      if (window.mappls) {
        return resolve(window.mappls);
      }

      existingScript.addEventListener("load", () => resolve(window.mappls));
      existingScript.addEventListener("error", reject);
      return;
    }

    const script = document.createElement("script");
    script.dataset.mapplsSdk = "true";
    script.src = `https://apis.mappls.com/advancedmaps/api/${apiKey}/map_sdk?layer=vector&v=3.0`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      console.log("Mappls SDK loaded");
      resolve(window.mappls);
    };
    script.onerror = () => {
      console.error("Failed to load Mappls SDK:", script.src);
      reject(new Error("Failed to load Mappls SDK"));
    };

    document.body.appendChild(script);
  });

  return mapPromise;
}