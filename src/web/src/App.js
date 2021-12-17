import React, { Component } from "react";
import axios from "axios";
import { InputGroup, Input, Button} from "reactstrap";
import ModuleAccordion from "./components/ModuleAccordion"


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      mgmtPlaneSpecs: [],
      dataPlaneSpecs: [],
      allMgmtPlaneSpecs: [],
      allDataPlaneSpecs: [],
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
      let mgmtPlaneSpecs = {}
      mgmtPlaneSpecs[this.state.moduleName] = this.state.allMgmtPlaneSpecs[this.state.moduleName]
      this.setState({ mgmtPlaneSpecs: mgmtPlaneSpecs})
      found = true
    } else {
      this.setState({ mgmtPlaneSpecs: null})
    }
    if (this.state.moduleName in this.state.allDataPlaneSpecs){
      let dataPlaneSpecs = {}
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

  handleInput = e => {
    this.setState({moduleName: e.target.value})
  }

  searchBar = () => {
    return <InputGroup>
            <Input placeholder="Module Name" value={this.state.moduleName} onChange={this.handleInput}/>
            <Button onClick={this.handleSearch}>Search</Button>
          </InputGroup>
  }

  render() {
    return (
      <main className="container">
        <this.searchBar/>
        <br/>
        <ModuleAccordion hidden={!this.state.moduleFound} mgmtPlaneSpecs={this.state.mgmtPlaneSpecs} dataPlaneSpecs={this.state.dataPlaneSpecs}></ModuleAccordion>
        <ModuleAccordion hidden={this.state.moduleFound} mgmtPlaneSpecs={this.state.allMgmtPlaneSpecs} dataPlaneSpecs={this.state.allDataPlaneSpecs}></ModuleAccordion>
      </main>
    );
  }
}

export default App;