import React, { Component, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { Row, Col, Navbar, Nav, Container, ListGroup } from "react-bootstrap"
import type { WrapperProp } from "./SpecSelector"
import { Set } from "typescript";


import { Tree, NodeModel, DragLayerMonitorProps, DropOptions } from "@minoru/react-dnd-treeview";
import { CustomData } from "./TreeView/types";
import { CustomNode } from "./TreeView/CustomNode";
import { CustomDragPreview } from "./TreeView/CustomDragPreview";
import styles from "./TreeView/App.module.css";

import { CommandGroupDetails } from "./CommandGroupDetails"

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

type NumberMap = {
  [depth: number]: string
}

type NameMap = {
  [name: string]: CommandGroups
}

type treeNode = {
  id: number,
  parent: number,
  droppable: boolean,
  text: string,
  data: {
    hasChildren: boolean
  }
}

type treeDataType = treeNode[]

type ConfigEditorState = {
  commandGroups: CommandGroups,
  commandGroupNameToDepth: DepthMap,
  commandGroupNameToChildren: NameMap,
  commandNameToDepth: DepthMap,
  selectedCommandGroupName: string,
  nameToCommandGroup: CommandGroups,
  maxDepth: number,
  treeData: treeDataType,
  currentIndex: number,
  indexToCommandGroupName: NumberMap
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
      nameToCommandGroup: {},
      maxDepth: 0,
      treeData: [],
      currentIndex: 0,
      indexToCommandGroupName: {}
    }
  }

  parseCommandGroup = (depth: number, parentName: string, parentIndex: number, commandGroups?: CommandGroups) => {
    if (!commandGroups) {
      return
    }

    this.state.commandGroupNameToChildren[parentName] = commandGroups
    this.setState({ maxDepth: Math.max(depth, this.state.maxDepth) })
    Object.keys(commandGroups).map(commandGroupName => {
      let namesJoined = commandGroups[commandGroupName].names.join('/')
      this.state.commandGroupNameToDepth[namesJoined] = depth
      this.state.nameToCommandGroup[namesJoined] = commandGroups[commandGroupName]
      this.setState({ currentIndex: this.state.currentIndex + 1 })
      this.state.indexToCommandGroupName[this.state.currentIndex] = namesJoined

      let treeNode: treeNode = {
        id: this.state.currentIndex,
        parent: parentIndex,
        text: commandGroupName,
        droppable: true,
        data: { hasChildren: true }
      }
      this.state.treeData.push(treeNode)

      this.parseCommandGroup(depth + 1, namesJoined, this.state.currentIndex, commandGroups[commandGroupName].commandGroups)
      let commands = commandGroups[commandGroupName].commands
      if (!commands) {
        return
      }
      Object.values(commands).map(command => {
        let namesJoined = command.names.join('/')
        this.state.commandNameToDepth[namesJoined] = depth
      })
    })
    this.markHasChildren()

  }

  getSwagger = () => {
    let module = "";
    let resourceProvider = "";
    let version = "";
    let resources = new Set<string>();
    return axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}`)
      .then(res => {
        // console.log(res.data)
        let commandGroups: CommandGroups = res.data.commandTree.commandGroups
        this.setState({ commandGroups: commandGroups })
        let depth = 0
        this.parseCommandGroup(depth, 'aaz', 0, commandGroups)
      })
      .catch((err) => console.log(err));
  }

  componentDidMount() {
    this.getSwagger()
  }

  refreshAll = () => {
    this.setState({
      commandGroups: {},
      commandGroupNameToDepth: {},
      commandGroupNameToChildren: {},
      commandNameToDepth: {},
      selectedCommandGroupName: "",
      nameToCommandGroup: {},
      maxDepth: 0,
      treeData: [],
      currentIndex: 0,
      indexToCommandGroupName: {}
    })
  }

  handleNameChange = (id: NodeModel["id"], newName: string) => {
    let oldName = this.state.indexToCommandGroupName[Number(id)]
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${oldName}/Rename`
    let oldNameSplit = oldName.split('/')
    oldNameSplit[oldNameSplit.length-1] = newName
    let newNameJoined = oldNameSplit.join(' ')

    axios.post(url, {name:newNameJoined})
      .then(res => {
        this.refreshAll()
        return this.getSwagger()
      })
      .then(()=>{
        this.setState({selectedCommandGroupName: newNameJoined.split(' ').join('/')})
      })
      .catch(err => {
        console.error(err.response)
      })
  }

  handleHelpChange = (name: string, help: string) => {
    name = name.split(' ').join('/')
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${name}/Rename`
    // console.log(url)
    // console.log(newName)
    axios.post(url, {help:help})
      .then(res => {
        console.log(res)
        window.location.reload();
      })
      .catch(err => {
        console.error(err.response)
      })
  }


  displayCommandDetail = () => {
    if (!this.state.selectedCommandGroupName) {
      return <div></div>
    }
    return <CommandGroupDetails commandGroup={this.state.nameToCommandGroup[this.state.selectedCommandGroupName]} onNameChange={this.handleNameChange} onHelpChange={this.handleHelpChange}/>
  }

  markHasChildren = () => {
    let hasChildren = new Set()
    this.state.treeData.map(node => {
      hasChildren.add(node.parent)
    })
    this.state.treeData.map(node => {
      node.data.hasChildren = hasChildren.has(node.id)
    })
  }

  handleDrop = (newTreeData: any, dropOptions: DropOptions) => {
    // console.log(dropOptions.dragSourceId, dropOptions.dropTargetId)
    let index = Number(dropOptions.dragSourceId)

    let namesJoined = this.state.indexToCommandGroupName[index]

    // let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesJoined}`
    // console.log(url)

    this.setState({ treeData: newTreeData })
    this.markHasChildren()
  }

  handleClick = (id: NodeModel["id"]) => {
    id = Number(id)
    // console.log(this.state.indexToCommandGroupName[id])
    this.setState({ selectedCommandGroupName: this.state.indexToCommandGroupName[id] })
  }

  displayCommandGroupsTree = () => {
    return <div className={styles.app}>
      <Tree
        tree={this.state.treeData}
        rootId={0}
        render={(node: NodeModel<CustomData>, { depth, isOpen, onToggle }) => (
          <CustomNode node={node} depth={depth} isOpen={isOpen} onToggle={onToggle} onClick={this.handleClick} onSubmit={this.handleNameChange}/>
        )}
        dragPreviewRender={(
          monitorProps: DragLayerMonitorProps<CustomData>
        ) => <CustomDragPreview monitorProps={monitorProps} />}
        onDrop={this.handleDrop}
        classes={{
          root: styles.treeRoot,
          draggingSource: styles.draggingSource,
          dropTarget: styles.dropTarget,
        }}
      />
    </div>
  }

  render() {
    return <div className="m-1 p-1">
      <Navbar bg="dark" variant="dark">
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
          <this.displayCommandGroupsTree />
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

export type { CommandGroup as CommandGroup };