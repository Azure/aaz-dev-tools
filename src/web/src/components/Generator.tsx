import React, {Component} from "react";
import {Navbar, Nav, Container, Button} from "react-bootstrap"
import {useParams} from "react-router-dom";


type GeneratorState = {
  currRepo: string,
  profiles: string[]
}


class Generator extends Component<any, GeneratorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      currRepo: "",
      profiles: []
    }
  }

  render() {
    return (
      <div>
        <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
          <Container>
            <Navbar.Brand>{this.props.params.moduleName}</Navbar.Brand>
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
}

const GeneratorWrapper = (props: any) => {
  const params = useParams()
  return <Generator params={params} {...props} />
}

export { GeneratorWrapper as Generator };
