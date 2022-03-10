import React, {Component, useState} from "react";
import {Navbar, Nav, Container, Button} from "react-bootstrap"
import {useParams} from "react-router-dom";
import axios from "axios";
import styles from "./TreeView/App.module.css";
import {DragLayerMonitorProps, DropOptions, NodeModel, Tree} from "@minoru/react-dnd-treeview";
import {CheckData} from "./TreeView/types";
import {CheckNode} from "./TreeView/CheckNode";
import {CustomDragPreview} from "./TreeView/CustomDragPreview";

import SampleData from "./tree.json";


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


type GeneratorState = {
  currRepo: string,
  moduleName: string,
  profiles: string[],
  currProfile: string,
  treeData: TreeNode[],
  selectedIdx: number
}


class Generator extends Component<any, GeneratorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      currRepo: this.props.params.currRepo,
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
    if (this.state.currRepo === "Azure CLI") {
      axios.get(`/CLI/Az/Main/Modules/${this.state.moduleName}`)
        .then(res => {
          console.log(`/CLI/Az/Main/Modules/${this.state.moduleName}`)
        })
    }

    const handleDrop = (newTree: NodeModel[]) => {};
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [selectedNodes, setSelectedNodes] = useState<NodeModel[]>([]);

    const handleSelect = (node: NodeModel) => {
      const item = selectedNodes.find((n) => n.id === node.id);

      if (!item) {
        setSelectedNodes([...selectedNodes, node]);
      } else {
        setSelectedNodes(selectedNodes.filter((n) => n.id !== node.id));
      }
    };

    const handleClear = (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        setSelectedNodes([]);
      }
    };

    return <div className={styles.app}>
      <Tree
        tree={this.state.treeData}
        rootId={0}
        render={(node: NodeModel<CheckData>, {depth, isOpen, onToggle}) => (
          <CheckNode
            node={node}
            depth={depth}
            isOpen={isOpen}
            isSelected={!!selectedNodes.find((n) => n.id === node.id)}
            onToggle={onToggle}
            onSelect={handleSelect}
          />
        )}
        dragPreviewRender={(monitorProps: DragLayerMonitorProps<CheckData>) => (
          <CustomDragPreview monitorProps={monitorProps}/>
        )}
        onDrop={handleDrop}
        classes={{
          root: styles.treeRoot,
          draggingSource: styles.draggingSource,
          dropTarget: styles.dropTarget,
        }}
        rootProps={{
          onClick: handleClear
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
