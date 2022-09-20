import * as React from "react";
import { NodeModel, Tree } from "@minoru/react-dnd-treeview";
import { CheckData } from "../../components/TreeView/types";
import { CheckNode } from "../../components/TreeView/CheckNode";
import styles from "../../components/TreeView/App.module.css";

interface GenerationCommandTreeProps {
  treeData: NodeModel<CheckData>[];
  selectedNodes: NodeModel<CheckData>[];
  onSelect: (node: NodeModel<CheckData>) => void;
  onChange: (node: NodeModel<CheckData>, version: string) => void;
}

class GenerationCommandTree extends React.Component<GenerationCommandTreeProps> {
  render() {
    const { treeData, selectedNodes, onSelect, onChange } = this.props;
    return (
      <Tree
        tree={treeData}
        rootId={0}
        render={(node: NodeModel<CheckData>, { depth, isOpen, onToggle }) => (
          <CheckNode
            node={node}
            depth={depth}
            isOpen={isOpen}
            isSelected={!!selectedNodes.find((n) => n.id === node.id)}
            onToggle={onToggle}
            onSelect={onSelect}
            onChange={onChange}
          />
        )}
        onDrop={() => {}}
        classes={{
          root: styles.treeRoot,
          dropTarget: styles.dropTarget,
        }}
        initialOpen={true}
      />
    );
  }
}

export default GenerationCommandTree;
