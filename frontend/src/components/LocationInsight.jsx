import { useEffect, useState } from "react";
import "./LocationInsight.css";
import Loader from "./Loader";


//Location Insight tab
const LocationInsight = ({ lat, lng }) => {
  const [summary, setSummary] = useState("");
  const [factors, setFactors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const key = `${lat.toFixed(4)}_${lng.toFixed(4)}`;
    fetch(`http://localhost:8000/location_insight?lat=${lat}&lng=${lng}`)
    .then((res) => res.json())
    .then((data) => {
        setSummary(data.summary);
        setFactors(data.factors || []);
        sessionStorage.setItem(key, JSON.stringify(data));
    })

    fetch(`https://noisemap-ai.onrender.com/location_insight?lat=${lat}&lng=${lng}`)
      .then((res) => res.json())
      .then((data) => {
        const parsed = {
          summary: data.summary || "No insights available for this area.",
          factors: data.factors || [],
        };
        setSummary(parsed.summary);
        setFactors(parsed.factors);
        sessionStorage.setItem(key, JSON.stringify(parsed));
      })
      .catch(() => {
        setSummary("Failed to load insight.");
        setFactors([]);
      })
      .finally(() => setLoading(false));
  }, [lat, lng]);

  if (loading) return <Loader />;

  return (
    <div className="location-insight">
      <h4>🗺️ Location Overview</h4>
      <p style={{ marginBottom: "1rem" }}>{summary}</p>

      {factors.length > 0 && (
        <>
          <h4>🔊 Likely Noise Sources</h4>
          <ul className="noise-factors">
            {factors.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};

export default LocationInsight;
