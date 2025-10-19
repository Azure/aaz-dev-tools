import { describe, it, expect } from "vitest";
import {
  ProfileCommandTree,
  initializeCommandTreeByModView,
  exportModViewProfile,
} from "../../../views/cli/utils/commandTreeInitialization";
import { CLIModViewProfile } from "../../../views/cli/interfaces";
import { CLISpecsSimpleCommandTree } from "../../../views/cli/CLIModuleGenerator";

describe("CLIModGeneratorProfileCommandTree", () => {
  describe("initializeCommandTreeByModView", () => {
    it("should initialize command tree with empty profile", () => {
      const profileName = "test-profile";
      const view: CLIModViewProfile | null = null;
      const simpleTree: CLISpecsSimpleCommandTree = {
        root: {
          names: ["root"],
          commands: {},
          commandGroups: {
            "test-group": {
              names: ["test-group"],
              commands: {
                "test-command": {
                  names: ["test-group", "test-command"],
                },
              },
              commandGroups: {},
            },
          },
        },
      };

      const result = initializeCommandTreeByModView(profileName, view, simpleTree);

      expect(result.name).toBe(profileName);
      expect(result.commandGroups).toBeDefined();
      expect(result.commandGroups["test-group"]).toBeDefined();
      expect(result.commandGroups["test-group"].names).toEqual(["test-group"]);
      expect(result.commandGroups["test-group"].commands).toBeDefined();
      expect(result.commandGroups["test-group"].commands!["test-command"]).toBeDefined();
      expect(result.commandGroups["test-group"].commands!["test-command"].names).toEqual([
        "test-group",
        "test-command",
      ]);
      expect(result.commandGroups["test-group"].commands!["test-command"].selected).toBe(false);
    });

    it("should initialize command tree with profile view", () => {
      const profileName = "test-profile";
      const view: CLIModViewProfile = {
        name: "test-profile",
        commandGroups: {
          "test-group": {
            names: ["test-group"],
            commands: {
              "test-command": {
                names: ["test-group", "test-command"],
                version: "2023-01-01",
                registered: true,
                modified: false,
              },
            },
          },
        },
      };
      const simpleTree: CLISpecsSimpleCommandTree = {
        root: {
          names: ["root"],
          commands: {},
          commandGroups: {
            "test-group": {
              names: ["test-group"],
              commands: {
                "test-command": {
                  names: ["test-group", "test-command"],
                },
              },
              commandGroups: {},
            },
          },
        },
      };

      const result = initializeCommandTreeByModView(profileName, view, simpleTree);

      expect(result.name).toBe(profileName);
      expect(result.commandGroups["test-group"].commands!["test-command"].selected).toBe(true);
      expect(result.commandGroups["test-group"].commands!["test-command"].selectedVersion).toBe("2023-01-01");
      expect(result.commandGroups["test-group"].commands!["test-command"].registered).toBe(true);
    });

    it("should throw error for missing command groups in aaz", () => {
      const profileName = "test-profile";
      const view: CLIModViewProfile = {
        name: "test-profile",
        commandGroups: {
          "missing-group": {
            names: ["missing-group"],
            commands: {},
          },
        },
      };
      const simpleTree: CLISpecsSimpleCommandTree = {
        root: {
          names: ["root"],
          commands: {},
          commandGroups: {},
        },
      };

      expect(() => {
        initializeCommandTreeByModView(profileName, view, simpleTree);
      }).toThrow("Miss command groups in aaz: `az missing-group`");
    });
  });

  describe("exportModViewProfile", () => {
    it("should export profile with selected commands", () => {
      const tree: ProfileCommandTree = {
        name: "test-profile",
        commandGroups: {
          "test-group": {
            id: "test-group",
            names: ["test-group"],
            commands: {
              "test-command": {
                id: "test-group/test-command",
                names: ["test-group", "test-command"],
                selected: true,
                selectedVersion: "2023-01-01",
                registered: true,
                modified: false,
                loading: false,
              },
            },
            loading: false,
            selected: true,
          },
        },
      };

      const result = exportModViewProfile(tree);

      expect(result.name).toBe("test-profile");
      expect(result.commandGroups).toBeDefined();
      expect(result.commandGroups!["test-group"]).toBeDefined();
      expect(result.commandGroups!["test-group"].names).toEqual(["test-group"]);
      expect(result.commandGroups!["test-group"].commands!["test-command"]).toBeDefined();
      expect(result.commandGroups!["test-group"].commands!["test-command"].names).toEqual([
        "test-group",
        "test-command",
      ]);
      expect(result.commandGroups!["test-group"].commands!["test-command"].version).toBe("2023-01-01");
      expect(result.commandGroups!["test-group"].commands!["test-command"].registered).toBe(true);
      expect(result.commandGroups!["test-group"].commands!["test-command"].modified).toBe(false);
    });

    it("should exclude unselected commands", () => {
      const tree: ProfileCommandTree = {
        name: "test-profile",
        commandGroups: {
          "test-group": {
            id: "test-group",
            names: ["test-group"],
            commands: {
              "selected-command": {
                id: "test-group/selected-command",
                names: ["test-group", "selected-command"],
                selected: true,
                selectedVersion: "2023-01-01",
                registered: true,
                modified: false,
                loading: false,
              },
              "unselected-command": {
                id: "test-group/unselected-command",
                names: ["test-group", "unselected-command"],
                selected: false,
                modified: false,
                loading: false,
              },
            },
            loading: false,
            selected: undefined,
          },
        },
      };

      const result = exportModViewProfile(tree);

      expect(result.commandGroups!["test-group"].commands!["selected-command"]).toBeDefined();
      expect(result.commandGroups!["test-group"].commands!["unselected-command"]).toBeUndefined();
    });

    it("should exclude command groups marked as false", () => {
      const tree: ProfileCommandTree = {
        name: "test-profile",
        commandGroups: {
          "selected-group": {
            id: "selected-group",
            names: ["selected-group"],
            commands: {},
            loading: false,
            selected: true,
          },
          "unselected-group": {
            id: "unselected-group",
            names: ["unselected-group"],
            commands: {},
            loading: false,
            selected: false,
          },
        },
      };

      const result = exportModViewProfile(tree);

      expect(result.commandGroups!["selected-group"]).toBeDefined();
      expect(result.commandGroups!["unselected-group"]).toBeUndefined();
    });
  });
});
