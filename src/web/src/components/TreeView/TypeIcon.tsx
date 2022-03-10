import React from "react";
import FolderIcon from "@mui/icons-material/Folder";
import DescriptionIcon from "@mui/icons-material/Description";

type Props = {
  type?: string;
};

export const TypeIcon: React.FC<Props> = (props) => {

  
  if (props.type==="CommandGroup") {
    return <FolderIcon />;
  } else {
    return <DescriptionIcon/>
  }
};