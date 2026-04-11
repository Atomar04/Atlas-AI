import { useEffect, useRef } from "react";
import { loadMappls } from "../utils/mapplsLoader";

export default function MapView({ center, places, selected, zoom = 13, onSelect }) {
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const initializedRef = useRef(false);

  useEffect(() => {
    let mounted = true;

    async function initMap() {
      const mappls = await loadMappls();
      if (!mounted || initializedRef.current) return;

      const CLOCK_TOWER = { lat: 28.3639, lng: 75.5873 };

      const safeCenter = center?.lat && center?.lng
        ? [center.lng, center.lat]
        : [CLOCK_TOWER.lng, CLOCK_TOWER.lat];

      mapInstanceRef.current = new mappls.Map("map", {
        center: safeCenter,
        zoom
      });

      // Add default marker ONLY if no center provided
      if (!center?.lat || !center?.lng) {
        new mappls.Marker({
          map: mapInstanceRef.current,
          position: [CLOCK_TOWER.lng, CLOCK_TOWER.lat],
          popupHtml: "<b>Clock Tower, BITS Pilani</b>",
        });
      }

      initializedRef.current = true;
    }

    initMap().catch((err) => {
      console.error("Map initialization failed:", err);
    });

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !center?.lat || !center?.lng) return;

    map.setCenter([center.lng, center.lat]);
    map.setZoom(zoom || 13);
  }, [center, zoom]);

  useEffect(() => {
    const map = mapInstanceRef.current;
    
    if (!map || !Array.isArray(places)) return;

    markersRef.current.forEach((marker) => marker.remove?.());
    markersRef.current = [];

    places.forEach((place) => {
      if (typeof place.lat !== "number" || typeof place.lng !== "number") return;

      const marker = new window.mappls.Marker({
        map,
        position: [place.lng, place.lat],
        fitbounds: false,
        popupHtml: `
          <div style="min-width:180px;">
            <div style="font-weight:700; margin-bottom:4px;">${place.rank}. ${place.name}</div>
            <div style="font-size:12px; color:#4b5563;">${place.address || "Address unavailable"}</div>
            <div style="margin-top:6px; font-size:12px;">
              ⭐ ${place.rating ?? "N/A"} • ${place.distance_km ?? "N/A"} km
            </div>
          </div>
        `
      });

      if (typeof marker.on === "function") {
        marker.on("click", () => onSelect?.(place));
      }

      markersRef.current.push(marker);
    });
  }, [places, onSelect]);

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !selected?.lat || !selected?.lng) return;

    map.setCenter([selected.lng, selected.lat]);
    map.setZoom(16);
  }, [selected]);

  return (
    <div className="map-shell">
      <div className="map-topbar">
        <div>
          <div className="map-title">Live Map</div>
          <div className="map-subtitle">Pins update as the conversation evolves</div>
        </div>

        {selected ? (
          <div className="selected-pill">
            Selected: {selected.rank}. {selected.name}
          </div>
        ) : (
          <div className="selected-pill muted">No place selected</div>
        )}
      </div>

      <div id="map" />
    </div>
  );
}