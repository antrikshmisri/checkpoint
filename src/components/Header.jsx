import React from "react";
import { Button, Container, Stack } from "react-bootstrap";

import "./Header.scss";

const Header = () => {
  return (
    <div className="header">
      <Container>
        <div className="header__title">
          <img
            src="https://github.com/antrikshmisri/checkpoint/blob/master/docs/_static/logo.png?raw=true"
            alt="logo"
          />
          <h1>Checkpoint</h1>
          <p className="my-5">
            Create restore points for your project locally.
          </p>
        </div>
        <div className="header__links">
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
      </Container>
    </div>
  );
};

export default Header;
