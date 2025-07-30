import React, { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import SearchBox from "./SearchBox";
import { getGeocode, getLatLng } from "use-places-autocomplete";
import LocationPopup from "./LocationPopup";
import LandingPage from "./loading_page";
import "./MapPage.css";
import "mapbox-gl/dist/mapbox-gl.css";

//Rendering 3D map using mapbox
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

const MapPage = () => {
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const mapInstance = useRef(null);
  const requestIdRef = useRef(0);

  const [searchHistory, setSearchHistory] = useState(() => {
    const saved = localStorage.getItem("searchHistory");
    return saved ? JSON.parse(saved) : [];
  });

  const [userLocation, setUserLocation] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [popupLoading, setPopupLoading] = useState(false);
  const [showLanding, setShowLanding] = useState(true);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setUserLocation({ lat: latitude, lng: longitude });
      },
      () => console.warn("Location access denied")
    );
  }, []);

  useEffect(() => {
    if (showLanding) return;

    const map = new mapboxgl.Map({
      container: mapRef.current,
      style: "mapbox://styles/mapbox/streets-v12",
      center: [-118.2437, 34.0522],
      zoom: 12,
      pitch: 60,
      bearing: -17.6,
      antialias: true,
    });

    mapInstance.current = map;

    map.on("load", () => {
      const layers = map.getStyle().layers;
      const labelLayerId = layers.find(
        (l) => l.type === "symbol" && l.layout["text-field"]
      )?.id;

      map.addLayer(
        {
          id: "3d-buildings",
          source: "composite",
          "source-layer": "building",
          filter: ["==", "extrude", "true"],
          type: "fill-extrusion",
          minzoom: 15,
          paint: {
            "fill-extrusion-color": "#aaa",
            "fill-extrusion-height": ["get", "height"],
            "fill-extrusion-base": ["get", "min_height"],
            "fill-extrusion-opacity": 0.6,
          },
        },
        labelLayerId
      );
    });

    return () => map.remove();
  }, [showLanding]);

  const handleSelect = async (address) => {
    const currentRequestId = ++requestIdRef.current;
    try {
      setPopupLoading(true);
      setSelectedPlace({
        name: address,
        score: null,
        reason: "",
        lat: null,
        lng: null,
      });

      const results = await getGeocode({ address });
      const { lat, lng } = await getLatLng(results[0]);

      if (mapInstance.current) {
        mapInstance.current.flyTo({ center: [lng, lat], zoom: 15 });

        if (markerRef.current) markerRef.current.remove();
        markerRef.current = new mapboxgl.Marker({ color: "red" })
          .setLngLat([lng, lat])
          .addTo(mapInstance.current);
      }

      const detail = results[0].formatted_address.split(", ").slice(-2).join(", ");
      const updated = [
        { label: address, detail },
        ...searchHistory.filter((item) => item.label !== address),
      ].slice(0, 5);
      setSearchHistory(updated);
      localStorage.setItem("searchHistory", JSON.stringify(updated));

      mapInstance.current.once("moveend", async () => {
        const res = await fetch(
          `https://noisemap-ai.onrender.com/noise?lat=${lat}&lng=${lng}&location=${encodeURIComponent(address)}`
        );
        const data = await res.json();

        if (requestIdRef.current === currentRequestId) {
          setSelectedPlace({
            name: data.location || address,
            score: data.score != null ? parseFloat(data.score.toFixed(1)) : 0.0,
            reason: data.reason || "Unknown",
            lat,
            lng,
          });
        }
        setPopupLoading(false);
      });
    } catch (err) {
      console.error("handleSelect error:", err);
      setPopupLoading(false);
    }
  };


  if (showLanding) {
    return <LandingPage onSearchClick={() => setShowLanding(false)} />;
  }

  return (
    <div className="map-container">
      <SearchBox
        onSelect={handleSelect}
        history={searchHistory}
        setHistory={setSearchHistory}
        userLocation={userLocation}
      />
      <div ref={mapRef} className="mapbox-map" />
      {selectedPlace && (
        <LocationPopup
          key={`${selectedPlace.lat}-${selectedPlace.lng}`}
          name={selectedPlace.name}
          score={selectedPlace.score}
          reason={selectedPlace.reason}
          lat={selectedPlace.lat}
          lng={selectedPlace.lng}
          loading={popupLoading}
          onClose={() => setSelectedPlace(null)}
        />
      )}
    </div>
  );
};

export default MapPage;
