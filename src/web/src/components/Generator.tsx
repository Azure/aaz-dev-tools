import React, {Component} from "react";
import {Navbar, Nav, Container, Button} from "react-bootstrap"
import {useParams} from "react-router-dom";
import axios from "axios";
import styles from "./TreeView/App.module.css";
import {DragLayerMonitorProps, DropOptions, NodeModel, Tree} from "@minoru/react-dnd-treeview";
import {CustomData} from "./TreeView/types";
import {CustomNode} from "./TreeView/CustomNode";
import {CustomDragPreview} from "./TreeView/CustomDragPreview";
import {TreeDataType} from "./ConfigEditor";

import SampleData from "./tree.json";


type GeneratorState = {
  moduleName: string,
  profiles: string[],
  currProfile: string,
  treeData: TreeDataType,
  selectedIdx: number
}


class Generator extends Component<any, GeneratorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      moduleName: this.props.params.moduleName,
      profiles: [],
      currProfile: "",
      treeData: SampleData,
      selectedIdx: -1
    }
  }

  componentDidMount() {
    axios.get("/CLI/Az/Profiles")
        .then(res => {this.setState({profiles: res.data})})
  }

  displayNavbar = () => {
    const handleClick = (event: any) => {
      const profileName = event.target.text
      this.setState({currProfile: profileName})
    }

    return (
      <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
        <Container>
          <Navbar.Brand>{this.state.moduleName}</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">{
              this.state.profiles.map((profile: string) => {
                return <Nav.Link href={`#${profile}`} onClick={handleClick}>{profile}</Nav.Link>
              })
            }
            </Nav>
            <Button>
              Generate
            </Button>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    )
  }

  displayCommandTree = () => {
    const handleClick = (id: NodeModel["id"]) => {
      id = Number(id)
      this.setState({ selectedIdx: id })
    }

    const handleNameChange = (id: NodeModel["id"], newName: string) => {}

    const handleDrop = (newTreeData: any, dropOptions: DropOptions) => {}

    return <div className={styles.app}>
      <Tree
        tree={this.state.treeData}
        rootId={0}
        render={(node: NodeModel<CustomData>, { depth, isOpen, onToggle }) => (
            <CustomNode node={node} depth={depth} isOpen={isOpen} isSelected={node.id === this.state.selectedIdx} onToggle={onToggle} onClick={handleClick} onSubmit={handleNameChange} editable={true}/>
        )}
        dragPreviewRender={(
            monitorProps: DragLayerMonitorProps<CustomData>
        ) => <CustomDragPreview monitorProps={monitorProps} />}
        onDrop={handleDrop}
        classes={{
          root: styles.treeRoot,
          draggingSource: styles.draggingSource,
          dropTarget: styles.dropTarget,
        }}
      />
    </div>
  }

  render() {
    return (
      <div>
        <this.displayNavbar/>
        <this.displayCommandTree/>
      </div>
    )
  }
}

const GeneratorWrapper = (props: any) => {
  const params = useParams()
  return <Generator params={params} {...props}/>
}

export {GeneratorWrapper as Generator};
