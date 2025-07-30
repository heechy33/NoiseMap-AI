import "./loading_page.css";

//The intro page (text with buttons)
const LandingPage = ({ onSearchClick }) => {
  return (
    <div className="landing-overlay">
      <div className="landing-content">
        <h1>NoiseMap AI</h1>
        <p>Explore and visualize urban noise around the globe.</p>
        <button className="start-button" onClick={onSearchClick}>
          Enter the map
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
