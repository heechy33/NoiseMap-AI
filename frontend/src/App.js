import GoogleMapsWrapper from "./components/GoogleMapsWrapper";
import MapPage from "./components/MapPage";
import './App.css';

function App() {
  return (
    <GoogleMapsWrapper>
      <MapPage />
    </GoogleMapsWrapper>
  );
}

export default App;
