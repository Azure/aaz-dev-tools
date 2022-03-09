import React from "react";
import {Navbar, Nav, Container, Button} from "react-bootstrap"

const Generator = () => {
  return (
    <div>
      <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
        <Container>
          <Navbar.Brand>Module Name</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="#features">Profile1</Nav.Link>
              <Nav.Link href="#pricing">Profile2</Nav.Link>
            </Nav>
            <Button>
              Generate
            </Button>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </div>
  )
}

export default Generator;
