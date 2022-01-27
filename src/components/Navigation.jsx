import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { AiFillGithub } from "react-icons/ai";

const Navigation = () => {
  return (
    <Navbar
      collapseOnSelect
      expand="lg"
      bg="dark"
      variant="dark"
      className="navbar"
    >
      <Container>
        <Navbar.Brand href="">
          <img
            src="https://raw.githubusercontent.com/antrikshmisri/checkpoint/master/docs/_static/favicon.ico"
            alt="checkpoint-logo"
          />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        <Navbar.Collapse id="responsive-navbar-nav">
          <Nav className="me-auto"> </Nav>
          <Nav>
            <Nav.Link href="#">Guide</Nav.Link>
            <Nav.Link eventKey={2} href="#">
              About
            </Nav.Link>
            <Nav.Link href="https://github.com/antrikshmisri/checkpoint">
              <AiFillGithub style={{ fontSize: "1.5rem" }} />
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
