import React, { Component, MouseEventHandler } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { ListGroup, Row, Col, Navbar, Nav, Dropdown, DropdownButton, Spinner } from "react-bootstrap"

type ParamsType = {
  workspaceName: String
}

type SpecSelectorProp = {
  params: ParamsType
}

type SpecSelectState = {
  mgmtPlane: boolean,
  modules: DictType,
  selectedModule: string,
  resourceProviders: DictType,
  selectedResourceProvider: string,
  resources: DictType,
  loadingResources: boolean
}

type Instance = {
  folder: string,
  name: string,
  url: string
}

type DictType = {
  [name: string]: string
}


class SpecSelector extends Component<SpecSelectorProp, SpecSelectState> {
  constructor(props: any) {
    super(props);
    this.state = {
      mgmtPlane: true,
      modules: {},
      selectedModule: "",
      resourceProviders: {},
      selectedResourceProvider: "",
      resources: {},
      loadingResources: false
    }
  }

  getModules = () => {
    const plane = this.state.mgmtPlane ? 'mgmt-plane' : 'mgmt-plane'
    axios.get(`/swagger/specs/${plane}`)
      .then((res) => {
        const modules: DictType = {}
        res.data.map((module: Instance) => {
          modules[module.name] = module.url
        })
        this.setState({ modules: modules })
      })
      .catch((err) => console.log(err));
  }

  componentDidMount() {
    this.getModules();
  }

  handleTogglePlane = (eventKey: any) => {
    this.setState({ mgmtPlane: eventKey === 'mgmtPlane', selectedModule: "" })
    this.getModules();
  }

  handleSelectModule = (eventKey: any) => {
    const moduleName: string = eventKey
    const moduleUrl = this.state.modules[moduleName]
    axios.get(`${moduleUrl}/resource-providers`)
      .then((res) => {
        const resourceProviders: DictType = {}
        res.data.map((resourceProvider: Instance) => {
          resourceProviders[resourceProvider.name] = resourceProvider.url
        })
        this.setState({ resourceProviders: resourceProviders, selectedModule: moduleName, selectedResourceProvider: "" })
      })
      .catch((err) => console.log(err));
  }


  handleSelectResourceProvider = (eventKey: any) => {
    const resourceProviderName: string = eventKey
    const resourceProviderUrl = this.state.resourceProviders[resourceProviderName]
    this.setState({loadingResources:true})
    axios.get(`${resourceProviderUrl}/resources`)
      .then((res) => {
        const resources: DictType = {}
        // res.data.map((resourceProvider: Instance) => {
        //   resourceProviders[resourceProvider.name] = resourceProvider.url
        // })
        this.setState({ resources: resources, selectedResourceProvider: resourceProviderName, loadingResources:false})
      })
      .catch((err) => console.log(err));
  }

  listInstances = (instanceDict: {}) => {
    let instanceNames = Object.keys(instanceDict)
    instanceNames.sort((a, b) => a.localeCompare(b))
    return <div>
      {instanceNames.map((instanceName) => {
        return <Dropdown.Item eventKey={instanceName} key={instanceName}>{instanceName}</Dropdown.Item>
      })}
    </div>
  }


  ListModules = () => {
    return this.listInstances(this.state.modules)
  }

  ListResourceProviders = () => {
    return this.listInstances(this.state.resourceProviders)
  }

  instanceHeight = (instanceDict: {}, instance: string) => {
    let instanceList = Object.keys(instanceDict)
    instanceList.sort((a, b) => a.localeCompare(b))
    return 41 * instanceList.indexOf(instance)
  }

  render() {
    return <div>
      <h1>
        Workspace Name: {this.props.params.workspaceName}
      </h1>
      <Row>
        <Col xs="auto">
          <DropdownButton title={this.state.mgmtPlane ? 'Management Plane' : 'Data Plane'} onSelect={this.handleTogglePlane} >
            <Dropdown.Item eventKey='mgmtPlane'>Management Plane</Dropdown.Item>
            <Dropdown.Item eventKey='dataPlane'>Data Plane</Dropdown.Item>
          </DropdownButton>
        </Col>
        <Col xs="auto">
          <DropdownButton title={this.state.selectedModule === "" ? "Please select a module" : this.state.selectedModule} onSelect={this.handleSelectModule} >
            <this.ListModules />
          </DropdownButton>
        </Col>
        <Col xs="auto">
          <DropdownButton title={this.state.selectedResourceProvider === "" ? "Please select a resource provider" : this.state.selectedResourceProvider} onSelect={this.handleSelectResourceProvider} >
            <this.ListResourceProviders />
          </DropdownButton>
        </Col>
        {this.state.loadingResources?(<Col xs="auto">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Col>):<></>}

      </Row>

      <Row className='g-1'>
        {/* <Col>
          <this.ListModules />
        </Col> */}
        {/* <Col style={{ position: "relative", top: `${this.instanceHeight(this.state.modules, this.state.selectedModule)}px` }}>
          <this.ListResourceProviders />
        </Col>

        <Col style={{ position: "relative", top: `${this.instanceHeight(this.state.modules, this.state.selectedModule)}px` }}>
          <this.ListResourceProviders />
        </Col>

        <Col>
          <ListGroup>
            <ListGroup.Item active>Cras justo odio</ListGroup.Item>
            <ListGroup.Item>Dapibus ac facilisis in</ListGroup.Item>
            <ListGroup.Item>Morbi leo risus</ListGroup.Item>
            <ListGroup.Item>Porta ac consectetur ac</ListGroup.Item>
            <ListGroup.Item>Vestibulum at eros</ListGroup.Item>
          </ListGroup>
        </Col> */}
      </Row>

    </div>
  }
}

const SpecSelectorWrapper = (props: any) => {
  const params = useParams()

  return <SpecSelector params={params} {...props} />
}

export { SpecSelectorWrapper as SpecSelector };