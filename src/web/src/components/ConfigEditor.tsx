import React, { Component } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { Row, Col, Navbar, Nav, Container, ListGroup } from "react-bootstrap"
import { isThisTypeNode, Set } from "typescript";
import type { WrapperProp } from "./SpecSelector"
import { List } from "reactstrap";

type Command = {
  help: { short: string },
  names: string[],
  resources: {},
  version: string
}

type Commands = {
  [name: string]: Command
}

type CommandGroup = {
  commandGroups?: CommandGroups,
  commands?: Commands,
  names: string[]
}

type CommandGroups = {
  [name: string]: CommandGroup
}

type DepthMap = {
  [name: string]: number
}

type DepthToName = {
  [depth: number]: string
}

type NameMap = {
  [name: string]: CommandGroups
}

type ConfigEditorState = {
  commandGroups: CommandGroups,
  commandGroupNameToDepth: DepthMap,
  commandGroupNameToChildren: NameMap,
  commandNameToDepth: DepthMap,
  selectedCommandGroupName: string,
  selectedCommandGroupNameForDepth: DepthToName,
  nameToCommandGroup: CommandGroups,
  currentNode: string,
  maxDepth: number
}

class ConfigEditor extends Component<WrapperProp, ConfigEditorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      commandGroups: {},
      commandGroupNameToDepth: {},
      commandGroupNameToChildren: {},
      commandNameToDepth: {},
      selectedCommandGroupName: "",
      selectedCommandGroupNameForDepth: {},
      nameToCommandGroup: {},
      currentNode: "",
      maxDepth: 0
    }
  }

  parseCommandGroup = (depth: number, parentName: string, commandGroups?: CommandGroups) => {
    if (!commandGroups) {
      return
    }
    this.state.commandGroupNameToChildren[parentName] = commandGroups
    this.setState({ maxDepth: Math.max(depth, this.state.maxDepth) })
    Object.keys(commandGroups).map(commandGroupName => {
      let namesJoined = commandGroups[commandGroupName].names.join('/')
      this.state.commandGroupNameToDepth[namesJoined] = depth
      this.state.nameToCommandGroup[namesJoined] = commandGroups[commandGroupName]
      this.parseCommandGroup(depth + 1, namesJoined, commandGroups[commandGroupName].commandGroups)
      let commands = commandGroups[commandGroupName].commands
      if (!commands) {
        return
      }
      Object.values(commands).map(command => {
        let namesJoined = command.names.join('/')
        this.state.commandNameToDepth[namesJoined] = depth
      })
    })
    console.log(this.state)

  }

  getSwagger = () => {
    let module = "";
    let resourceProvider = "";
    let version = "";
    let resources = new Set<string>();
    axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}`)
      .then(res => {
        let commandGroups: CommandGroups = res.data.commandTree.commandGroups
        this.setState({ commandGroups: commandGroups })
        let depth = 0
        this.parseCommandGroup(depth, 'aaz', commandGroups)
        console.log(this.state)
      })
      .catch((err) => console.log(err));
  }

  componentDidMount() {
    this.getSwagger()
  }

  handleSelectCommandGroup = (eventKey: any) => {
    // console.log(eventKey)
    // console.log(this.state.nameToCommandGroup[eventKey])
    if (this.state.selectedCommandGroupName === eventKey) {
      return
    }
    this.setState({ selectedCommandGroupName: eventKey })
    let depth = this.state.commandGroupNameToDepth[eventKey]

    this.state.selectedCommandGroupNameForDepth[depth] = eventKey
    while (++depth <= this.state.maxDepth) {
      this.state.selectedCommandGroupNameForDepth[depth] = ""
    }
    this.forceUpdate()
    // console.log(this.state.selectedCommandGroupNameForDepth)
  }

  displayCommandGroupForDepth = (depth: number) => {
    let commandGroups: CommandGroups = {}
    // console.log(depth,this.state.selectedCommandGroupNameForDepth)
    if (depth == 0) {
      commandGroups = this.state.commandGroups
    } else {
      let selectedParent = this.state.selectedCommandGroupNameForDepth[depth - 1]
      // console.log(selectedParent)
      if (!selectedParent) {
        return <Col key={depth} lg="auto"></Col>
      }
      commandGroups = this.state.commandGroupNameToChildren[selectedParent]
    }
    if (!commandGroups) {
      return <Col key={depth} lg="auto"></Col>
    }
    return <Col key={depth} lg="auto">
      <ListGroup onSelect={this.handleSelectCommandGroup}>
        {Object.keys(commandGroups).map(commandGroupName => {
          let namesJoined = commandGroups[commandGroupName].names.join('/')
          return <ListGroup.Item action active={this.state.selectedCommandGroupNameForDepth[depth] === namesJoined} eventKey={namesJoined} key={namesJoined}>{commandGroupName}</ListGroup.Item>
        })}
      </ListGroup>
    </Col>

  }

  displayCommandGroups = (commandGroups: CommandGroups) => {
    let list = []
    for (let i = 0; i <= this.state.maxDepth; i++) {
      list.push(i)
    }
    return <Row className='g-1'>
      {list.map((depth) => {
        return this.displayCommandGroupForDepth(depth)
      })}
      {/* {this.displayCommandGroupForDepth(1)} */}
    </Row>


  }

  displayCommandDetail = () => {
    let namesJoined = this.state.selectedCommandGroupName
    if (!namesJoined) {
      return <div></div>
    }
    let name = namesJoined.split('/').pop()
    let commands = this.state.nameToCommandGroup[namesJoined].commands
    let commandsSection;
    if (!commands) {
      commandsSection = <div></div>
    } else {
      commandsSection = <div>
        <p>Commands: </p>
        <ListGroup>
          {commands && Object.keys(commands).map(commandName => {
            let namesJoined = commands![commandName].names.join('/')
            return <ListGroup.Item eventKey={namesJoined} key={namesJoined}>
              <ListGroup>
                <ListGroup.Item>{commandName}</ListGroup.Item>
                <ListGroup.Item>Help: {commands![commandName].help.short}</ListGroup.Item>
              </ListGroup>
            </ListGroup.Item>
          })}
        </ListGroup>
      </div>
    }

    return <div>
      <p>Name: {name}</p>
      {commandsSection}
    </div>
  }

  render() {
    return <div className="m-1 p-1">
      <Navbar bg="primary" variant="dark">
        <Container>
          <Navbar.Brand href="editor">Editor</Navbar.Brand>
          <Navbar.Brand href="resourceSelection">Resource Selection</Navbar.Brand>
          <Nav className="me-auto">
          </Nav>
        </Container>
      </Navbar>
      <Row>
        <Col lg='11'>
          <h1>
            Workspace Name: {this.props.params.workspaceName}
          </h1>
        </Col>
      </Row>
      <Row>
        <Col lg="auto">
          {/* {this.displayCommandGroups(this.state.commandGroups)} */}
          
        </Col>
        <Col>
          <this.displayCommandDetail />
        </Col>

      </Row>

    </div>
  }
}

const ConfigEditorWrapper = (props: any) => {
  const params = useParams()

  return <ConfigEditor params={params} {...props} />
}

export { ConfigEditorWrapper as ConfigEditor };