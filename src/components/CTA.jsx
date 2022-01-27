import React from "react";
import { Container, Stack, Button } from "react-bootstrap";

import "./CTA.scss";

const CTA = () => {
  return (
    <div id="cta">
      <Container>
        <div className="cta">
          <h1>Ready to try?</h1>
          <p>Read the docs to get started</p>
          <div className="cta__links">
            <Stack direction="horizontal" gap={5}>
              <Button variant="light">Get Started</Button>
              <a
                href="http://checkpoint.antriksh.live"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="outline-light">Documentation</Button>
              </a>
            </Stack>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default CTA;
