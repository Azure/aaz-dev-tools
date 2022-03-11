import React from "react";
import { DragLayerMonitorProps } from "@minoru/react-dnd-treeview";
import { CheckData } from "./types";
import { TypeIcon } from "./TypeIcon";
import styles from "./CheckDragPreview.module.css";

type Props = {
  monitorProps: DragLayerMonitorProps<CheckData>;
};

export const CheckDragPreview: React.FC<Props> = (props) => {
  const item = props.monitorProps.item;

  return (
    <div className={styles.root}>
      <div className={styles.icon}>
        <TypeIcon type={item.data?.type} />
      </div>
      <div className={styles.label}>{item.text}</div>
    </div>
  );
};
