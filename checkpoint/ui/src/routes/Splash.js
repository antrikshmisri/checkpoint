import React from "react";
import { useHistory } from "react-router-dom";
import { Container, Row, Col } from "react-bootstrap";
import Button from "../components/button";
import GradientText from "../components/gradientText";
import "bootstrap/dist/css/bootstrap.min.css";

const Splash = () => {
  const history = useHistory();

  const nextPage = () => {
    let page = "/home";
    history.push(page);
  };

  return (
    <Container className="splash-div">
      <Row>
        <Col lg={12}>
          <h1 className="text-center heading mb-3">
            <GradientText startColor="#03A9F1" endColor="#007BB0" style={{"textDecoration": "underline"}}>
              Checkpoint
            </GradientText>
          </h1>
        </Col>
        <Col lg={12}>
            <h2 className="text-center heading">
                Create Restore Points in a Single Click
            </h2>
        </Col>
      </Row>
      <Row>
        <Col lg={12} className="btn-div">
          <Button
            width={100}
            height={40}
            text={<GradientText startColor="#f18303" endColor="#f94409">Start</GradientText>}
            onClick={nextPage}
          />
        </Col>
      </Row>
    </Container>
  );
};

export default Splash;
