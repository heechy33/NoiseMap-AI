import ReactSpeedometer from "react-d3-speedometer";

const ScoreMeter = ({
  value = 0,
  width = 350,
  height = 200,
  fontFamily = "'Poppins', sans-serif"
}) => {
  return (
    <div style={{ fontFamily, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <ReactSpeedometer
        maxValue={10}
        value={value}
        segments={10}
        needleColor="black"
        startColor="green"
        endColor="red"
        textColor="#111"
        currentValueText=""
        ringWidth={25}
        width={width}
        height={height}
        needleHeightRatio={0.6}
        valueTextFontSize="0"
        labelFontSize="12px"
      />
      <div
        style={{
          fontSize: '50px',
          fontWeight: 700,
          fontFamily: "'Poppins', sans-serif",
          marginTop: '-12px'
        }}
      >
        {value.toFixed(1)}
      </div>
    </div>
  );
};

export default ScoreMeter;
