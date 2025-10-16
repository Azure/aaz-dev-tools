import { useState, useCallback, useEffect } from "react";
import type { Command, CommandGroup } from "../interfaces";

interface CommandGroupMap {
  [id: string]: CommandGroup;
}

interface CommandMap {
  [id: string]: Command;
}

interface UseTreeStateReturn {
  selected: Command | CommandGroup | null;
  expanded: Set<string>;
  handleCommandTreeSelect: (nodeId: string) => void;
  handleCommandTreeToggle: (nodeIds: string[]) => void;
  updateExpanded: (commandGroupMap: CommandGroupMap, selected?: Command | CommandGroup | null) => void;
  setSelected: (selected: Command | CommandGroup | null) => void;
}

interface CommandTreeNode {
  id: string;
  names: string[];
  canDelete: boolean;
  leaves?: CommandTreeLeaf[];
  nodes?: CommandTreeNode[];
}

interface CommandTreeLeaf {
  id: string;
  names: string[];
}

export function useTreeState(
  commandMap: CommandMap,
  commandGroupMap: CommandGroupMap,
  commandTree: CommandTreeNode[],
): UseTreeStateReturn {
  const [selected, setSelected] = useState<Command | CommandGroup | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set<string>());

  const handleCommandTreeSelect = useCallback(
    (nodeId: string) => {
      if (nodeId.startsWith("command:")) {
        const selectedCommand = commandMap[nodeId];
        setSelected(selectedCommand);
      } else if (nodeId.startsWith("group:")) {
        const selectedGroup = commandGroupMap[nodeId];
        setSelected(selectedGroup);
      }
    },
    [commandMap, commandGroupMap],
  );

  const handleCommandTreeToggle = useCallback((nodeIds: string[]) => {
    const newExpanded = new Set(nodeIds);
    setExpanded(newExpanded);
  }, []);

  const updateExpanded = useCallback(
    (newCommandGroupMap: CommandGroupMap, newSelected?: Command | CommandGroup | null) => {
      setExpanded((prevExpanded) => {
        const newExpanded = new Set<string>();

        prevExpanded.forEach((value) => {
          if (value in newCommandGroupMap) {
            newExpanded.add(value);
          }
        });

        for (const groupId in newCommandGroupMap) {
          if (!(groupId in commandGroupMap)) {
            newExpanded.add(groupId);
          }
        }

        if (newSelected) {
          let expandedId = newSelected.id;
          if (expandedId.startsWith("command:")) {
            expandedId = expandedId.replace("command:", "group:").split("/").slice(0, -1).join("/");
          }
          const expandedIdParts = expandedId.split("/");
          expandedIdParts.forEach((_value, idx) => {
            newExpanded.add(expandedIdParts.slice(0, idx + 1).join("/"));
          });
        }

        return newExpanded;
      });
    },
    [commandGroupMap],
  );

  useEffect(() => {
    if (!selected && commandTree.length > 0) {
      const firstGroupId = commandTree[0].id;
      const firstGroup = commandGroupMap[firstGroupId];
      if (firstGroup) {
        setSelected(firstGroup);
      }
    }
  }, [selected, commandTree, commandGroupMap]);

  useEffect(() => {
    if (selected && Object.keys(commandGroupMap).length > 0) {
      setExpanded((prevExpanded) => {
        const newExpanded = new Set(prevExpanded);

        let expandedId = selected.id;
        if (expandedId.startsWith("command:")) {
          expandedId = expandedId.replace("command:", "group:").split("/").slice(0, -1).join("/");
        }
        const expandedIdParts = expandedId.split("/");
        expandedIdParts.forEach((_value, idx) => {
          newExpanded.add(expandedIdParts.slice(0, idx + 1).join("/"));
        });

        return newExpanded;
      });
    }
  }, [selected, commandGroupMap]);

  return {
    selected,
    expanded,
    handleCommandTreeSelect,
    handleCommandTreeToggle,
    updateExpanded,
    setSelected,
  };
}
