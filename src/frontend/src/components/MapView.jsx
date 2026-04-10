import { useEffect, useRef } from "react";
import { loadMappls } from "../utils/mapplsLoader";

export default function MapView({ center, places, selected, route }) {
  const mapRef = useRef(null);
  const markers = useRef([]);

  useEffect(() => {
    loadMappls().then((mappls) => {
      mapRef.current = new mappls.Map("map", {
        center: [center.lng, center.lat],
        zoom: 12
      });
    });
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    markers.current.forEach((m) => m.remove?.());
    markers.current = [];

    places.forEach((p) => {
      const marker = new window.mappls.Marker({
        map: mapRef.current,
        position: [p.lng, p.lat]
      });

      markers.current.push(marker);
    });
  }, [places]);

  useEffect(() => {
    if (!selected || !mapRef.current) return;

    mapRef.current.setCenter([selected.lng, selected.lat]);
    mapRef.current.setZoom(16);
  }, [selected]);

  return <div id="map" style={{ height: "100%" }} />;
}