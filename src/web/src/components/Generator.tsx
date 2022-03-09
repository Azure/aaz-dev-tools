import React, {Component} from "react";
import {Navbar, Nav, Container, Button} from "react-bootstrap"
import {useParams} from "react-router-dom";
import axios from "axios";


type GeneratorState = {
  moduleName: string,
  profiles: string[]
}


class Generator extends Component<any, GeneratorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      moduleName: this.props.params.moduleName,
      profiles: []
    }
  }

  componentDidMount() {
    axios.get("/CLI/Az/Profiles")
        .then(res => {this.setState({profiles: res.data})})
  }

  render() {
    return (
      <div>
        <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
          <Container>
            <Navbar.Brand>{this.state.moduleName}</Navbar.Brand>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
              <Nav className="me-auto">{
                this.state.profiles.map((profile: string) => {
                  return <Nav.Link href={`#${profile}`}>{profile}</Nav.Link>
                })
              }
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
  return <Generator params={params} {...props}/>
}

export {GeneratorWrapper as Generator};
