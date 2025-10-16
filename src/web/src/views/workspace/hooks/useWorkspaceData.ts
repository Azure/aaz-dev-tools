import { useState, useCallback } from "react";
import { workspaceApi, specsApi } from "../../../services";
import type {
  CommandGroup,
  ResponseCommandGroup,
  ResponseCommandGroups,
  Command,
  ResponseCommand,
} from "../interfaces";
import { DecodeResponseCommand } from "../components/WSEditorCommandContent";
import { DecodeResponseCommandGroup } from "../components/WSEditorCommandGroupContent";

interface CommandGroupMap {
  [id: string]: CommandGroup;
}

interface CommandMap {
  [id: string]: Command;
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

interface WorkspaceData {
  name: string;
  workspaceUrl: string;
  plane: string;
  source: string;
  clientConfigurable: boolean;
  commandMap: CommandMap;
  commandGroupMap: CommandGroupMap;
  commandTree: CommandTreeNode[];
  reloadTimestamp: number | null;
}

interface UseWorkspaceDataReturn extends WorkspaceData {
  loadWorkspace: () => Promise<void>;
  getWorkspaceClientConfig: (workspaceUrl: string) => Promise<any>;
}

export function useWorkspaceData(workspaceName: string): UseWorkspaceDataReturn {
  const [workspaceData, setWorkspaceData] = useState<WorkspaceData>({
    name: workspaceName,
    workspaceUrl: `/AAZ/Editor/Workspaces/${workspaceName}`,
    plane: "",
    source: "",
    clientConfigurable: false,
    commandMap: {},
    commandGroupMap: {},
    commandTree: [],
    reloadTimestamp: null,
  });
  const [isLoading, setIsLoading] = useState(false);

  const getWorkspaceClientConfig = useCallback(async (workspaceUrl: string) => {
    return await workspaceApi.getWorkspaceClientConfig(workspaceUrl);
  }, []);

  const loadWorkspace = useCallback(async () => {
    if (isLoading) return; // Prevent concurrent calls

    setIsLoading(true);
    try {
      const planeNames = await specsApi.getPlaneNames();
      const workspaceResponse = await workspaceApi.getWorkspace(`/AAZ/Editor/Workspaces/${workspaceName}`);
      const reloadTimestamp = Date.now();
      const commandMap: CommandMap = {};
      const commandGroupMap: CommandGroupMap = {};

      const buildCommand = (command_1: ResponseCommand): CommandTreeLeaf => {
        const cmd: Command = DecodeResponseCommand(command_1);
        commandMap[cmd.id] = cmd;
        return {
          id: cmd.id,
          names: [...cmd.names],
        };
      };

      const buildCommandGroup = (commandGroup_1: ResponseCommandGroup): CommandTreeNode => {
        const group: CommandGroup = DecodeResponseCommandGroup(commandGroup_1);

        commandGroupMap[group.id] = group;

        const node: CommandTreeNode = {
          id: group.id,
          names: [...group.names],
          canDelete: group.canDelete,
        };

        if (typeof commandGroup_1.commands === "object" && commandGroup_1.commands !== null) {
          node["leaves"] = [];

          for (const name in commandGroup_1.commands) {
            const subLeave = buildCommand(commandGroup_1.commands[name]);
            node["leaves"].push(subLeave);
          }
          node["leaves"].sort((a, b) => a.id.localeCompare(b.id));
          if (node["leaves"].length > 0) {
            node.canDelete = false;
          }
        }

        if (typeof commandGroup_1.commandGroups === "object" && commandGroup_1.commandGroups !== null) {
          node["nodes"] = [];
          for (const name_1 in commandGroup_1.commandGroups) {
            const subNode = buildCommandGroup(commandGroup_1.commandGroups[name_1]);
            node["nodes"].push(subNode);
            if (!subNode.canDelete) {
              node.canDelete = false;
            }
          }
          node["nodes"].sort((a_1, b_1) => a_1.id.localeCompare(b_1.id));
        }

        if ((node["leaves"]?.length ?? 0) > 1) {
          node.canDelete = false;
        }
        group.canDelete = node.canDelete;
        return node;
      };

      const commandTree: CommandTreeNode[] = [];

      if (workspaceResponse.commandTree.commandGroups) {
        const cmdGroups: ResponseCommandGroups = workspaceResponse.commandTree.commandGroups;
        for (const key in cmdGroups) {
          commandTree.push(buildCommandGroup(cmdGroups[key]));
        }
        commandTree.sort((a_2, b_2) => a_2.id.localeCompare(b_2.id));
      }

      const clientConfigurable = !planeNames.includes(workspaceResponse.plane);

      setWorkspaceData((prev) => ({
        ...prev,
        plane: workspaceResponse.plane,
        source: workspaceResponse.source,
        clientConfigurable,
        commandTree,
        reloadTimestamp,
        commandMap,
        commandGroupMap,
      }));
    } catch (err) {
      console.error(err);
    }
  }, [workspaceName]);

  return {
    ...workspaceData,
    loadWorkspace,
    getWorkspaceClientConfig,
  };
}
