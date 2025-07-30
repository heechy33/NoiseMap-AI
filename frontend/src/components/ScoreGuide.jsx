import "./LocationPopup.css";
import { Icon } from "@iconify/react";

const data = [
  { range: "0.0 - 1.9", label: "Very Quiet", db: "0-30 dB", icon: "twemoji:leaf-fluttering-in-wind", color: "#2ecc71" },
  { range: "2.0 - 3.9", label: "Quiet", db: "31-45 dB", icon: "twemoji:bed", color: "#27ae60" },
  { range: "4.0 - 5.9", label: "Moderate", db: "46-60 dB", icon: "twemoji:speaking-head", color: "#f1c40f" },
  { range: "6.0 - 7.4", label: "Loud", db: "61-75 dB", icon: "twemoji:automobile", color: "#e67e22" },
  { range: "7.5 - 8.9", label: "Very Loud", db: "76-90 dB", icon: "twemoji:airplane", color: "#e74c3c" },
  { range: "9.0 - 10.0", label: "Extremely Loud", db: "91-110 dB", icon: "twemoji:loudspeaker", color: "#c0392b" },
];

const ScoreGuide = () => {
  return (
    <div className="score-details fade-in" style={{ padding: '0 10px' }}>
      <table className="score-guide-table" style={{ width: '100%', fontFamily: 'Kanit, sans-serif', fontSize: '14px', borderCollapse: 'collapse', marginTop: '16px' }}>
        <thead>
          <tr style={{ backgroundColor: '#ffffffff' }}>
            <th style={{ padding: '10px', borderBottom: '1px solid #ddd', textAlign: 'left' }}>Score Range</th>
            <th style={{ padding: '10px', borderBottom: '1px solid #ddd', textAlign: 'left' }}>Category</th>
            <th style={{ padding: '10px', borderBottom: '1px solid #ddd', textAlign: 'left' }}>Approx. dB</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #eee', backgroundColor: row.color + '20' }}>
              <td style={{ padding: '10px' }}>{row.range}</td>
              <td style={{ padding: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Icon icon={row.icon} width={20} /> {row.label}
              </td>
              <td style={{ padding: '10px' }}>{row.db}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScoreGuide;