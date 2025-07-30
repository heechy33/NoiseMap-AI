import "./Loader.css";

//3 loading dots
const Loader = ({ height = 160 }) => (
  <div className="loader-card" style={{ minHeight: height }}>
    <div className="dot-loader">
      <div className="dot bounce1" />
      <div className="dot bounce2" />
      <div className="dot bounce3" />
    </div>
  </div>
);

export default Loader;
