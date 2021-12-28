import React, { Component } from "react";
import { Routes, Route} from "react-router-dom";
import axios from "axios";
import { InputGroup, Input, Button, } from "reactstrap";
import {Navbar, Nav, Container} from "react-bootstrap"
import ModuleAccordion from "./components/ModuleAccordion"
import Editor from "./components/Editor";
import {Spec} from "./components/ModuleAccordion"


type AppState = {
  mgmtPlaneSpecs: Spec | null,
  dataPlaneSpecs: Spec | null,
  allMgmtPlaneSpecs: Spec,
  allDataPlaneSpecs: Spec,
  moduleName: string,
  moduleFound: boolean,
}

class App extends Component<{}, AppState> {
  constructor(props: any) {
    super(props);
    this.state = {
      mgmtPlaneSpecs: null,
      dataPlaneSpecs: null,
      allMgmtPlaneSpecs: {},
      allDataPlaneSpecs: {},
      moduleName: "",
      moduleFound: false
    };
  }

  componentDidMount(){
   this.listAllSpecs();
  }

  listAllSpecs = () => {
    axios
      .get("/specifications")
      .then((res) => {
        this.setState({ allMgmtPlaneSpecs: res.data["mgmt"], 
                        allDataPlaneSpecs: res.data["data"],
                        mgmtPlaneSpecs: res.data["mgmt"],
                        dataPlaneSpecs: res.data["data"],
                      })
      })
      .catch((err) => console.log(err));
  };

  handleSearch = () => {
    let found = false
    if (this.state.moduleName in this.state.allMgmtPlaneSpecs){
      let mgmtPlaneSpecs:Spec = {};
      mgmtPlaneSpecs[this.state.moduleName] = this.state.allMgmtPlaneSpecs[this.state.moduleName]
      this.setState({ mgmtPlaneSpecs: mgmtPlaneSpecs})
      found = true
    } else {
      this.setState({ mgmtPlaneSpecs: null})
    }
    if (this.state.moduleName in this.state.allDataPlaneSpecs){
      let dataPlaneSpecs:Spec = {};
      dataPlaneSpecs[this.state.moduleName] = this.state.allDataPlaneSpecs[this.state.moduleName]
      this.setState({ dataPlaneSpecs: dataPlaneSpecs})
      found = true
    } else {
      this.setState({ dataPlaneSpecs: null})
    }
    if (!found){
      this.setState({ mgmtPlaneSpecs: null, dataPlaneSpecs: null, moduleFound: false})
    } else {
      this.setState({moduleFound: true})
    }
  }

  handleInput = (e: any) => {
    this.setState({moduleName: e.target.value})
  }

  SearchBar = () => {
    return <InputGroup>
            <Input placeholder="Module Name" value={this.state.moduleName} onChange={this.handleInput}/>
            <Button onClick={this.handleSearch}>Search</Button>
          </InputGroup>
  }

  Specs = () => {
    return  <div className="container-fluid row">
              <this.SearchBar/>
              <br/>
              <ModuleAccordion hidden={!this.state.moduleFound} mgmtPlaneSpecs={this.state.mgmtPlaneSpecs} dataPlaneSpecs={this.state.dataPlaneSpecs}></ModuleAccordion>
              <ModuleAccordion hidden={this.state.moduleFound} mgmtPlaneSpecs={this.state.allMgmtPlaneSpecs} dataPlaneSpecs={this.state.allDataPlaneSpecs}></ModuleAccordion>
            </div>
      
  }

  render() {
    return (
      <main className="container">
        <Navbar bg="dark" variant="dark">
          <Container>
          <Nav className="me-auto">
            <Nav.Link href="/">Specifications</Nav.Link>
            <Nav.Link href="/editor">Editor</Nav.Link>
          </Nav>
          </Container>
        </Navbar>

        <Routes>
          <Route path="/" element={<this.Specs />} />
          <Route path="editor" element={<Editor />} />
        </Routes>
        </main>
    );
  }
}

export default App;