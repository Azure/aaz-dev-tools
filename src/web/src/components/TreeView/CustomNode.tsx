import React from "react";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import { NodeModel, useDragOver } from "@minoru/react-dnd-treeview";
import { CustomData } from "./types";
import { TypeIcon } from "./TypeIcon";
import styles from "./CustomNode.module.css";

type Props = {
  node: NodeModel<CustomData>;
  depth: number;
  isOpen: boolean;
  onToggle: (id: NodeModel["id"]) => void;
  onClick: (id: NodeModel["id"])=>void
};

export const CustomNode: React.FC<Props> = (props) => {
  const { id, droppable, data } = props.node;
  const indent = props.depth * 5;

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    props.onToggle(props.node.id);
  };

  const handleClick = (e: React.MouseEvent) =>{
    e.stopPropagation();
    props.onClick(props.node.id);
  }

  const dragOverProps = useDragOver(id, props.isOpen, props.onToggle);

  return (
    <div
      className={`tree-node ${styles.root}`}
      style={{ paddingInlineStart: indent }}
      {...dragOverProps}
      onClick={handleClick}
    >
      <div className={`${styles.expandIconWrapper} ${props.isOpen ? styles.isOpen : ""}`} onClick={handleToggle}>
        {props.node.droppable && props.node.data?.hasChildren && (
          <div >
            <ArrowRightIcon />
          </div>
        )}
      </div>
      <div>
        <TypeIcon droppable={droppable} />
      </div>
      <div className={styles.labelGridItem}>
        {props.node.text}
      </div>
    </div>
  );
};
