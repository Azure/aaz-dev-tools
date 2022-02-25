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

type Argument = {
  idPart: string,
  help?: { short: string },
  options: string[],
  required: boolean,
  type: string
}

type Args = Argument[]

type Command = {
  argGroups?: Args[],
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
  names: string[],
  help?: { short: string }
}

type CommandGroups = {
  [name: string]: CommandGroup
}

type NumberToString = {
  [index: number]: string
}

type NumberToTreeNode = {
  [index: number]: TreeNode
}

type NumberToCommandGroup = {
  [index: number]: CommandGroup
}


type TreeNode = {
  id: number,
  parent: number,
  droppable: boolean,
  text: string,
  data: {
    hasChildren: boolean,
    type: string
  }
}

type TreeDataType = TreeNode[]

type ConfigEditorState = {
  commandGroups: CommandGroups,
  selectedIndex: number,
  treeData: TreeDataType,
  currentIndex: number,
  indexToCommandGroupName: NumberToString,
  indexToCommandGroup: NumberToCommandGroup,
  indexToTreeNode: NumberToTreeNode,
}

class ConfigEditor extends Component<WrapperProp, ConfigEditorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      commandGroups: {},
      selectedIndex: -1,
      treeData: [],
      currentIndex: 0,
      indexToCommandGroupName: {},
      indexToCommandGroup: {},
      indexToTreeNode: {}
    }
  }

  parseCommandGroup = (depth: number, parentName: string, parentIndex: number, commandGroups?: CommandGroups) => {
    if (!commandGroups) {
      return Promise.resolve()
    }
    let totalPromise:Promise<any>[] = Object.keys(commandGroups).map(commandGroupName => {
      let namesJoined = commandGroups[commandGroupName].names.join('/')
      this.setState({ currentIndex: this.state.currentIndex + 1 })
      this.state.indexToCommandGroupName[this.state.currentIndex] = namesJoined
      this.state.indexToCommandGroup[this.state.currentIndex] = commandGroups[commandGroupName]

      let treeNode: TreeNode = {
        id: this.state.currentIndex,
        parent: parentIndex,
        text: commandGroupName,
        droppable: true,
        data: { hasChildren: true, type: 'CommandGroup' }
      }
      this.state.treeData.push(treeNode)
      this.state.indexToTreeNode[this.state.currentIndex] = treeNode

      let commandGroupIndex = this.state.currentIndex
      let commandGroupPromise: Promise<any> = this.parseCommandGroup(depth + 1, namesJoined, this.state.currentIndex, commandGroups[commandGroupName].commandGroups)
      let commands = commandGroups[commandGroupName].commands
      if (!commands) {
        return commandGroupPromise
      }

      let commandPromises = Object.keys(commands).map(commandName => {
        if (!commands)
          return Promise.resolve()
        const names = commands[commandName].names
        let namesJoined = commands[commandName].names.join('/')
        this.setState({ currentIndex: this.state.currentIndex + 1 })
        let treeNode: TreeNode = {
          id: this.state.currentIndex,
          parent: commandGroupIndex,
          text: commandName,
          droppable: false,
          data: { hasChildren: false, type: 'Command' }
        }
        const currentIndex = this.state.currentIndex
        this.state.indexToCommandGroupName[currentIndex] = namesJoined
        this.state.treeData.push(treeNode)
        this.state.indexToTreeNode[currentIndex] = treeNode
        return this.getCommand(currentIndex, names.slice(0, names.length - 1).join('/'), names[names.length - 1])
      })

      return Promise.all([commandGroupPromise,commandPromises])
    })
    this.markHasChildren()
    return Promise.all([totalPromise])
  }

  getCommand = (currentIndex: number, namesPath: string, commandName: string) => {
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}`
    // console.log(url)
    return axios.get(url)
      .then(res => {
        const command = res.data
        this.state.indexToCommandGroup[currentIndex] = command
        return res.data
      })
      .catch((err) => console.log(err));
  }

  getSwagger = () => {
    return axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}`)
      .then(res => {
        // console.log(res.data)
        let commandGroups: CommandGroups = res.data.commandTree.commandGroups
        this.setState({ commandGroups: commandGroups })
        let depth = 0
        this.parseCommandGroup(depth, 'aaz', 0, commandGroups)
        console.log(this.state)
      })
      .catch((err) => console.log(err));
  }

  componentDidMount() {
    this.getSwagger()
  }

  refreshAll = () => {
    this.setState({
      commandGroups: {},
      selectedIndex: -1,
      treeData: [],
      currentIndex: 0,
      indexToCommandGroupName: {},
      indexToCommandGroup: {},
      indexToTreeNode: {}
    })
  }

  handleNameChange = (id: NodeModel["id"], newName: string) => {
    let oldName = this.state.indexToCommandGroupName[Number(id)]
    const oldNameSplit = oldName.split('/')
    const type = this.state.indexToTreeNode[Number(id)].data.type
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${oldName}/Rename`
    if (type === 'Command') {
      const namesPath = oldNameSplit.slice(0, oldNameSplit.length - 1).join('/')
      const commandName = oldNameSplit[oldNameSplit.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}/Rename`
    }
    oldNameSplit[oldNameSplit.length - 1] = newName
    let newNameJoined = oldNameSplit.join(' ')

    console.log(url)
    console.log(newNameJoined)
    axios.post(url, { name: newNameJoined })
      .then(res => {
        this.refreshAll()
        return this.getSwagger()
      })
      .then(() => {
        this.setState({ selectedIndex: Number(id) })
      })
      .catch(err => {
        console.error(err.response)
      })
  }

  handleShortHelpChange = (id: NodeModel["id"], help: string) => {
    id = Number(id)
    const namesJoined = this.state.indexToCommandGroupName[id]
    const names = namesJoined.split('/')

    const type = this.state.indexToTreeNode[id].data.type

    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesJoined}`
    if (type === 'Command') {
      const namesPath = names.slice(0, names.length - 1).join('/')
      const commandName = names[names.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}`
    }
    // console.log(url)
    // console.log(help)
    axios.patch(url, {
      help: {
        short: help
      }
    })
      .then(res => {
        this.refreshAll()
        return this.getSwagger()
      })
      .then(() => {
        this.setState({ selectedIndex: Number(id) })
      })
      .catch(err => {
        console.error(err.response)
      })
  }


  displayCommandDetail = () => {
    // console.log(this.state.selectedIndex)
    // console.log(this.state.indexToCommandGroup)
    // console.log(this.state.indexToCommandGroup[this.state.selectedIndex])
    if (this.state.selectedIndex!==-1 && this.state.indexToCommandGroup[this.state.selectedIndex]) {
      return <CommandGroupDetails commandGroup={this.state.indexToCommandGroup[this.state.selectedIndex]} id={this.state.selectedIndex} onHelpChange={this.handleShortHelpChange} />
    }
    return <div></div>
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
    let {dragSourceId, dropTargetId} = dropOptions

    dragSourceId = Number(dragSourceId)
    dropTargetId = Number(dropTargetId)
    const type = this.state.indexToTreeNode[dragSourceId].data.type
    const sourceNamesJoined = this.state.indexToCommandGroupName[dragSourceId]
    const targetNamesJoined = this.state.indexToCommandGroupName[dropTargetId]
    const sourceNames = sourceNamesJoined.split('/')
    let targetNames = targetNamesJoined.split('/')
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${sourceNamesJoined}/Rename`
    if (type==='Command'){
      const namesPath = sourceNames.slice(0, sourceNames.length - 1).join('/')
      const commandName = sourceNames[sourceNames.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}/Rename`
    }
    targetNames.push(sourceNames[sourceNames.length-1])
    let newNameJoined = targetNames.join(' ')

    // console.log(url)
    // console.log(newNameJoined)

    axios.post(url, { name: newNameJoined })
      .then(res => {
        this.refreshAll()
        return this.getSwagger()
      })
      .then(() => {
        // console.log(this.state)
        this.setState({ selectedIndex: Number(dragSourceId) })
        // console.log(this.state.selectedIndex)
      })
      .catch(err => {
        console.error(err.response)
      })

    // this.setState({ treeData: newTreeData })
    // this.markHasChildren()

  }

  handleClick = (id: NodeModel["id"]) => {
    id = Number(id)
    // console.log(this.state.indexToCommandGroupName[id])
    this.setState({ selectedIndex: id })
  }

  displayCommandGroupsTree = () => {
    return <div className={styles.app}>
      <Tree
        tree={this.state.treeData}
        rootId={0}
        render={(node: NodeModel<CustomData>, { depth, isOpen, onToggle }) => (
          <CustomNode node={node} depth={depth} isOpen={isOpen} onToggle={onToggle} onClick={this.handleClick} onSubmit={this.handleNameChange} />
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