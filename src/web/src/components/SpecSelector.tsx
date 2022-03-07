import React, { Component } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { ListGroup, Row, Col, Button, Dropdown, DropdownButton, Spinner, Navbar, Nav, Container } from "react-bootstrap"
import { Set } from "typescript";

type ParamsType = {
  workspaceName: String
}

type WrapperProp = {
  params: ParamsType
}

type SpecSelectState = {
  mgmtPlane: boolean,
  modules: DictType,
  selectedModule: string,
  prevModule: string,
  resourceProviders: DictType,
  selectedResourceProvider: string,
  prevResourceProvider: string,
  resources: Resources,
  loadingResources: boolean,
  selectedResources: Set<string>,
  prevResources: Set<string>,
  versions: Versions,
  selectedVersion: string,
  prevVersion: string,
  altered: boolean
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

type Versions = {
  [version: string]: string[]
}

type Resources = {
  [id: string]: Version[]
}

type Swagger = {
  module: string,
  version: string,
  resources: string[]
}


class SpecSelector extends Component<WrapperProp, SpecSelectState> {
  constructor(props: any) {
    super(props);
    this.state = {
      mgmtPlane: true,
      modules: {},
      selectedModule: "",
      prevModule: "",
      resourceProviders: {},
      selectedResourceProvider: "",
      prevResourceProvider: "",
      resources: {},
      loadingResources: false,
      selectedResources: new Set<string>(),
      prevResources: new Set<string>(),
      versions: {},
      selectedVersion: "",
      prevVersion: "",
      altered: false
    }
  }

  getModules = () => {
    const plane = this.state.mgmtPlane ? 'mgmt-plane' : 'mgmt-plane'
    return axios.get(`/Swagger/Specs/${plane}`)
      .then((res) => {
        const modules: DictType = {}
        res.data.map((module: Instance) => {
          modules[module.name] = module.url
        })
        this.setState({ modules: modules })
      })
      .catch((err) => console.log(err.response.message));
  }

  getSwagger = () => {
    let module = "";
    let resourceProvider = "";
    let version = "";
    let resources = new Set<string>();
    return axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/Resources`)
      .then(res => {
        if (res.data && Array.isArray(res.data) && res.data.length > 0) {

          module = res.data[0].swagger.split('/')[1]
          resourceProvider = res.data[0].swagger.split('/')[3]
          version = res.data[0].version
          this.setState({
            prevModule: module,
            prevResourceProvider: resourceProvider,
            prevVersion: version
          })
          return this.handleSelectModule(module)
            .then(() => {
              return this.handleSelectResourceProvider(resourceProvider)
            })
            .then(() => {
              this.handleSelectVersion(version)
              for (let resource of res.data) {
                resources.add(resource.id)
                let checkbox = document.getElementById(resource.id)
                if (checkbox) {
                  checkbox.click()
                }
              }
              this.setState({ prevResources: resources })
              this.state.selectedResources.clear()
              this.setState({ altered: this.checkAltered() })
            })
        }
      })
      .catch((err) => console.log(err));
  }

  resetResourcesAndVersion = () => {
    console.log("reset")
  }

  componentDidMount() {
    this.getModules()
      .then(() => {
        this.getSwagger()
      })

  }

  clearResourcesAndVersions = () => {
    this.setState({
      resources: {},
      selectedResources: new Set<string>(),
      selectedVersion: "",
      versions: {}
    })

  }

  checkAltered = () => {
    return true
    let altered = this.state.selectedModule !== this.state.prevModule
    altered = altered || this.state.selectedResourceProvider !== this.state.prevResourceProvider
    altered = altered || this.state.selectedVersion !== this.state.prevVersion
    let areSetsEqual = (a: any, b: any) => a.size === b.size && [...a].every(value => b.has(value));
    altered = altered || !areSetsEqual(this.state.selectedResources, this.state.prevResources)
    return altered
  }

  handleTogglePlane = (eventKey: any) => {
    if (eventKey === this.state.mgmtPlane) {
      return
    }
    this.getModules();
  }

  handleSelectModule = (eventKey: any) => {
    if (eventKey === this.state.selectedModule) {
      return Promise.resolve();
    }
    const moduleName: string = eventKey
    const moduleUrl = this.state.modules[moduleName]
    return axios.get(`${moduleUrl}/ResourceProviders`)
      .then((res) => {
        const resourceProviders: DictType = {}
        res.data.map((resourceProvider: Instance) => {
          resourceProviders[resourceProvider.name] = resourceProvider.url
        })
        this.setState({
          resourceProviders: resourceProviders,
          selectedModule: moduleName,
          selectedResourceProvider: "",
          altered: this.checkAltered()
        })
        this.clearResourcesAndVersions()
      })
      .catch((err) => console.log(err.response.message));
  }


  handleSelectResourceProvider = (eventKey: any) => {
    if (eventKey === this.state.selectedResourceProvider) {
      return Promise.resolve();
    }
    const resourceProviderName: string = eventKey
    const resourceProviderUrl = this.state.resourceProviders[resourceProviderName]
    this.setState({ loadingResources: true })
    return axios.get(`${resourceProviderUrl}/Resources`)
      .then((res) => {

        const resources: Resources = {}
        const versions: Versions = {}
        let selectedVersion: string = ""
        res.data.map((resource: Resource) => {
          resource.versions.sort((a, b) => a.version.localeCompare(b.version))
          resource.versions.reverse()
          selectedVersion = resource.versions[0].version
          resources[resource.id] = resource.versions
          resource.versions.map((versionObj: Version) => {
            const version = versionObj.version
            if (!(version in versions)) {
              versions[version] = []
            }
            versions[version].push(resource.id)
          })
        })
        this.setState({
          resources: resources,
          versions: versions,
          selectedVersion: selectedVersion,
          selectedResourceProvider: resourceProviderName,
          loadingResources: false,
          altered: this.checkAltered()
        })
      })
      .catch((err) => console.log(err.response.message));
  }

  listInstances = (instanceDict: {}, sortDesc: boolean = false) => {
    let instanceNames = Object.keys(instanceDict)
    instanceNames.sort((a, b) => a.localeCompare(b))
    if (sortDesc) {
      instanceNames.reverse()
    }
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

  handleSelectVersion = (eventKey: any) => {
    const version: string = eventKey
    this.setState({ selectedVersion: version, altered: this.checkAltered() })
  }

  handleSelectResource = (event: any) => {
    const resourceId: string = event.target.id
    if (event.target.checked) {
      this.state.selectedResources.add(resourceId)
    } else {
      this.state.selectedResources.delete(resourceId)
    }

    this.setState({
      altered: this.checkAltered()
    })
  }

  ListVersions = () => {
    return this.listInstances(this.state.versions, true)
  }

  ListResources = () => {
    if (!this.state.selectedVersion) {
      return <></>
    }
    let resourceIds = this.state.versions[this.state.selectedVersion]
    resourceIds.sort((a, b) => a.localeCompare(b))
    return <div>
      <ListGroup>
        {resourceIds.map((resourceId) => {
          return <ListGroup.Item key={resourceId}><input type="checkbox" checked={this.state.prevResources.has(resourceId) || this.state.selectedResources.has(resourceId)} disabled={this.state.prevResources.has(resourceId)} onChange={this.handleSelectResource} id={resourceId} /> {resourceId}</ListGroup.Item>
        })}
      </ListGroup>
    </div>
  }

  saveResourcesAndVersion = () => {
    const finalResources: Swagger = {
      module: this.state.selectedModule,
      version: this.state.selectedVersion,
      resources: []
    }
    this.state.selectedResources.forEach(resourceId => {
      finalResources.resources.push(resourceId)
    })
    console.log(finalResources)
    this.addSwagger(finalResources)
  }

  addSwagger = (requestBody: Swagger) => {
    axios.post(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/AddSwagger`, requestBody)
      .then(() => {
        axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz`)
          .then((res) => {
            console.log(res.data)
            window.location.reload();
          })

      })
      .catch((err) => console.log(err.response));
  }



  render() {
    return <div className="m-1 p-1">
      <Navbar bg="dark" variant="dark">
          <Navbar.Brand href="editor">Editor</Navbar.Brand>
          <Navbar.Brand href="resourceSelection">Resource Selection</Navbar.Brand>
          <Nav className="me-auto"/>
      </Navbar>
      <Row>
        <Col lg='11'>
          <h1>
            Workspace Name: {this.props.params.workspaceName}
          </h1>
        </Col>
        <Col lg="auto">
          {this.state.altered ? <Button variant="dark" onClick={this.saveResourcesAndVersion}>Save</Button> : <Button onClick={this.resetResourcesAndVersion}>Cancel</Button>}
        </Col>

      </Row>

      <Row>
        <Col xs="auto">
          <DropdownButton variant="dark" title={this.state.mgmtPlane ? 'Management Plane' : 'Data Plane'} onSelect={this.handleTogglePlane} >
            <Dropdown.Item eventKey='mgmtPlane'>Management Plane</Dropdown.Item>
            <Dropdown.Item eventKey='dataPlane' disabled>Data Plane</Dropdown.Item>
          </DropdownButton>
        </Col>
        <Col xs="auto">
          <DropdownButton variant="dark" title={this.state.selectedModule === "" ? "Please select a module" : this.state.selectedModule} onSelect={this.handleSelectModule} >
            <this.ListModules />
          </DropdownButton>
        </Col>
        <Col xs="auto">
          <DropdownButton variant="dark" title={this.state.selectedResourceProvider === "" ? "Please select a resource provider" : this.state.selectedResourceProvider} onSelect={this.handleSelectResourceProvider} >
            <this.ListResourceProviders />
          </DropdownButton>
        </Col>
        {this.state.loadingResources ? (<Col xs="auto">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Col>) : <></>}
        <Col xs="auto">
          <DropdownButton variant="dark" title={this.state.selectedVersion === "" ? "Please select a version" : this.state.selectedVersion} onSelect={this.handleSelectVersion} >
            <this.ListVersions />
          </DropdownButton>
        </Col>
      </Row>
      <br />
      <Row>
        <Col>
          <this.ListResources />
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
export type { WrapperProp }