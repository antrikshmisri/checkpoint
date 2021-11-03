import React, { useRef } from "react";
import { useHistory } from "react-router-dom";
import { Container, Row, Col } from "react-bootstrap";
import Button from "../components/button";
import GradientText from "../components/gradientText";
import "bootstrap/dist/css/bootstrap.min.css";
import marker from "../assets/marker.png";

const Splash = () => {
  const fillRef = useRef(null);
  const history = useHistory();

  const nextPage = () => {
    let page = "/home";
    history.push(page);
  };

  const handleCheckpointClick = (image_idx) => {
    let progress_map = {
      0: "0%",
      1: "35%",
      2: "65%",
      3: "100%",
    };
    fillRef.current.style.width = progress_map[image_idx];
  };

  return (
    <Container className="splash-div">
      <Row>
        <Col lg={12}>
          <h1 className="text-center heading mb-3">
            <GradientText
              startColor="#03A9F1"
              endColor="#007BB0"
              style={{ textDecoration: "underline" }}
            >
              Checkpoint
            </GradientText>
          </h1>
        </Col>
        <Col lg={12}>
          <h2 className="text-center heading">
            Create Restore Points in a Single Click
          </h2>
        </Col>
        <Col lg={12} className="text-center mt-5">
          <div className="checkpoint-img-div">
            {[...Array(4)].map((value, idx) => {
              return (
                <img
                  src={marker}
                  id={idx}
                  onClick={() => {
                    handleCheckpointClick(idx);
                  }}
                  className="marker"
                  alt="marker"
                />
              );
            })}
          </div>
          <div className="checkpoints">
            <div className="fill-bar" ref={fillRef}></div>
          </div>
        </Col>
      </Row>
      <Row>
        <Col lg={12} className="btn-div">
          <Button
            width={100}
            height={40}
            text={
              <GradientText startColor="#f18303" endColor="#f94409">
                Start
              </GradientText>
            }
            onClick={nextPage}
          />
        </Col>
      </Row>
    </Container>
  );
};

export default Splash;
