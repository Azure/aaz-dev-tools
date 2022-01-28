import React, { Component} from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { ListGroup, Row, Col, Button, Dropdown, DropdownButton, Spinner } from "react-bootstrap"

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
  resources: Resources,
  loadingResources: boolean,
  currentResource: string,
  selectedResources: DictBooleanType,
  selectedVersion: DictType
}

type Instance = {
  folder: string,
  name: string,
  url: string,
}

type Resource = {
  id: string,
  versions: Version[]
}

type Version = {
  version: string
}

type DictType = {
  [name: string]: string
}

type DictBooleanType = {
  [name: string]: boolean
}

type Resources = {
  [id: string]: Version[]
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
      loadingResources: false,
      currentResource: "",
      selectedResources: {},
      selectedVersion: {}
    }
  }

  getModules = () => {
    const plane = this.state.mgmtPlane ? 'mgmt-plane' : 'mgmt-plane'
    axios.get(`/Swagger/Specs/${plane}`)
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

  clearResourcesAndVersions = () => {
    this.setState({
      resources: {},
      currentResource: "",
      selectedVersion: {}
    })

  }

  handleTogglePlane = (eventKey: any) => {
    if (eventKey === this.state.mgmtPlane) {
      return
    }
    this.getModules();
  }

  handleSelectModule = (eventKey: any) => {
    if (eventKey === this.state.selectedModule) {
      return
    }
    const moduleName: string = eventKey
    const moduleUrl = this.state.modules[moduleName]
    axios.get(`${moduleUrl}/ResourceProviders`)
      .then((res) => {
        const resourceProviders: DictType = {}
        res.data.map((resourceProvider: Instance) => {
          resourceProviders[resourceProvider.name] = resourceProvider.url
        })
        this.setState({ resourceProviders: resourceProviders, selectedModule: moduleName, selectedResourceProvider: "" })
        this.clearResourcesAndVersions()
      })
      .catch((err) => console.log(err));
  }


  handleSelectResourceProvider = (eventKey: any) => {
    if (eventKey === this.state.selectedResourceProvider) {
      return
    }
    const resourceProviderName: string = eventKey
    const resourceProviderUrl = this.state.resourceProviders[resourceProviderName]
    this.setState({ loadingResources: true })
    axios.get(`${resourceProviderUrl}/Resources`)
      .then((res) => {
        const resources: Resources = {}
        res.data.map((resource: Resource) => {
          resource.versions.sort((a, b) => a.version.localeCompare(b.version))
          resource.versions.reverse()
          resources[resource.id] = resource.versions
        })
        this.setState({ resources: resources, selectedResourceProvider: resourceProviderName, loadingResources: false })
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

  instanceHeight = (instanceDict: {}, instance: string) => {
    let instanceList = Object.keys(instanceDict)
    instanceList.sort((a, b) => a.localeCompare(b))
    return 41 * instanceList.indexOf(instance)
  }

  ListModules = () => {
    return this.listInstances(this.state.modules)
  }

  ListResourceProviders = () => {
    return this.listInstances(this.state.resourceProviders)
  }

  handleToggleVersion = (event: any) => {
    // console.log(event.target.id)
    const resourceId: string = event.target.id
    this.setState({ currentResource: resourceId })
  }

  handleSelectVersion = (eventKey: any) => {
    // console.log(eventKey)
    // console.log(this.state.currentResource)
    const version: string = eventKey
    this.state.selectedVersion[this.state.currentResource] = version
  }

  handleSelectResource = (event: any) => {
    const resourceId: string = event.target.id
    this.state.selectedResources[resourceId] = event.target.checked
  }

  ListResourcesAndVersion = () => {
    let resourceIds = Object.keys(this.state.resources)
    resourceIds.sort((a, b) => a.localeCompare(b))
    return <div>
      <ListGroup>
        {resourceIds.map((resourceId) => {
          if (!(resourceId in this.state.selectedVersion)){
            this.state.selectedVersion[resourceId] = this.state.resources[resourceId][0].version
          }
          
          return <Row key={resourceId}>
            <Col lg='10'>
              <ListGroup.Item><input type="checkbox" onChange={this.handleSelectResource} id={resourceId} />  {resourceId}</ListGroup.Item>
            </Col>
            <Col lg='2'>
              <DropdownButton id={resourceId} title={this.state.selectedVersion[resourceId]} onSelect={this.handleSelectVersion} onClick={this.handleToggleVersion} drop='end'>
                {this.state.resources[resourceId].map((version, index) => {
                  return <Dropdown.Item eventKey={version.version} key={index} active={false}>{version.version}</Dropdown.Item>
                })}
              </DropdownButton>
            </Col>
          </Row>
        })}
      </ListGroup>
    </div>
  }

  saveResourcesAndVersion = () => {
    const finalResources:DictType = {}
    Object.keys(this.state.selectedResources).map(resourceId=>{
      if (this.state.selectedResources[resourceId]){
        finalResources[resourceId] = this.state.selectedVersion[resourceId]
      }
    })
    console.log(finalResources)
  }

  render() {
    return <div className="m-1 p-1">
      <Row>
        <Col lg='10'>
          <h1>
            Workspace Name: {this.props.params.workspaceName}
          </h1>
        </Col>
        <Col lg='2'>
        <Button onClick={this.saveResourcesAndVersion}>Save</Button>
        </Col>

      </Row>

      <Row>
        <Col xs="auto">
          <DropdownButton title={this.state.mgmtPlane ? 'Management Plane' : 'Data Plane'} onSelect={this.handleTogglePlane} >
            <Dropdown.Item eventKey='mgmtPlane'>Management Plane</Dropdown.Item>
            <Dropdown.Item eventKey='dataPlane' disabled>Data Plane</Dropdown.Item>
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
        {this.state.loadingResources ? (<Col xs="auto">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Col>) : <></>}
      </Row>
      <br />
      <Row>
        <Col>
          <this.ListResourcesAndVersion />
        </Col>
      </Row>

    </div>
  }
}

const SpecSelectorWrapper = (props: any) => {
  const params = useParams()

  return <SpecSelector params={params} {...props} />
}

export { SpecSelectorWrapper as SpecSelector };