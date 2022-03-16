import React, { Component } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"
import { Row, Col, Navbar, Nav, Button, Alert, Modal } from "react-bootstrap"
import { SpecSelector } from "./SpecSelector";


import { Tree, NodeModel, DragLayerMonitorProps, DropOptions } from "@minoru/react-dnd-treeview";
import { CustomData } from "./TreeView/types";
import { CustomNode } from "./TreeView/CustomNode";
import { CustomDragPreview } from "./TreeView/CustomDragPreview";
import styles from "./TreeView/App.module.css";

import { CommandGroupDetails } from "./CommandGroupDetails"
import { ArgumentDetails } from "./ArgumentDetails"
import { couldStartTrivia } from "typescript";

type Argument = {
  options?: string[],
  type?: string,
  help?: { short: string },
  required?: boolean,
  idPart?: string,
  args?: Argument[],
  item?: {
    args: Argument[],
    type: string
  }
}

type ArgGroups = {
  args: Argument[],
  name: string
}[]

type Command = {
  help: { short: string },
  names: string[],
  resources: {
    id: string,
    version: string
  }[],
  version: string
}

type Commands = {
  [name: string]: Command
}

type CommandGroup = {
  commandGroups?: CommandGroups,
  commands?: Commands,
  names: string[],
  help?: HelpType,
  examples?: ExampleType[],
  argGroups?: ArgGroups,
  resources?: {
    id: string,
    version: string
  }[]
}

type CommandGroups = {
  [name: string]: CommandGroup
}

type NumberToString = {
  [index: number]: string
}

type StringToNumber = {
  [name: string]: number
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
  data: CustomData
}

type TreeDataType = TreeNode[]

type HelpType = {
  short: string,
  lines?: string[]
}

type ExampleType = {
  name: string,
  commands: string[]
}

type DeleteCommand = {
  active: boolean,
  originalCommand: string,
  affectedCommands: string[],
  urls: string[]
}

type ConfigEditorState = {
  commandGroups: CommandGroups,
  selectedIndex: number,
  initialTreeData: TreeDataType,
  treeData: TreeDataType,
  currentIndex: number,
  indexToCommandGroupName: NumberToString,
  nameToIndex: StringToNumber,
  indexToCommandGroup: NumberToCommandGroup,
  indexToTreeNode: NumberToTreeNode,
  showSpecSelectorModal: boolean,
  showGenerateAlert: boolean,
  showDeleteCommandGroupAlert: boolean,
  alertVariant: string,
  alertText: string
  resourceIdToCommands: { [id: string]: string[] }
  deletingCommand: DeleteCommand
}

type WrapperProp = {
  params: {
    workspaceName: string
  }
}

class ConfigEditor extends Component<WrapperProp, ConfigEditorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      commandGroups: {},
      selectedIndex: -1,
      initialTreeData: [],
      treeData: [],
      currentIndex: 0,
      indexToCommandGroupName: {},
      nameToIndex: {},
      indexToCommandGroup: {},
      indexToTreeNode: {},
      showSpecSelectorModal: false,
      showGenerateAlert: false,
      showDeleteCommandGroupAlert: false,
      alertVariant: "",
      alertText: "",
      resourceIdToCommands: {},
      deletingCommand: {
        active: false,
        originalCommand: "",
        affectedCommands: [],
        urls: []
      }
    }
  }

  parseCommandGroup = (depth: number, parentIndex: number, commandGroups?: CommandGroups) => {
    if (!commandGroups) {
      return Promise.resolve()
    }
    let totalPromise: Promise<any>[] = Object.keys(commandGroups).map(commandGroupName => {
      let namesJoined = commandGroups[commandGroupName].names.join('/')
      this.setState({ currentIndex: this.state.currentIndex + 1 })
      // console.log(this.state.currentIndex)
      this.state.indexToCommandGroupName[this.state.currentIndex] = namesJoined
      this.state.nameToIndex[namesJoined] = this.state.currentIndex
      this.state.indexToCommandGroup[this.state.currentIndex] = commandGroups[commandGroupName]

      let treeNode: TreeNode = {
        id: this.state.currentIndex,
        parent: parentIndex,
        text: commandGroupName,
        droppable: true,
        data: { hasChildren: true, type: 'CommandGroup', allowDelete: true }
      }
      // console.log(commandGroupName)
      this.state.initialTreeData.push(treeNode)
      this.state.indexToTreeNode[this.state.currentIndex] = treeNode

      let commandGroupIndex = this.state.currentIndex
      let commandGroupPromise: Promise<any> = this.parseCommandGroup(depth + 1, this.state.currentIndex, commandGroups[commandGroupName].commandGroups)
      let commands = commandGroups[commandGroupName].commands
      if (!commands) {
        return commandGroupPromise
      }

      let commandPromises = Object.keys(commands).map(commandName => {
        const names = commands![commandName].names
        let namesJoined = commands![commandName].names.join('/')
        this.setState({ currentIndex: this.state.currentIndex + 1 })
        // console.log(this.state.currentIndex)
        let treeNode: TreeNode = {
          id: this.state.currentIndex,
          parent: commandGroupIndex,
          text: commandName,
          droppable: false,
          data: { hasChildren: false, type: 'Command', allowDelete: true }
        }
        const resources = commands![commandName].resources
        resources.forEach(resource => {
          //           console.log(resource)
          const resourceId = btoa(resource.id)
          const version = btoa(resource.version)
          // console.log(resourceId, version)
          const combined = `${resourceId}/V/${version}`
          if (!(combined in this.state.resourceIdToCommands)) {
            this.state.resourceIdToCommands[combined] = []
          }
          this.state.resourceIdToCommands[combined].push(namesJoined)
        })
        const currentIndex = this.state.currentIndex
        this.state.indexToCommandGroupName[currentIndex] = namesJoined
        this.state.nameToIndex[namesJoined] = this.state.currentIndex
        this.state.initialTreeData.push(treeNode)
        this.state.indexToTreeNode[currentIndex] = treeNode
        return this.getCommand(currentIndex, names.slice(0, names.length - 1).join('/'), names[names.length - 1])
      })

      return Promise.all([commandGroupPromise, ...commandPromises])
    })
    return Promise.all(totalPromise)
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
        if (!commandGroups) {
          this.setState({ showSpecSelectorModal: true })
          return
        }
        this.setState({ commandGroups: commandGroups })
        let depth = 0
        return this.parseCommandGroup(depth, 0, commandGroups)
          .then(() => {
            this.setState({ treeData: this.state.initialTreeData })
            this.markHasChildren()
            // console.log(this.state)
            // console.log(this.state.resourceIdToCommands)
            
            return Promise.resolve()
          })
      })
      .catch((err) => console.log(err));
  }

  markHasChildren = () => {
    let hasChildren = new Set()
    this.state.treeData.forEach(node => {
      hasChildren.add(node.parent)
    })
    this.state.treeData.forEach(node => {
      node.data.hasChildren = hasChildren.has(node.id)
    })
  }

  componentDidMount() {
    this.getSwagger()
  }

  refreshAll = () => {
    this.setState({
      commandGroups: {},
      initialTreeData: [],
      treeData: [],
      currentIndex: 0,
      indexToCommandGroupName: {},
      nameToIndex: {},
      indexToCommandGroup: {},
      indexToTreeNode: {},
      resourceIdToCommands: {},
      deletingCommand: {
        active: false,
        originalCommand: "",
        affectedCommands: [],
        urls: []
      }
    })
  }

  handleNameChange = (id: NodeModel["id"], newName: string) => {
    let oldName = this.state.indexToCommandGroupName[Number(id)]
    const oldNameSplit = oldName.split('/')
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${oldName}/Rename`
    if (this.isCommand(id)) {
      const namesPath = oldNameSplit.slice(0, oldNameSplit.length - 1).join('/')
      const commandName = oldNameSplit[oldNameSplit.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}/Rename`
    }
    oldNameSplit[oldNameSplit.length - 1] = newName
    let newNameJoined = oldNameSplit.join(' ')

    // console.log(url)
    // console.log(newNameJoined)
    return axios.post(url, { name: newNameJoined })
      .then(res => {
        console.log(this.state.indexToCommandGroup[this.state.selectedIndex])
        this.refreshAll()
        return this.getSwagger()
      })
      .then(() => {
        // console.log(Object.keys(this.state.indexToCommandGroup).length)
        // console.log(this.state.selectedIndex, Number(id))
        // console.log(this.state.indexToCommandGroup[this.state.selectedIndex].names)
        this.setState({ selectedIndex: Number(id) })
      })
      .catch(err => {
        console.error(err.response)
      })
  }

  handleHelpChange = (id: NodeModel["id"], help: HelpType) => {
    id = Number(id)
    const namesJoined = this.state.indexToCommandGroupName[id]
    const names = namesJoined.split('/')

    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesJoined}`
    if (this.isCommand(id)) {
      const namesPath = names.slice(0, names.length - 1).join('/')
      const commandName = names[names.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}`
    }
    axios.patch(url, {
      help: help
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

  handleExampleChange = (id: NodeModel["id"], examples: ExampleType[]) => {
    id = Number(id)
    const namesJoined = this.state.indexToCommandGroupName[id]
    const names = namesJoined.split('/')

    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesJoined}`
    if (this.isCommand(id)) {
      const namesPath = names.slice(0, names.length - 1).join('/')
      const commandName = names[names.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}`
    }
    console.log(url)
    console.log(examples)
    axios.patch(url, {
      examples: examples
    })
      .then(res => {
        this.refreshAll()
        return this.getSwagger()
      })
      .then(() => {
        this.setState({ selectedIndex: Number(id) })
        // console.log(this.state.indexToCommandGroup[this.state.selectedIndex])
      })
      .catch(err => {
        console.error(err.response)
      })
  }

  isCommand = (id: NodeModel["id"]) => {
    const type = this.state.indexToTreeNode[Number(id)].data.type
    return type === 'Command'
  }

  handleDrop = (newTreeData: any, dropOptions: DropOptions) => {
    let { dragSourceId, dropTargetId } = dropOptions

    dragSourceId = Number(dragSourceId)
    dropTargetId = Number(dropTargetId)
    if (this.isCommand(dragSourceId) && dropTargetId === 0) {
      return
    }
    const sourceNamesJoined = this.state.indexToCommandGroupName[dragSourceId]
    const targetNamesJoined = this.state.indexToCommandGroupName[dropTargetId]
    // console.log(sourceNamesJoined)
    // console.log(targetNamesJoined)
    const sourceNames = sourceNamesJoined.split('/')
    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${sourceNamesJoined}/Rename`
    if (this.isCommand(dragSourceId)) {
      const namesPath = sourceNames.slice(0, sourceNames.length - 1).join('/')
      const commandName = sourceNames[sourceNames.length - 1]
      url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}/Rename`
    }
    let targetNames: string[] = [];
    if (targetNamesJoined) {
      targetNames = targetNamesJoined.split('/')
    }
    targetNames.push(sourceNames[sourceNames.length - 1])
    const newNameJoined = targetNames.join(' ')
    // console.log(url)
    // console.log(targetNames)

    return axios.post(url, { name: newNameJoined })
      .then(res => {
        this.refreshAll()
        return this.getSwagger()
      })
      .then(() => {
        // console.log(this.state)
        let newIndex = -1
        if (this.state.nameToIndex[targetNames.join('/')]) {
          newIndex = this.state.nameToIndex[targetNames.join('/')]
        }
        console.log(newIndex)
        this.setState({ selectedIndex: newIndex })
        this.markHasChildren()
        console.log(this.state)
      })
      .catch(err => {
        console.error(err.response)
      })
  }

  handleClick = (id: NodeModel["id"]) => {
    id = Number(id)
    // console.log(this.state.indexToCommandGroupName[id])
    this.setState({ selectedIndex: id })
    // console.log(this.state.selectedIndex)
    // console.log(this.state.indexToCommandGroup[this.state.selectedIndex])
  }

  handleDelete = (id: NodeModel["id"]) => {
    id = Number(id)
    // console.log(this.state.indexToTreeNode[id])
    // console.log(this.state.indexToCommandGroupName[id])
    const namesJoined = this.state.indexToCommandGroupName[id]


    let url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/CommandTree/Nodes/aaz/${namesJoined}`
    let urls: string[] = []
    if (this.isCommand(id)) {
      const command = this.state.indexToCommandGroup[id]
      // console.log(command.resources)
      const affectedCommands: string[] = []
      command.resources?.forEach(resource => {
        const resourceId = btoa(resource.id)
        const version = btoa(resource.version)
        url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/Resources/${resourceId}/V/${version}`
        const curr_commands = this.state.resourceIdToCommands[`${resourceId}/V/${version}`]
        if (curr_commands) {
          affectedCommands.push(...curr_commands)
        }
        urls.push(url)
      })
      this.setState({
        deletingCommand: {
          active: true,
          originalCommand: this.state.indexToCommandGroupName[id],
          affectedCommands: affectedCommands,
          urls: urls
        }
      })
    } else {
      // console.log(this.state.indexToTreeNode[id])
      if (this.state.indexToTreeNode[id].data.hasChildren) {
        this.setState({ showDeleteCommandGroupAlert: true })
        window.setTimeout(() => {
          this.setState({ showDeleteCommandGroupAlert: false })
        }, 2000)
      } else {
        urls.push(url)
        this.confirmDelete(urls)
      }
    }
  }

  confirmDelete = (urls: string[]) => {
    const promisesAll = urls.map(url => {
      console.log(url)
      return axios.delete(url)
    })
    Promise.all(promisesAll)
      .then(res => {
        // console.log(res)
        if (res[0].status !== 200) {
          this.state.deletingCommand.active = false
        } else {
          this.refreshAll()
          return this.getSwagger()
            .then(() => {
              this.setState({ selectedIndex: -1 })
              this.markHasChildren()
            })
        }

      })
      .catch(err => {
        console.error(err.response)
      })
  }

  cancelDelete = () => {
    this.setState({
      deletingCommand: {
        active: false,
        originalCommand: "",
        affectedCommands: [],
        urls: []
      }
    })
  }

  ConfirmDeletionModal = () => {
    const { active, originalCommand, affectedCommands, urls } = this.state.deletingCommand
    return <Modal show={active} centered>
      <Modal.Header>
        Deleting {originalCommand}
      </Modal.Header>
      <Modal.Body>
        This will delete {affectedCommands.join(', ')}
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={() => { this.confirmDelete(urls) }}>Confirm</Button>
        <Button onClick={this.cancelDelete}>Cancel</Button>
      </Modal.Footer>
    </Modal>
  }


  displayCommandGroupsTree = () => {
    // console.log(this.state.treeData)
    return <div className={styles.app}>
      <Tree
        tree={this.state.treeData}
        rootId={0}
        render={(node: NodeModel<CustomData>, { depth, isOpen, onToggle }) => (
          <CustomNode node={node} depth={depth} isOpen={isOpen} isSelected={node.id === this.state.selectedIndex} onToggle={onToggle} onClick={this.handleClick} onSubmit={this.handleNameChange} editable={true} onDelete={this.handleDelete} />
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
        initialOpen={true}
      />
    </div>
  }

  displayCommandDetail = () => {
    // console.log(this.state.selectedIndex)
    // console.log(this.state.indexToCommandGroup)
    // console.log(this.state.indexToCommandGroup[this.state.selectedIndex])
    if (this.state.selectedIndex !== -1 && this.state.indexToCommandGroup[this.state.selectedIndex]) {
      return <CommandGroupDetails commandGroup={this.state.indexToCommandGroup[this.state.selectedIndex]} id={this.state.selectedIndex} onHelpChange={this.handleHelpChange} onExampleChange={this.handleExampleChange} isCommand={this.isCommand(this.state.selectedIndex)} />
    }
    return <div></div>
  }

  handleArgumentNameChange = () => {

  }

  displayArgumentDetail = () => {
    if (!this.state.indexToCommandGroup[this.state.selectedIndex]) {
      return <div />
    }
    let argGroups = this.state.indexToCommandGroup[this.state.selectedIndex].argGroups
    return argGroups
      ?
      <ArgumentDetails argGroups={this.state.indexToCommandGroup[this.state.selectedIndex].argGroups!} id={this.state.selectedIndex} onNameChange={this.handleArgumentNameChange} />
      :
      <></>
  }

  handleCloseModal = () => {
    this.setState({ showSpecSelectorModal: false })
  }

  handleGenerate = () => {
    const url = `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}/Generate`
    axios.post(url)
      .then(res => {
        this.setState({ showGenerateAlert: true, alertText: "Successfully generated configuration.", alertVariant: "success" })
        window.setTimeout(() => {
          this.setState({ showGenerateAlert: false })
        }, 2000)
      })
      .catch(err => {
        console.error(err.response)
        this.setState({ showGenerateAlert: true, alertText: "Need to complete all the short help fields", alertVariant: "danger" })
        window.setTimeout(() => {
          this.setState({ showGenerateAlert: false })
        }, 2000)
      })
  }

  render() {
    return <div className="m-1 p-1">
      <Navbar bg="dark" variant="dark">
        <Navbar.Brand href={window.location.href} >Workspace: {this.props.params.workspaceName}</Navbar.Brand>
        <Button variant='dark' onClick={() => { this.setState({ showSpecSelectorModal: true }) }}>
          Add Swagger
        </Button>
        <Button variant='dark' onClick={this.handleGenerate}>
          Generate Configuration
        </Button>
        <Nav className="me-auto" />
      </Navbar>
      {this.state.showGenerateAlert && <Alert variant={this.state.alertVariant} onClose={() => this.setState({ showGenerateAlert: false })}>
        {this.state.alertText}
      </Alert>}
      {this.state.showDeleteCommandGroupAlert && <Alert variant="danger" onClose={() => this.setState({ showDeleteCommandGroupAlert: false })}>
        "You can only delete an empty command group!"
      </Alert>}
      <Row>
        <Col xxl="3" style={{ overflow: `auto` }}>
          {this.state.treeData && this.state.treeData.length > 0 && <this.displayCommandGroupsTree />}
        </Col>
        <Col xxl="9">
          <this.displayCommandDetail />
          <this.displayArgumentDetail />
        </Col>
      </Row>


      {this.state.showSpecSelectorModal ? <SpecSelector onCloseModal={this.handleCloseModal} /> : <></>}
      <this.ConfirmDeletionModal />
    </div>
  }
}

const ConfigEditorWrapper = (props: any) => {
  const params = useParams()

  return <ConfigEditor params={params} {...props} />
}

export { ConfigEditorWrapper as ConfigEditor };

export type { CommandGroup, HelpType, ExampleType, ArgGroups, TreeDataType, TreeNode, Argument };