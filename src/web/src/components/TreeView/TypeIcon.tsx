import React from "react";
import FolderIcon from "@mui/icons-material/Folder";
import ImageIcon from "@mui/icons-material/Image";
import ListAltIcon from "@mui/icons-material/ListAlt";
import DescriptionIcon from "@mui/icons-material/Description";

type Props = {
  
  type?: string;
};

export const TypeIcon: React.FC<Props> = (props) => {

  
  if (props.type==="commandGroup") {
    return <FolderIcon />;
  } else {
    return <DescriptionIcon/>
  }
};