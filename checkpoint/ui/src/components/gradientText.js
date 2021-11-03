import React from "react";

const GradientText = ({ children, startColor, endColor, style, key }) => {
  const textStyle = {
    background: startColor,
    background: `-webkit-linear-gradient(to right, ${startColor} 0%, ${endColor} 100%)`,
    background: `-moz-linear-gradient(to right, ${startColor} 0%, ${endColor} 100%)`,
    background: `linear-gradient(to right, ${startColor} 0%, ${endColor} 100%)`,
    ...style,
  };
  return (
    <p className="gradient-text" style={textStyle} key={key}>
      {children}
    </p>
  );
};

export default GradientText;
