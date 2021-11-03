import React from "react";

const TextBox = ({ value, placeholder, onChange, required, inputref }) => {
  return (
    <input
      type="text"
      ref={inputref}
      value={value}
      placeholder={placeholder}
      onChange={onChange}
      required={required}
    />
  );
};

export default TextBox;
