import React, { useEffect, useState } from "react";
import Loader from "./Loader";


const DonutChart = ({ factors }) => {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const total = factors.reduce((acc, f) => acc + f.value, 0);
  let offset = 0;

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", margin: "20px 0" }}>
      <svg width="150" height="150" style={{ marginRight: "20px" }}>
        <circle
          cx="75"
          cy="75"
          r={radius}
          fill="none"
          stroke="#eee"
          strokeWidth="16"
        />
        {factors.map(({ value, color }, i) => {
          const arc = (value / total) * circumference;
          const dashOffset = circumference - offset;
          offset += arc;

          return (
            <circle
              key={i}
              cx="75"
              cy="75"
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth="16"
              strokeDasharray={`${arc} ${circumference - arc}`}
              strokeDashoffset={dashOffset}
              transform="rotate(-90 75 75)"
              style={{ transition: "stroke-dashoffset 0.4s ease" }}
            />
          );
        })}
        <text x="75" y="82" textAnchor="middle" fontSize="20" fontWeight="700">
          100%
        </text>
      </svg>
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {factors.map(({ label, color }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ width: 12, height: 12, backgroundColor: color, borderRadius: "50%" }}></span>
            <span style={{ fontSize: 14 }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ScoreAnalysis tabs
const ScoreAnalysis = ({ lat, lng }) => {
  const [scores, setScores] = useState(null);

  useEffect(() => {
    if (!lat || !lng) return;

    const fetchScores = async () => {
      try {
        const res = await fetch(`http://localhost:8000/score_analysis?lat=${lat}&lng=${lng}`);
        const data = await res.json();
        setScores({
          nightlife: data.nightlife || 0,
          airport: data.airport || 0,
          train: data.train || 0,
          bus: data.bus || 0,
        });
      } catch (err) {
        console.error("Fetch failed:", err);
        setScores({ nightlife: 0, airport: 0, train: 0, bus: 0 });
      }
    };

    fetchScores();
  }, [lat, lng]);

  if (!scores) return <Loader />;

  const rawFactors = [
    { label: "Airport Noise Score", value: scores.airport, color: "#36A2EB" },
    { label: "Nightlife Noise Score", value: scores.nightlife, color: "#e74c3c" },
    { label: "Train Noise Score", value: scores.train, color: "#FFCE56" },
    { label: "Bus Noise Score", value: scores.bus, color: "#66BB6A" },
  ];

  const total = rawFactors.reduce((sum, f) => sum + f.value, 0);
  const factors = rawFactors.map(f => ({
    ...f,
    percent: total === 0 ? 0 : Math.round((f.value / total) * 100),
  }));

  return (
    <div className="score-details fade-in" style={{ padding: "0 10px", width: "100%" }}>
      <DonutChart factors={factors} />
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {factors.map(({ label, percent, color }) => (
          <div key={label}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <span style={{ fontWeight: 600 }}>{label}</span>
              <span style={{ fontWeight: 600 }}>{percent}%</span>
            </div>
            <div style={{ background: "#eee", borderRadius: 10, overflow: "hidden", height: 18 }}>
              <div
                style={{
                  width: `${percent}%`,
                  backgroundColor: color,
                  height: "100%",
                  borderRadius: 10,
                  transition: "width 0.4s ease",
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ScoreAnalysis;
