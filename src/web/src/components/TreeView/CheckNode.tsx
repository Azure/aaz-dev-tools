import React from "react";
import {Typography} from "@mui/material";
import {Checkbox} from "@mui/material";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {NodeModel} from "@minoru/react-dnd-treeview";
import {CheckData} from "./types";
import {TypeIcon} from "./TypeIcon";
import styles from "./CheckNode.module.css";


type Props = {
  node: NodeModel<CheckData>;
  depth: number;
  isOpen: boolean;
  isSelected: boolean;
  onToggle: (id: NodeModel["id"]) => void;
  onSelect: (node: NodeModel) => void;
};

export const CheckNode: React.FC<Props> = (props) => {
  const {data} = props.node;
  const indent = props.depth * 24;

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    props.onToggle(props.node.id);
  };

  const handleSelect = () => props.onSelect(props.node);

  return (
      <div
          className={`tree-node ${styles.root} ${props.isSelected ? styles.isSelected : ""}`}
          style={{paddingInlineStart: indent}}
      >
        <div className={`${styles.expandIconWrapper} ${props.isOpen ? styles.isOpen : ""}`}>
          {props.node.droppable && (
              <div onClick={handleToggle}>
                <ArrowRightIcon />
              </div>
          )}
        </div>
        <div>
          <Checkbox
              color="primary"
              size="small"
              checked={props.isSelected}
              onClick={handleSelect}
          />
        </div>
        <div>
          <TypeIcon type={data?.type}/>
        </div>
        <div className={styles.labelGridItem}>
          <Typography variant="inherit">
            {props.node.text}
          </Typography>
        </div>
      </div>
  );
};
