import React, { useState, useRef } from "react";
import { Container, Row, Col, FormSelect } from "react-bootstrap";
import GradientText from "../components/gradientText";
import TextBox from "../components/textbox";
import Button from "../components/button";
import { eel } from "../eel";
import "bootstrap/dist/css/bootstrap.min.css";

const Home = () => {
  const [path, setPath] = useState("");
  const [ignoreDirectories, setIgnoreDirectories] = useState(".git");
  const [checkpointName, setCheckpointName] = useState("");
  const [action, setAction] = useState("init");

  const [logarray, setLogarray] = useState([]);
  const [errorLogarray, setErrorLogarray] = useState([]);
  const [checkpointArray, setCheckpointArray] = useState([]);

  const pathRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLogarray([]);
    setErrorLogarray([]);
    eel.run_cli_sequence([
      "-p",
      path,
      "-i",
      ignoreDirectories,
      "-n",
      checkpointName,
      "-a",
      action,
    ])((status) => {
      eel.read_logs()((logs) => {
        filterLogs(logs);
      });
    });
  };

  const getAllCheckpoints = (e) => {
    e.preventDefault();
    eel.get_all_checkpoints(pathRef.current.value)((ret) => {
      setCheckpointArray(ret);
    });
  };
  const filterLogs = (array) => {
    array.map((log, idx) => {
      if (
        log.includes("ERROR") ||
        log.includes("INFO") ||
        log.includes("WARNING")
      ) {
        setErrorLogarray((prev) => [...prev, log]);
      } else {
        setLogarray((prev) => [...prev, log]);
      }
    });
  };

  return (
    <Container className="splash-div">
      <Row className="dir-tree-div">
        <Col lg={12} className="neu-box my-2">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Directory Tree
          </GradientText>
        </Col>
      </Row>
      <Row className="checkpoint-div">
        <Col lg={12} className="neu-box my-2">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            All Checkpoints
          </GradientText>
          <br />
          {checkpointArray.length ? (
            checkpointArray.map((checkpoint, idx) => {
              return (
                <>
                  <GradientText
                    key={idx}
                    startColor="#f18303"
                    endColor="#f94409"
                    style={{ textDecoration: "underline" }}
                  >
                    <a onClick={() => {}}>{checkpoint}</a>
                  </GradientText>
                  <br />
                </>
              );
            })
          ) : (
            <>
              <GradientText
                startColor="#505963"
                endColor="#3f4e49"
              >
                No Checkpoints!
              </GradientText>
              <br />
            </>
          )}
        </Col>
      </Row>
      <Row className="details-div">
        <Col lg={12} className="neu-box my-2">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Enter Details
          </GradientText>
          <Container>
            <Row>
              <form onSubmit={handleSubmit}>
                <Col lg={12} className="my-2">
                  <TextBox
                    value={checkpointName}
                    onChange={(e) => {
                      setCheckpointName(e.target.value);
                    }}
                    placeholder="Enter Checkpoint Name"
                    required={true}
                  />
                </Col>
                <Col lg={12} className="my-2">
                  <TextBox
                    inputref={pathRef}
                    value={path}
                    onChange={(e) => {
                      setPath(e.target.value);
                    }}
                    placeholder="Enter Directory Path"
                    required={true}
                  />
                </Col>
                <Col lg={12} className="my-2">
                  <Button
                    onClick={getAllCheckpoints}
                    width={100}
                    height={40}
                    text={
                      <GradientText startColor="#f18303" endColor="#f94409">
                        Get Checkpoints
                      </GradientText>
                    }
                  />
                </Col>
                <Col lg={12} className="my-2">
                  <TextBox
                    value={ignoreDirectories}
                    onChange={(e) => {
                      setIgnoreDirectories(e.target.value);
                    }}
                    placeholder="Ignore Directories (Space Seperated)"
                    required={false}
                  />
                </Col>
                <Col lg={12} className="my-2">
                  <FormSelect
                    className="options"
                    defaultValue={action}
                    onChange={(e) => {
                      setAction(e.target.value);
                    }}
                  >
                    <option>Select Action</option>
                    <option value="init">Init</option>
                    <option value="create">Create</option>
                    <option value="restore">Restore</option>
                    <option value="delete">Delete</option>
                  </FormSelect>
                </Col>
                <Col lg={12} className="my-2">
                  <Button
                    onClick={() => {}}
                    width={100}
                    height={40}
                    text={
                      <GradientText startColor="#f18303" endColor="#f94409">
                        Go!
                      </GradientText>
                    }
                  />
                </Col>
              </form>
            </Row>
          </Container>
        </Col>
      </Row>
      <Row className="log-div">
        <Col className="log-neu-box mx-1">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Checkpoint Status
          </GradientText>
          <br />
          {logarray.map((log, index) => {
            return (
              <code>
                <GradientText
                  startColor="#00E46A"
                  endColor="#00B152"
                  style={{ textDecoration: "underline" }}
                >
                  {log}
                </GradientText>
                <br />
              </code>
            );
          })}
        </Col>
        <Col className="neu-box mx-1">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Logs/Warnings
          </GradientText>
          <br />
          {errorLogarray.map((log, index) => {
            return (
              <code>
                <GradientText
                  startColor="#FA0003"
                  endColor="#C70002"
                  style={{ textDecoration: "underline" }}
                >
                  {log}
                </GradientText>
                <br />
              </code>
            );
          })}
        </Col>
      </Row>
    </Container>
  );
};

export default Home;
