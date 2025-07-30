import React, { useEffect, useRef, useState } from "react";
import "./LocationPopup.css";
import ScoreMeter from "./ScoreMeter";
import { FaSearch, FaChartBar, FaMapMarkedAlt, FaTimes } from "react-icons/fa";
import ScoreGuide from "./ScoreGuide";
import ScoreAnalysis from "./ScoreAnalysis";
import LocationInsight from "./LocationInsight";
import Loader from "./Loader";

//core Location pop up page
const LocationPopup = ({ name, score, lat, lng, loading, onClose }) => {
  const popupRef = useRef(null);
  const [position, setPosition] = useState({ x: 40, y: 100 });
  const [dragging, setDragging] = useState(false);
  const [rel, setRel] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!dragging) return;
      setPosition({
        x: e.clientX - rel.x,
        y: e.clientY - rel.y,
      });
    };
    const handleMouseUp = () => setDragging(false);

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [dragging, rel]);

  const handleMouseDown = (e) => {
    if (e.target.closest(".popup-close")) return;
    const rect = popupRef.current.getBoundingClientRect();
    setDragging(true);
    setRel({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const [displayScore, setDisplayScore] = useState(0);
  const [activeTab, setActiveTab] = useState("guide");

  useEffect(() => {
    if (loading || score == null || isNaN(score)) return;
    let start = 0;
    const end = score;
    const duration = 1000;
    const stepTime = 30;
    const increment = (end - start) / (duration / stepTime);

    const interval = setInterval(() => {
      start += increment;
      if (start >= end) {
        start = end;
        clearInterval(interval);
      }
      setDisplayScore(parseFloat(start.toFixed(1)));
    }, stepTime);

    return () => clearInterval(interval);
  }, [score, loading]);

  return (
    <div
      ref={popupRef}
      className="location-popup"
      onMouseDown={handleMouseDown}
      style={{ position: "absolute", left: position.x, top: position.y }}
    >
      <button
        className="popup-close"
        onClick={onClose}
        style={{
          position: "absolute",
          top: 12,
          right: 14,
          background: "none",
          border: "none",
          fontSize: "18px",
          cursor: "pointer",
          color: "#333",
          zIndex: 10,
        }}
        aria-label="Close popup"
      >
        <FaTimes />
      </button>

      <h3 className="location-title">{name || "Loading..."}</h3>
      <div className="score-label">NOISEMAP SCORE</div>

      {loading ? (
        <div className="popup-loader-container">
          <Loader height={280} />
          <p className="popup-loading-text">Noise score calculating...</p>
        </div>
        
      ) : (
        <>
          {score == null ? (
            <div style={{ textAlign: "center", fontSize: "16px", fontWeight: 500, color: "#888", margin: "20px 0" }}>
              No noise score available for this location.
            </div>
          ) : (
            <>
              <ScoreMeter value={displayScore} />
              <p className="reason">
                {displayScore < 2
                  ? "Very Quiet"
                  : displayScore < 4
                  ? "Quiet"
                  : displayScore < 6
                  ? "Moderate"
                  : displayScore < 7.5
                  ? "Loud"
                  : displayScore < 9
                  ? "Very Loud"
                  : "Extremely Loud"}
              </p>
            </>
          )}


          <div className="tab-buttons pretty-tabs">
            <button
              className={
                activeTab === "guide" ? "pretty-tab active" : "pretty-tab"
              }
              onClick={() => setActiveTab("guide")}
            >
              <FaSearch style={{ marginRight: 6 }} /> Score Guide
            </button>
            <button
              className={
                activeTab === "analysis" ? "pretty-tab active" : "pretty-tab"
              }
              onClick={() => setActiveTab("analysis")}
            >
              <FaChartBar style={{ marginRight: 6 }} /> Score Analysis
            </button>
            <button
              className={
                activeTab === "insight" ? "pretty-tab active" : "pretty-tab"
              }
              onClick={() => setActiveTab("insight")}
            >
              <FaMapMarkedAlt style={{ marginRight: 6 }} /> Location Insight
            </button>
          </div>

          <div className="tab-content">
            {activeTab === "guide" && <ScoreGuide />}
            {activeTab === "analysis" && <ScoreAnalysis lat={lat} lng={lng} />}
            {activeTab === "insight" && (
              <LocationInsight lat={lat} lng={lng} location={name} />
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default LocationPopup;
