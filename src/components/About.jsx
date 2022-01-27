import React from "react";
import { Container } from "react-bootstrap";

import "./About.scss";

const About = () => {
  return (
    <div id="about">
      <Container>
        <div className="about">
          <div className="about__middle-img text-center">
            <img
              src="https://user-images.githubusercontent.com/54466356/140969067-6e845c1a-dc7d-4985-a0e1-d47583eb0523.png"
              alt="checkpoint"
            />
          </div>

          <div className="about__content">
            <h1>How it works?</h1>
            <div className="about__content__details mt-5">
              <p>
                Checkpoint provides multiple Sequence classes that have memeber
                functions which execute based on their order in the sequence.
                These sequences are used to perform all the sequentional
                operations that are required to create a restore point. Some of
                these sequences are:
              </p>
              <ul>
                <li>
                  IOSequence: This sequence is used to perfrom all the
                  input/output sequentional operations.
                </li>
                <li>
                  CLISequence: This sequence is used to perform all the CLI
                  operations which includes parsing the arguments, determining
                  the action and performing the action.
                </li>
              </ul>
              <p>
                Checkpoint also supports custom sequences that can be used to
                initialize checkpoint in different environments. For example, if
                checkpoint isto be initialized in a UI enviroment a sequence for
                UI can be created and passed to the Checkpoint constructor.
              </p>
            </div>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default About;
