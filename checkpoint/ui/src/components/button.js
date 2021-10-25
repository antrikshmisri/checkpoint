import React from "react";

const Button = (props) => {
  return (
    <button
      style={{ minWidth: props.width, minHeight: props.height }}
      onClick={props.onClick}
    >
      <p className="gradient-text">{props.text}</p>
    </button>
  );
};

export default Button;
