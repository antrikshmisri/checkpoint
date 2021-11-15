import React from "react";
import { Container, Row, Col } from "react-bootstrap";
import GradientText from "./gradientText";

const TextBox = ({
  value,
  placeholder,
  onChange,
  required,
  inputref,
  label,
  keyPressCallback = () => {},
  outlineColor="rgb(54, 57, 59, 0.7)",
}) => {
  return (
    <Container className="px-0 py-0">
      <Row>
        <Col lg={12}>
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline", fontWeight: "500" }}
          >
            {label}
          </GradientText>
        </Col>
        <Col lg={12}>
          <input
            type="text"
            ref={inputref}
            value={value}
            placeholder={placeholder}
            onChange={(e) => {onChange(e); keyPressCallback(e);}}
            required={required}
            style={{borderColor: outlineColor}}
          >
          </input>
        </Col>
      </Row>
    </Container>
  );
};

export default TextBox;
