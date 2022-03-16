import React, { Component } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { ListGroup, Row, Col, Button, Dropdown, DropdownButton, Spinner, Modal, } from "react-bootstrap"
import { Set } from "typescript";

type WrapperProp = {
  params: {
    workspaceName: string
  },
  onCloseModal: () => void
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
  prevVersion: string
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
  resources: {
    id: string
  }[]
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
      prevVersion: ""
    }
  }

  getModules = () => {
    const plane = this.state.mgmtPlane ? 'mgmt-plane' : 'mgmt-plane'
    return axios.get(`/Swagger/Specs/${plane}`)
      .then((res) => {
        const modules: DictType = {}
        res.data.forEach((module: Instance) => {
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
            })
        }
      })
      .catch((err) => console.log(err));
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
        res.data.forEach((resourceProvider: Instance) => {
          resourceProviders[resourceProvider.name] = resourceProvider.url
        })
        this.setState({
          resourceProviders: resourceProviders,
          selectedModule: moduleName,
          selectedResourceProvider: ""
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
        res.data.forEach((resource: Resource) => {
          resource.versions.sort((a, b) => a.version.localeCompare(b.version))
          resource.versions.reverse()
          selectedVersion = resource.versions[0].version
          resources[resource.id] = resource.versions
          resource.versions.forEach((versionObj: Version) => {
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
          loadingResources: false
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
    return <div style={{ maxHeight: this.calculatePageHeight(140), overflow: `auto` }}>
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

  handleSelectVersion = (eventKey: any) => {
    const version: string = eventKey
    this.setState({ selectedVersion: version})
  }

  handleSelectResource = (event: any) => {
    const resourceId: string = event.target.id
    if (event.target.checked) {
      this.state.selectedResources.add(resourceId)
    } else {
      this.state.selectedResources.delete(resourceId)
    }
    this.setState({selectedResources: this.state.selectedResources})
  }

  ListVersions = () => {
    return this.listInstances(this.state.versions, true)
  }

  calculatePageHeight = (subtractAmount: number) => {
    const body = document.body;
    const html = document.documentElement;

    return (Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight) - subtractAmount).toString() + 'px'
  }

  ListResources = () => {
    if (!this.state.selectedVersion) {
      return <></>
    }
    let resourceIds = this.state.versions[this.state.selectedVersion]
    resourceIds.sort((a, b) => a.localeCompare(b))

    return <div>
      <ListGroup style={{ maxHeight: this.calculatePageHeight(130), overflow: `auto` }}>
        {resourceIds.map((resourceId) => {
          return <ListGroup.Item key={resourceId}><input type="checkbox" checked={this.state.prevResources.has(resourceId) || this.state.selectedResources.has(resourceId)} disabled={this.state.prevResources.has(resourceId)} onChange={this.handleSelectResource} id={resourceId} /> {resourceId}</ListGroup.Item>
        })}
      </ListGroup>
    </div>
  }

  saveResourcesAndVersion = () => {
    if (this.state.selectedResources.size === 0) {
      this.props.onCloseModal()
      return
    }
    const finalResources: Swagger = {
      module: this.state.selectedModule,
      version: this.state.selectedVersion,
      resources: []
    }
    this.state.selectedResources.forEach(resourceId => {
      finalResources.resources.push({id:resourceId})
    })
    console.log(finalResources)
    this.addSwagger(finalResources)
  }

  addSwagger = (requestBody: Swagger) => {
    axios.post(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/AddSwagger`, requestBody)
      .then(() => {
        axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz`)
          .then((res) => {
            // console.log(res.data)
            window.location.href = `/workspace/${this.props.params.workspaceName}`
          })

      })
      .catch((err) => console.log(err.response));
  }

  resetResourcesAndVersion = () => {
    this.props.onCloseModal()
  }

  DropdownButtonRow = () => {
    return (
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
        <Col lg="auto">
          <Button variant="secondary" onClick={this.saveResourcesAndVersion}>Save</Button>
          <> </>
          <Button variant="secondary" onClick={this.resetResourcesAndVersion}>Cancel</Button>
        </Col>
      </Row>
    )
  }

  render() {
    return <div className="m-1 p-1">
      <Modal show={true} backdrop="static" size='xl' >
        <Modal.Body >
          <this.DropdownButtonRow />
          <this.ListResources />
        </Modal.Body>
      </Modal>
    </div>
  }
}

const SpecSelectorWrapper = (props: any) => {
  const params = useParams()

  return <SpecSelector params={params} {...props} />
}

export { SpecSelectorWrapper as SpecSelector };