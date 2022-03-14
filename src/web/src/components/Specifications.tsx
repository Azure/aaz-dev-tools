import React, { Component } from "react";
import axios from "axios";
import ModuleAccordion from "./ModuleAccordion"
import { InputGroup, Input } from "reactstrap";
import { Button } from "react-bootstrap"
import { Spec } from "./ModuleAccordion"


type SpecsState = {
  mgmtPlaneSpecs: Spec | null,
  dataPlaneSpecs: Spec | null,
  allMgmtPlaneSpecs: Spec,
  allDataPlaneSpecs: Spec,
  moduleName: string,
  moduleFound: boolean
}

export default class Specifications extends Component<{}, SpecsState> {

  constructor(props: any) {
    super(props);
    this.state = {
      mgmtPlaneSpecs: null,
      dataPlaneSpecs: null,
      allMgmtPlaneSpecs: {},
      allDataPlaneSpecs: {},
      moduleName: "",
      moduleFound: false,
    };
  }

  componentDidMount() {
    this.listAllSpecs();
  }

  listAllSpecs = () => {
    axios.get("/swagger/specs/mgmt-plane")
      .then((res) => {
        let modules = res.data.map((module: any) => {
          return module.name
        })
      })
      .catch((err) => console.log(err));
  };

  handleSearch = () => {
    let found = false
    if (this.state.moduleName in this.state.allMgmtPlaneSpecs) {
      let mgmtPlaneSpecs: Spec = {};
      mgmtPlaneSpecs[this.state.moduleName] = this.state.allMgmtPlaneSpecs[this.state.moduleName]
      this.setState({ mgmtPlaneSpecs: mgmtPlaneSpecs })
      found = true
    } else {
      this.setState({ mgmtPlaneSpecs: null })
    }
    if (this.state.moduleName in this.state.allDataPlaneSpecs) {
      let dataPlaneSpecs: Spec = {};
      dataPlaneSpecs[this.state.moduleName] = this.state.allDataPlaneSpecs[this.state.moduleName]
      this.setState({ dataPlaneSpecs: dataPlaneSpecs })
      found = true
    } else {
      this.setState({ dataPlaneSpecs: null })
    }
    if (!found) {
      this.setState({ mgmtPlaneSpecs: null, dataPlaneSpecs: null, moduleFound: false })
    } else {
      this.setState({ moduleFound: true })
    }
  }

  handleInput = (e: any) => {
    this.setState({ moduleName: e.target.value })
  }

  Specs = () => {
    return <div className="container-fluid row">
      <InputGroup>
        <Input placeholder="Module Name" value={this.state.moduleName} onChange={this.handleInput} />
        <Button onClick={this.handleSearch}>Search</Button>
      </InputGroup>
      <br />
      <ModuleAccordion hidden={!this.state.moduleFound} mgmtPlaneSpecs={this.state.mgmtPlaneSpecs} dataPlaneSpecs={this.state.dataPlaneSpecs}></ModuleAccordion>
      <ModuleAccordion hidden={this.state.moduleFound} mgmtPlaneSpecs={this.state.allMgmtPlaneSpecs} dataPlaneSpecs={this.state.allDataPlaneSpecs}></ModuleAccordion>
    </div>
  }


  render() {
    return <div>

      {/* <Navbar bg="dark" variant="dark">
          <Container>
          <Nav className="me-auto">
            <Nav.Link href="/">Specifications</Nav.Link>
            <Nav.Link href="/editor">Editor</Nav.Link>
          </Nav>
          </Container>
    </Navbar>*/}
      <this.Specs />
    </div>
  }
} 