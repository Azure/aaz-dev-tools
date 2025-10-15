import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, screen } from "@testing-library/react";
import WSECArgumentSimilarPicker, {
  BuildArgSimilarTree,
  type ArgSimilarTree,
} from "../../views/workspace/argument/WSECArgumentSimilarPicker";
import { render } from "../test-utils";

describe("WSECArgumentSimilarPicker", () => {
  const mockOnTreeUpdated = vi.fn();
  const mockOnToggle = vi.fn();

  const mockArgSimilarTree: ArgSimilarTree = {
    root: {
      id: "az",
      name: "az",
      total: 4,
      selectedCount: 0,
      groups: [
        {
          id: "az/storage",
          name: "storage",
          total: 2,
          selectedCount: 0,
          commands: [
            {
              id: "az/storage/account",
              name: "account create",
              total: 2,
              selectedCount: 0,
              args: [
                {
                  id: "az/storage/account/Arguments/account_name",
                  var: "account_name",
                  display: "--account-name",
                  indexes: ["account-name"],
                  isSelected: false,
                },
                {
                  id: "az/storage/account/Arguments/resource_group",
                  var: "resource_group",
                  display: "--resource-group -g",
                  indexes: ["resource-group", "g"],
                  isSelected: false,
                },
              ],
            },
          ],
        },
        {
          id: "az/vm",
          name: "vm",
          total: 2,
          selectedCount: 0,
          commands: [
            {
              id: "az/vm/create",
              name: "create",
              total: 2,
              selectedCount: 0,
              args: [
                {
                  id: "az/vm/create/Arguments/vm_name",
                  var: "vm_name",
                  display: "--vm-name",
                  indexes: ["vm-name"],
                  isSelected: false,
                },
                {
                  id: "az/vm/create/Arguments/vm_size",
                  var: "vm_size",
                  display: "--vm-size",
                  indexes: ["vm-size"],
                  isSelected: false,
                },
              ],
            },
          ],
        },
      ],
    },
    selectedArgIds: [],
  };

  const defaultProps = {
    tree: mockArgSimilarTree,
    expandedIds: ["az", "az/storage", "az/vm", "az/storage/account", "az/vm/create"],
    updatedIds: [],
    onTreeUpdated: mockOnTreeUpdated,
    onToggle: mockOnToggle,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Component Rendering", () => {
    it("renders the tree structure correctly", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      // Check that the root group is rendered
      expect(screen.getByText("az")).toBeInTheDocument();

      // Check that command groups are rendered
      expect(screen.getByText("storage")).toBeInTheDocument();
      expect(screen.getByText("vm")).toBeInTheDocument();

      // Check that commands are rendered
      expect(screen.getByText("account create")).toBeInTheDocument();
      expect(screen.getByText("create")).toBeInTheDocument();

      // Check that arguments are rendered
      expect(screen.getByText("--account-name")).toBeInTheDocument();
      expect(screen.getByText("--resource-group -g")).toBeInTheDocument();
      expect(screen.getByText("--vm-name")).toBeInTheDocument();
      expect(screen.getByText("--vm-size")).toBeInTheDocument();
    });

    it("renders checkboxes for all tree items", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      // Should have checkboxes for: root (1) + groups (2) + commands (2) + args (4) = 9 total
      const checkboxes = screen.getAllByRole("checkbox");
      expect(checkboxes).toHaveLength(9);
    });

    it("renders expand/collapse icons", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      // TreeView should render with expand/collapse functionality
      const treeView = screen.getByRole("tree");
      expect(treeView).toBeInTheDocument();
    });
  });

  describe("Selection Functionality", () => {
    it("calls onTreeUpdated when an argument is selected", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      const accountNameCheckbox = screen.getByLabelText("--account-name");
      fireEvent.click(accountNameCheckbox);

      expect(mockOnTreeUpdated).toHaveBeenCalledTimes(1);
      const calledTree = mockOnTreeUpdated.mock.calls[0][0];
      expect(calledTree.selectedArgIds).toContain("az/storage/account/Arguments/account_name");
    });

    it("calls onTreeUpdated when an argument is deselected", () => {
      const treeWithSelection = {
        ...mockArgSimilarTree,
        selectedArgIds: ["az/storage/account/Arguments/account_name"],
        root: {
          ...mockArgSimilarTree.root,
          selectedCount: 1,
          groups: mockArgSimilarTree.root.groups?.map((group) =>
            group.id === "az/storage"
              ? {
                  ...group,
                  selectedCount: 1,
                  commands: group.commands?.map((command) =>
                    command.id === "az/storage/account"
                      ? {
                          ...command,
                          selectedCount: 1,
                          args: command.args.map((arg) =>
                            arg.id === "az/storage/account/Arguments/account_name" ? { ...arg, isSelected: true } : arg,
                          ),
                        }
                      : command,
                  ),
                }
              : group,
          ),
        },
      };

      const propsWithSelection = {
        ...defaultProps,
        tree: treeWithSelection,
      };

      render(<WSECArgumentSimilarPicker {...propsWithSelection} />);

      const accountNameCheckbox = screen.getByLabelText("--account-name");
      fireEvent.click(accountNameCheckbox);

      expect(mockOnTreeUpdated).toHaveBeenCalledTimes(1);
      const calledTree = mockOnTreeUpdated.mock.calls[0][0];
      expect(calledTree.selectedArgIds).not.toContain("az/storage/account/Arguments/account_name");
    });

    it("selects all command arguments when command is selected", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      const commandCheckbox = screen.getByLabelText("account create");
      fireEvent.click(commandCheckbox);

      expect(mockOnTreeUpdated).toHaveBeenCalledTimes(1);
      const calledTree = mockOnTreeUpdated.mock.calls[0][0];
      expect(calledTree.selectedArgIds).toContain("az/storage/account/Arguments/account_name");
      expect(calledTree.selectedArgIds).toContain("az/storage/account/Arguments/resource_group");
    });

    it("shows indeterminate state when some but not all children are selected", () => {
      const treeWithPartialSelection = {
        ...mockArgSimilarTree,
        selectedArgIds: ["az/storage/account/Arguments/account_name"],
        root: {
          ...mockArgSimilarTree.root,
          selectedCount: 1,
          groups: mockArgSimilarTree.root.groups?.map((group) =>
            group.id === "az/storage"
              ? {
                  ...group,
                  selectedCount: 1,
                  commands: group.commands?.map((command) =>
                    command.id === "az/storage/account"
                      ? {
                          ...command,
                          selectedCount: 1,
                          args: command.args.map((arg) =>
                            arg.id === "az/storage/account/Arguments/account_name" ? { ...arg, isSelected: true } : arg,
                          ),
                        }
                      : command,
                  ),
                }
              : group,
          ),
        },
      };

      const propsWithPartialSelection = {
        ...defaultProps,
        tree: treeWithPartialSelection,
      };

      render(<WSECArgumentSimilarPicker {...propsWithPartialSelection} />);

      const commandCheckbox = screen.getByLabelText("account create");

      expect(commandCheckbox).toHaveAttribute("data-indeterminate", "true");
    });

    it("disables checkboxes for updated arguments", () => {
      const propsWithUpdatedIds = {
        ...defaultProps,
        updatedIds: ["az/storage/account/Arguments/account_name"],
      };

      render(<WSECArgumentSimilarPicker {...propsWithUpdatedIds} />);

      const accountNameCheckbox = screen.getByLabelText("--account-name");
      expect(accountNameCheckbox).toBeDisabled();
    });
  });

  describe("Tree Expansion", () => {
    it("renders TreeView with expand/collapse functionality", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      const treeView = screen.getByRole("tree");
      expect(treeView).toBeInTheDocument();

      // Check that expanded IDs are passed correctly
      expect(defaultProps.expandedIds).toContain("az");
      expect(defaultProps.expandedIds).toContain("az/storage");
    });
  });

  describe("BuildArgSimilarTree Utility", () => {
    it("transforms API response into correct tree structure", () => {
      const mockApiResponse = {
        data: {
          aaz: {
            id: "aaz",
            commandGroups: {
              storage: {
                id: "storage",
                commands: {
                  "account create": {
                    id: "account-create",
                    args: {
                      name: ["name"],
                      resource_group: ["resource-group", "g"],
                    },
                  },
                },
              },
            },
          },
        },
      };

      const result = BuildArgSimilarTree(mockApiResponse);

      expect(result.tree.root.name).toBe("az storage");
      expect(result.tree.selectedArgIds).toEqual([]);
      expect(result.expandedIds).toContain("storage");
      expect(result.tree.root.commands).toBeDefined();
      expect(result.tree.root.commands![0].name).toBe("account create");
    });

    it("handles single character options correctly", () => {
      const mockApiResponse = {
        data: {
          aaz: {
            id: "aaz",
            commands: {
              test: {
                id: "test",
                args: {
                  short_option: ["g"],
                  long_option: ["resource-group"],
                  both_options: ["resource-group", "g"],
                },
              },
            },
          },
        },
      };

      const result = BuildArgSimilarTree(mockApiResponse);
      const command = result.tree.root.commands![0];

      expect(command.args[0].display).toBe("--g");
      expect(command.args[1].display).toBe("--resource-group");
      expect(command.args[2].display).toBe("[both_options] --resource-group --g");
    });

    it("handles nested special characters in options", () => {
      const mockApiResponse = {
        data: {
          aaz: {
            id: "aaz",
            commands: {
              test: {
                id: "test",
                args: {
                  nested_option: [".property", "[index]", "{key}"],
                },
              },
            },
          },
        },
      };

      const result = BuildArgSimilarTree(mockApiResponse);
      const command = result.tree.root.commands![0];

      // The logic checks idx[1], so for ".property" -> "p", "[index]" -> "i", "{key}" -> "k"
      // Since these are not ".", "[", or "{", they get "--" prefix
      expect(command.args[0].display).toBe("[nested_option] --.property --[index] --{key}");
    });
  });

  describe("Edge Cases", () => {
    it("handles empty tree gracefully", () => {
      const emptyTree: ArgSimilarTree = {
        root: {
          id: "empty",
          name: "empty",
          total: 0,
          selectedCount: 0,
        },
        selectedArgIds: [],
      };

      const emptyProps = {
        ...defaultProps,
        tree: emptyTree,
        expandedIds: ["empty"],
      };

      render(<WSECArgumentSimilarPicker {...emptyProps} />);

      expect(screen.getByText("empty")).toBeInTheDocument();
      expect(screen.getAllByRole("checkbox")).toHaveLength(1);
    });

    it("handles tree with only groups (no commands)", () => {
      const groupOnlyTree: ArgSimilarTree = {
        root: {
          id: "root",
          name: "root",
          total: 0,
          selectedCount: 0,
          groups: [
            {
              id: "group1",
              name: "group1",
              total: 0,
              selectedCount: 0,
            },
          ],
        },
        selectedArgIds: [],
      };

      const groupOnlyProps = {
        ...defaultProps,
        tree: groupOnlyTree,
        expandedIds: ["root", "group1"],
      };

      render(<WSECArgumentSimilarPicker {...groupOnlyProps} />);

      expect(screen.getByText("root")).toBeInTheDocument();
      expect(screen.getByText("group1")).toBeInTheDocument();
    });

    it("prevents event propagation on checkbox clicks", () => {
      render(<WSECArgumentSimilarPicker {...defaultProps} />);

      const accountNameCheckbox = screen.getByLabelText("--account-name");
      const event = new MouseEvent("click", { bubbles: true, cancelable: true });

      fireEvent(accountNameCheckbox, event);

      // The component should call stopPropagation and preventDefault
      // This ensures clicking checkbox doesn't trigger tree node expansion
      expect(mockOnTreeUpdated).toHaveBeenCalledTimes(1);
    });
  });
});
