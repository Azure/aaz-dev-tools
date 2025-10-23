import React, { useState, useCallback, useRef } from "react";
import TreeView from "@mui/lab/TreeView";
import TreeItem from "@mui/lab/TreeItem";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { styled, Box, IconButton, Menu, MenuItem, Tooltip, Typography, TypographyProps } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import RefreshIcon from "@mui/icons-material/Refresh";
import MoreHorizSharpIcon from "@mui/icons-material/MoreHorizSharp";

interface CommandTreeLeaf {
  id: string;
  names: string[];
}

interface CommandTreeNode {
  id: string;
  names: string[];
  nodes?: CommandTreeNode[];
  leaves?: CommandTreeLeaf[];
  canDelete: boolean;
}

interface WSEditorCommandTreeProps {
  commandTreeNodes: CommandTreeNode[];
  selected: string;
  expanded: string[];
  onSelected: (nodeId: string) => void;
  onToggle: (nodeIds: string[]) => void;
  onAdd: () => void;
  onReload: () => void;
  onEditClientConfig?: () => void;
}

const HeaderTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 16,
  fontWeight: 600,
}));

const WSEditorCommandTree: React.FC<WSEditorCommandTreeProps> = ({
  commandTreeNodes,
  selected,
  expanded,
  onSelected,
  onToggle,
  onAdd,
  onReload,
  onEditClientConfig,
}) => {
  const [openMore, setOpenMore] = useState<boolean>(false);
  const moreButtonRef = useRef<HTMLButtonElement>(null);

  const handleNodeSelected = useCallback(
    (_event: React.SyntheticEvent, nodeIds: string[] | string) => {
      if (typeof nodeIds === "string") {
        onSelected(nodeIds);
      }
    },
    [onSelected],
  );

  const handleNodeToggle = useCallback(
    (_event: React.SyntheticEvent, nodeIds: string[]) => {
      onToggle(nodeIds);
    },
    [onToggle],
  );

  const handleMoreClick = useCallback(() => {
    setOpenMore((prevOpenMore) => !prevOpenMore);
  }, []);

  const handleEditClientConfig = useCallback(() => {
    setOpenMore(false);
    onEditClientConfig!();
  }, [onEditClientConfig]);

  const renderLeaf = useCallback(
    (leaf: CommandTreeLeaf) => {
      const leafName = leaf.names[leaf.names.length - 1];
      return (
        <TreeItem
          key={leaf.id}
          nodeId={leaf.id}
          color="inherit"
          label={leafName}
          onClick={(event) => {
            if (selected !== leaf.id) {
              handleNodeSelected(event, leaf.id);
            }
            event.stopPropagation();
            event.preventDefault();
          }}
        />
      );
    },
    [selected, handleNodeSelected],
  );

  const renderNode = useCallback(
    (node: CommandTreeNode): React.ReactElement => {
      const nodeName = node.names[node.names.length - 1];
      return (
        <TreeItem
          key={node.id}
          nodeId={node.id}
          color="inherit"
          label={nodeName}
          onClick={(event) => {
            if (selected !== node.id || expanded.indexOf(node.id) === -1) {
              handleNodeSelected(event, node.id);
              handleNodeToggle(event, [...expanded, node.id]);
            } else {
              handleNodeToggle(
                event,
                expanded.filter((v) => v !== node.id),
              );
            }
            event.stopPropagation();
            event.preventDefault();
          }}
        >
          {Array.isArray(node.leaves) ? node.leaves.map((leaf) => renderLeaf(leaf)) : null}
          {Array.isArray(node.nodes) ? node.nodes.map((subNode) => renderNode(subNode)) : null}
        </TreeItem>
      );
    },
    [selected, expanded, handleNodeSelected, handleNodeToggle, renderLeaf],
  );

  return (
    <React.Fragment>
      <Box
        sx={{
          mt: 2,
          ml: 4,
          mr: 2,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "flex-start",
        }}
      >
        <HeaderTypography>Command Tree</HeaderTypography>
        <Box sx={{ flexGrow: 1 }} />
        <Tooltip title="Reload Swagger Change">
          <IconButton color="secondary" onClick={onReload} aria-label="reload">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Add from Swagger">
          <IconButton color="secondary" onClick={onAdd} aria-label="add">
            <AddIcon />
          </IconButton>
        </Tooltip>
        {onEditClientConfig !== undefined && (
          <>
            <Tooltip title="More Operations">
              <IconButton
                ref={moreButtonRef}
                id="more-button"
                color="secondary"
                aria-controls={openMore ? "more-menu" : undefined}
                aria-expanded={openMore ? "true" : undefined}
                aria-haspopup="true"
                onClick={handleMoreClick}
              >
                <MoreHorizSharpIcon />
              </IconButton>
            </Tooltip>
            <Menu
              id="more-menu"
              anchorEl={moreButtonRef.current}
              open={openMore}
              onClose={() => {
                setOpenMore(false);
              }}
              MenuListProps={{
                "aria-labelledby": "more-button",
              }}
            >
              <MenuItem onClick={handleEditClientConfig}>Edit Client Config</MenuItem>
            </Menu>
          </>
        )}
      </Box>
      <TreeView
        defaultCollapseIcon={<ExpandMoreIcon />}
        defaultExpandIcon={<ChevronRightIcon />}
        selected={selected}
        expanded={expanded}
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          mt: 1,
          ml: 3,
          mr: 3,
        }}
      >
        {commandTreeNodes.map((node) => renderNode(node))}
      </TreeView>
    </React.Fragment>
  );
};

export default WSEditorCommandTree;

export type { CommandTreeNode, CommandTreeLeaf };
