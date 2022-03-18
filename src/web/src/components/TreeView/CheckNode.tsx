import React from "react";
import { NativeSelect, Typography } from "@mui/material";
import { Checkbox } from "@mui/material";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import { NodeModel } from "@minoru/react-dnd-treeview";
import { CheckData } from "./types";
import { TypeIcon } from "./TypeIcon";
import styles from "./CheckNode.module.css";
import FormControl from "@mui/material/FormControl";

type Props = {
  node: NodeModel<CheckData>;
  depth: number;
  isOpen: boolean;
  isSelected: boolean;
  onToggle: (id: NodeModel["id"]) => void;
  onSelect: (node: NodeModel<CheckData>) => void;
  onChange: (node: NodeModel<CheckData>, version: string) => void;
};

export const CheckNode: React.FC<Props> = (props) => {
  const { data } = props.node;
  const versions = data!.versions;
  const indent = props.depth * 24;

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    props.onToggle(props.node.id);
  };

  const handleSelect = () => props.onSelect(props.node);
  const handleChange = (event: any) => {
    if (versions) {
      const currVersion = versions[event.target.value];
      props.onChange(props.node, currVersion);
    }
  };
  return (
    <div
      className={`tree-node ${styles.root} ${
        props.isSelected ? styles.isSelected : ""
      }`}
      style={{ paddingInlineStart: indent }}
    >
      <div
        className={`${styles.expandIconWrapper} ${
          props.isOpen ? styles.isOpen : ""
        }`}
      >
        {props.node.droppable && (
          <div onClick={handleToggle}>
            <ArrowRightIcon />
          </div>
        )}
      </div>
      {data!.type === "Command" && (
        <div>
          <Checkbox
            color="primary"
            size="small"
            checked={props.isSelected}
            onClick={handleSelect}
          />
        </div>
      )}
      <div>
        <TypeIcon type={data!.type} />
      </div>
      <div className={styles.labelGridItem}>
        <Typography variant="inherit">{props.node.text}</Typography>
      </div>
      <div>
        {props.isSelected && (
          <FormControl sx={{ m: 1, minWidth: 80 }}>
            <NativeSelect
              key={data!.versionIndex}
              defaultValue={data!.versionIndex}
              inputProps={{
                name: "version",
                id: "uncontrolled-native",
              }}
              onChange={handleChange}
            >
              {versions?.map((version, idx) => (
                <option key={idx} value={idx}>
                  {version}
                </option>
              ))}
            </NativeSelect>
          </FormControl>
        )}
      </div>
    </div>
  );
};
