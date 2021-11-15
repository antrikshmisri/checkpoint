import React, { useState, useRef } from "react";

import { AiOutlineCheck, AiOutlineClose, AiFillRocket } from "react-icons/ai";
import { ImLocation } from "react-icons/im";

import GradientText from "../components/gradientText";
import TextBox from "../components/textbox";
import Button from "../components/button";

import { Container, Row, Col, FormSelect } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

import HashLoader from "react-spinners/HashLoader";
import PulseLoader from "react-spinners/PulseLoader";

import spinnerStyle from "../constants/spinnerStyles";
import Tree from "../components/tree";
import notify from "../utils/toast";
import { eel } from "../eel";

const Home = () => {
  const [inputs, setInputs] = useState({
    path: "",
    ignoreDirectories: "",
    checkpointName: "",
    action: "init",
  });

  const [logState, setLogState] = useState({
    logarray: [],
    errorLogarray: [],
  });

  const [pathOutlineColor, setPathOutlineColor] = useState(
    "rgb(54, 57, 59, 0.7)"
  );

  const [checkpointArray, setCheckpointArray] = useState([]);
  const [treeStructure, setTreeStructure] = useState({});
  const [loading, setLoading] = useState(false);

  const pathRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setLogState({
      logarray: [],
      errorLogarray: [],
    });
    eel.run_cli_sequence([
      "-p",
      inputs.path,
      "-i",
      inputs.ignoreDirectories,
      "-n",
      inputs.checkpointName,
      "-a",
      inputs.action,
    ])((status) => {
      eel.read_logs()((logs) => {
        setLoading(false);
        filterLogs(logs);
        status
          ? notify(`${inputs.action} action, successful`, "success")
          : notify(`${inputs.action} action, failed`, "error");
        status && getAllCheckpoints(e);
      });
    });
  };

  const getAllCheckpoints = (e) => {
    e.preventDefault();
    eel.get_all_checkpoints(pathRef.current.value)((allCheckpoints) => {
      eel.get_current_checkpoint(pathRef.current.value)((currentCheckpoint) => {
        allCheckpoints.length &&
          notify("Fetched checkpoint configurations", "success");

        if (!currentCheckpoint) {
          setCheckpointArray(allCheckpoints);
        } else {
          getCheckpointTree(currentCheckpoint, pathRef.current.value);
          setCheckpointArray([
            ...allCheckpoints.map((checkpoint, idx) => {
              if (checkpoint === currentCheckpoint) {
                return checkpoint + "*";
              } else {
                return checkpoint;
              }
            }),
          ]);
        }
      });
    });
  };
  const filterLogs = (array) => {
    array.map((log, idx) => {
      if (
        log.includes("ERROR") ||
        log.includes("INFO") ||
        log.includes("WARNING")
      ) {
        setLogState((prevState) => ({
          ...prevState,
          errorLogarray: [...prevState.errorLogarray, log],
        }));
      } else {
        setLogState((prevState) => ({
          ...prevState,
          logarray: [...prevState.logarray, log],
        }));
      }
    });
  };

  const getCheckpointTree = (checkpoint, targetDirectory) => {
    eel.generate_tree(
      checkpoint.split("*")[0],
      targetDirectory
    )((dirTree) => {
      setTreeStructure(dirTree);
    });
  };

  const pathValidator = (e) => {
    eel.validate_path(e.target.value)((isValid) => {
      if (!isValid) {
        setPathOutlineColor("rgba(249, 68, 9, 0.5)");
      } else {
        getAllCheckpoints(e);
        setPathOutlineColor("rgb(54, 57, 59, 0.7)");
        eel.get_ignore_dirs(pathRef.current.value)((ignoreDirs) => {
          setInputs((prevState) => ({
            ...prevState,
            ignoreDirectories: ignoreDirs.join(" "),
          }));
        });
      }
    });
  };

  return (
    <Container className="splash-div">
      <div className={loading ? "overlay-bg" : ""}></div>
      <HashLoader
        loading={loading}
        className="spinner"
        color={"#f94409"}
        css={spinnerStyle}
        speedMultiplier={1.2}
      />
      <Row className="dir-tree-div">
        <Col lg={12} className="dir-tree-box my-2">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Directory Tree
          </GradientText>
          <br />
          {Object.keys(treeStructure).length ? (
            <Tree structure={treeStructure} />
          ) : (
            <GradientText startColor="#505963" endColor="#3f4e49">
              No Tree!
            </GradientText>
          )}
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
                    startColor={
                      checkpoint.includes("*") ? "#f94409" : "#f18303"
                    }
                    endColor={checkpoint.includes("*") ? "#f94409" : "#f94409"}
                    style={{ textDecoration: "underline" }}
                  >
                    <a
                      onClick={() => {
                        getCheckpointTree(checkpoint, pathRef.current.value);
                      }}
                    >
                      <code>{checkpoint.split("*")[0]} </code>
                      <ImLocation color="#f18303" className="mx-1" size={10} />
                    </a>
                  </GradientText>
                  <br />
                </>
              );
            })
          ) : (
            <>
              <GradientText startColor="#505963" endColor="#3f4e49">
                No Checkpoints!
              </GradientText>
              <br />
            </>
          )}
        </Col>
      </Row>
      <Row className="details-div">
        <Col lg={12} className="details-box neu-box my-2">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Enter Details
          </GradientText>
          <form className="details-form py-0" onSubmit={handleSubmit}>
            <Container className="fluid">
              <Row>
                <Container className="fluid">
                  <Row className="d-flex align-items-end">
                    <Col lg={12} className="my-2">
                      <TextBox
                        label="Path"
                        inputref={pathRef}
                        value={inputs.path}
                        onChange={(e) => {
                          setInputs((prevState) => ({
                            ...prevState,
                            path: e.target.value,
                          }));
                        }}
                        placeholder="Enter Directory Path"
                        required={true}
                        keyPressCallback={pathValidator}
                        outlineColor={pathOutlineColor}
                      />
                    </Col>
                  </Row>
                </Container>
                <Col lg={12} className="my-2">
                  <TextBox
                    label="Checkpoint Name"
                    value={inputs.checkpointName}
                    onChange={(e) => {
                      setInputs((prevState) => ({
                        ...prevState,
                        checkpointName: e.target.value,
                      }));
                    }}
                    placeholder="Enter Checkpoint Name"
                    required={true}
                  />
                </Col>
                <Col lg={12} className="my-2">
                  <TextBox
                    label="Ignore Directories"
                    value={inputs.ignoreDirectories}
                    onChange={(e) => {
                      setInputs((prevState) => ({
                        ...prevState,
                        ignoreDirectories: e.target.value,
                      }));
                    }}
                    placeholder="Ignore Directories (Space Seperated)"
                    required={false}
                  />
                </Col>
                <Col lg={9} className="mt-4">
                  <FormSelect
                    className="options"
                    defaultValue={inputs.action}
                    onChange={(e) => {
                      setInputs((prevState) => ({
                        ...prevState,
                        action: e.target.value,
                      }));
                    }}
                  >
                    <option value="init">Init</option>
                    <option value="create">Create</option>
                    <option value="restore">Restore</option>
                    <option value="delete">Delete</option>
                  </FormSelect>
                </Col>
                <Col lg={3} className="mt-4">
                  <Button
                    className="d-flex justify-content-center align-items-center"
                    onClick={() => {}}
                    width={80}
                    height={40}
                    text={
                      <GradientText startColor="#f18303" endColor="#f94409">
                        Go{" "}
                        <AiFillRocket
                          size={15}
                          className="mx-0"
                          style={{ transform: "rotateZ(25deg)" }}
                        />
                      </GradientText>
                    }
                  />
                </Col>
              </Row>
            </Container>
          </form>
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
          <PulseLoader
            className="mx-5"
            color={"#f94409"}
            loading={loading}
            size={5}
          />
          {logState.logarray.map((log, index) => {
            return (
              <code>
                <GradientText
                  startColor="#00E46A"
                  endColor="#00B152"
                  style={{ textDecoration: "underline" }}
                >
                  {log} {<AiOutlineCheck color="#00B152" />}
                </GradientText>
                <br />
              </code>
            );
          })}
        </Col>
        <Col className="log-neu-box mx-1">
          <GradientText
            startColor="#f18303"
            endColor="#f94409"
            style={{ textDecoration: "underline" }}
          >
            Logs/Warnings
          </GradientText>
          <br />
          <PulseLoader
            className="mx-5"
            color={"#f94409"}
            loading={loading}
            size={5}
          />
          {logState.errorLogarray.map((log, index) => {
            return (
              <code>
                <GradientText
                  startColor="#FA0003"
                  endColor="#C70002"
                  style={{ textDecoration: "underline" }}
                >
                  {log} {<AiOutlineClose color="#C70002" />}
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
