import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import WSEditorCommandTree, { CommandTreeNode, CommandTreeLeaf } from "../../views/workspace/WSEditorCommandTree";

describe("WSEditorCommandTree", () => {
  const mockLeaf: CommandTreeLeaf = {
    id: "leaf-1",
    names: ["az", "storage", "account", "create"],
  };

  const mockNode: CommandTreeNode = {
    id: "node-1",
    names: ["az", "storage"],
    canDelete: true,
    leaves: [mockLeaf],
    nodes: [
      {
        id: "subnode-1",
        names: ["az", "storage", "blob"],
        canDelete: true,
        leaves: [
          {
            id: "leaf-2",
            names: ["az", "storage", "blob", "upload"],
          },
        ],
      },
    ],
  };

  const complexTreeData: CommandTreeNode[] = [
    mockNode,
    {
      id: "node-2",
      names: ["az", "vm"],
      canDelete: false,
      leaves: [
        {
          id: "leaf-3",
          names: ["az", "vm", "create"],
        },
        {
          id: "leaf-4",
          names: ["az", "vm", "delete"],
        },
      ],
      nodes: [
        {
          id: "subnode-2",
          names: ["az", "vm", "disk"],
          canDelete: true,
          leaves: [
            {
              id: "leaf-5",
              names: ["az", "vm", "disk", "attach"],
            },
          ],
        },
      ],
    },
  ];

  const defaultProps = {
    commandTreeNodes: [mockNode],
    selected: "",
    expanded: [],
    onSelected: vi.fn(),
    onToggle: vi.fn(),
    onAdd: vi.fn(),
    onReload: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Core Rendering", () => {
    it("renders the command tree header", () => {
      render(<WSEditorCommandTree {...defaultProps} />);

      expect(screen.getByText("Command Tree")).toBeInTheDocument();
    });

    it("renders toolbar buttons", () => {
      render(<WSEditorCommandTree {...defaultProps} />);

      expect(screen.getByRole("button", { name: /reload/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /add/i })).toBeInTheDocument();
    });

    it("renders tree nodes with correct labels", () => {
      render(<WSEditorCommandTree {...defaultProps} />);

      expect(screen.getByText("storage")).toBeInTheDocument();
    });

    it("renders tree leaves when expanded", () => {
      const propsWithExpanded = {
        ...defaultProps,
        expanded: ["node-1"],
      };

      render(<WSEditorCommandTree {...propsWithExpanded} />);

      expect(screen.getByText("create")).toBeInTheDocument();
    });

    it("renders empty tree gracefully", () => {
      const emptyProps = {
        ...defaultProps,
        commandTreeNodes: [],
      };

      render(<WSEditorCommandTree {...emptyProps} />);

      expect(screen.getByText("Command Tree")).toBeInTheDocument();
    });
  });

  describe("Tree Navigation", () => {
    it("calls onSelected when leaf is clicked", async () => {
      const user = userEvent.setup();
      const propsWithExpanded = {
        ...defaultProps,
        expanded: ["node-1"],
      };

      render(<WSEditorCommandTree {...propsWithExpanded} />);

      const leafNode = screen.getByText("create");
      await user.click(leafNode);

      expect(defaultProps.onSelected).toHaveBeenCalledWith("leaf-1");
    });

    it("calls onSelected and onToggle when node is clicked and not selected", async () => {
      const user = userEvent.setup();

      render(<WSEditorCommandTree {...defaultProps} />);

      const nodeElement = screen.getByText("storage");
      await user.click(nodeElement);

      expect(defaultProps.onSelected).toHaveBeenCalledWith("node-1");
      expect(defaultProps.onToggle).toHaveBeenCalledWith(["node-1"]);
    });

    it("toggles node expansion when already selected node is clicked", async () => {
      const user = userEvent.setup();
      const propsWithSelected = {
        ...defaultProps,
        selected: "node-1",
        expanded: ["node-1"],
      };

      render(<WSEditorCommandTree {...propsWithSelected} />);

      const nodeElement = screen.getByText("storage");
      await user.click(nodeElement);

      expect(defaultProps.onToggle).toHaveBeenCalledWith([]);
    });

    it("handles complex tree navigation", () => {
      const complexProps = {
        ...defaultProps,
        commandTreeNodes: complexTreeData,
        expanded: ["node-1", "node-2", "subnode-1", "subnode-2"],
      };

      render(<WSEditorCommandTree {...complexProps} />);

      expect(screen.getByText("storage")).toBeInTheDocument();
      expect(screen.getByText("vm")).toBeInTheDocument();
      expect(screen.getByText("blob")).toBeInTheDocument();
      expect(screen.getByText("disk")).toBeInTheDocument();
      expect(screen.getAllByText("create")).toHaveLength(2);
      expect(screen.getByText("upload")).toBeInTheDocument();
      expect(screen.getByText("attach")).toBeInTheDocument();
    });

    it("does not trigger events when same leaf is clicked again", async () => {
      const user = userEvent.setup();
      const propsWithSelected = {
        ...defaultProps,
        selected: "leaf-1",
        expanded: ["node-1"],
      };

      render(<WSEditorCommandTree {...propsWithSelected} />);

      const leafNode = screen.getByText("create");
      await user.click(leafNode);

      expect(defaultProps.onSelected).not.toHaveBeenCalled();
    });
  });

  describe("Toolbar Actions", () => {
    it("calls onReload when reload button is clicked", async () => {
      const user = userEvent.setup();

      render(<WSEditorCommandTree {...defaultProps} />);

      const reloadButton = screen.getByRole("button", { name: /reload/i });
      await user.click(reloadButton);

      expect(defaultProps.onReload).toHaveBeenCalled();
    });

    it("calls onAdd when add button is clicked", async () => {
      const user = userEvent.setup();

      render(<WSEditorCommandTree {...defaultProps} />);

      const addButton = screen.getByRole("button", { name: /add/i });
      await user.click(addButton);

      expect(defaultProps.onAdd).toHaveBeenCalled();
    });

    it("shows more menu when onEditClientConfig is provided", () => {
      const propsWithMoreActions = {
        ...defaultProps,
        onEditClientConfig: vi.fn(),
      };

      render(<WSEditorCommandTree {...propsWithMoreActions} />);

      expect(screen.getByRole("button", { name: /more operations/i })).toBeInTheDocument();
    });

    it("does not show more menu when onEditClientConfig is not provided", () => {
      render(<WSEditorCommandTree {...defaultProps} />);

      expect(screen.queryByRole("button", { name: /more operations/i })).not.toBeInTheDocument();
    });

    it("opens and closes more menu correctly", async () => {
      const user = userEvent.setup();
      const propsWithMoreActions = {
        ...defaultProps,
        onEditClientConfig: vi.fn(),
      };

      render(<WSEditorCommandTree {...propsWithMoreActions} />);

      const moreButton = screen.getByRole("button", { name: /more operations/i });

      expect(screen.queryByRole("menu")).not.toBeInTheDocument();

      await user.click(moreButton);
      expect(screen.getByRole("menu")).toBeInTheDocument();
      expect(screen.getByRole("menuitem", { name: /edit client config/i })).toBeInTheDocument();

      await user.keyboard("{Escape}");
      await waitFor(() => {
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
      });
    });

    it("calls onEditClientConfig and closes menu when menu item is clicked", async () => {
      const user = userEvent.setup();
      const mockEditClientConfig = vi.fn();
      const propsWithMoreActions = {
        ...defaultProps,
        onEditClientConfig: mockEditClientConfig,
      };

      render(<WSEditorCommandTree {...propsWithMoreActions} />);

      const moreButton = screen.getByRole("button", { name: /more operations/i });
      await user.click(moreButton);

      const editConfigMenuItem = screen.getByRole("menuitem", { name: /edit client config/i });
      await user.click(editConfigMenuItem);

      expect(mockEditClientConfig).toHaveBeenCalled();
      await waitFor(() => {
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
      });
    });
  });

  describe("Tree Structure Handling", () => {
    it("handles nodes without leaves", () => {
      const nodeWithoutLeaves: CommandTreeNode = {
        id: "node-no-leaves",
        names: ["az", "group"],
        canDelete: true,
        nodes: [
          {
            id: "subnode-only",
            names: ["az", "group", "subgroup"],
            canDelete: true,
          },
        ],
      };

      const propsWithNodeOnly = {
        ...defaultProps,
        commandTreeNodes: [nodeWithoutLeaves],
        expanded: ["node-no-leaves"],
      };

      render(<WSEditorCommandTree {...propsWithNodeOnly} />);

      expect(screen.getByText("group")).toBeInTheDocument();
      expect(screen.getByText("subgroup")).toBeInTheDocument();
    });

    it("handles nodes without subnodes", () => {
      const nodeWithLeavesOnly: CommandTreeNode = {
        id: "node-leaves-only",
        names: ["az", "simple"],
        canDelete: true,
        leaves: [
          {
            id: "simple-leaf-1",
            names: ["az", "simple", "command1"],
          },
          {
            id: "simple-leaf-2",
            names: ["az", "simple", "command2"],
          },
        ],
      };

      const propsWithLeavesOnly = {
        ...defaultProps,
        commandTreeNodes: [nodeWithLeavesOnly],
        expanded: ["node-leaves-only"],
      };

      render(<WSEditorCommandTree {...propsWithLeavesOnly} />);

      expect(screen.getByText("simple")).toBeInTheDocument();
      expect(screen.getByText("command1")).toBeInTheDocument();
      expect(screen.getByText("command2")).toBeInTheDocument();
    });

    it("displays last segment of names array for nodes and leaves", () => {
      const multiSegmentData: CommandTreeNode[] = [
        {
          id: "multi-segment-node",
          names: ["az", "resource", "group", "deployment"],
          canDelete: true,
          leaves: [
            {
              id: "multi-segment-leaf",
              names: ["az", "resource", "group", "deployment", "create"],
            },
          ],
        },
      ];

      const propsWithMultiSegment = {
        ...defaultProps,
        commandTreeNodes: multiSegmentData,
        expanded: ["multi-segment-node"],
      };

      render(<WSEditorCommandTree {...propsWithMultiSegment} />);

      expect(screen.getByText("deployment")).toBeInTheDocument();
      expect(screen.getByText("create")).toBeInTheDocument();
    });
  });

  describe("Selection and Expansion State", () => {
    it("highlights selected node/leaf", () => {
      const propsWithSelection = {
        ...defaultProps,
        selected: "node-1",
        expanded: ["node-1"],
      };

      render(<WSEditorCommandTree {...propsWithSelection} />);

      const treeView = screen.getByRole("tree");
      expect(treeView).toBeInTheDocument();
    });

    it("expands nodes based on expanded prop", () => {
      const propsWithExpansion = {
        ...defaultProps,
        commandTreeNodes: complexTreeData,
        expanded: ["node-1", "subnode-1"],
      };

      render(<WSEditorCommandTree {...propsWithExpansion} />);

      expect(screen.getByText("blob")).toBeInTheDocument();
      expect(screen.getByText("upload")).toBeInTheDocument();
    });

    it("handles empty selection and expansion arrays", () => {
      const propsWithEmpty = {
        ...defaultProps,
        selected: "",
        expanded: [],
      };

      render(<WSEditorCommandTree {...propsWithEmpty} />);

      expect(screen.getByText("Command Tree")).toBeInTheDocument();
      expect(screen.getByText("storage")).toBeInTheDocument();
    });
  });

  describe("Event Handling", () => {
    it("prevents event propagation on leaf clicks", async () => {
      const propsWithExpanded = {
        ...defaultProps,
        expanded: ["node-1"],
      };

      render(<WSEditorCommandTree {...propsWithExpanded} />);

      const leafNode = screen.getByText("create");
      const clickEvent = new MouseEvent("click", { bubbles: true });
      const stopPropagationSpy = vi.spyOn(clickEvent, "stopPropagation");
      const preventDefaultSpy = vi.spyOn(clickEvent, "preventDefault");

      fireEvent(leafNode, clickEvent);

      expect(stopPropagationSpy).toHaveBeenCalled();
      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it("prevents event propagation on node clicks", async () => {
      render(<WSEditorCommandTree {...defaultProps} />);

      const nodeElement = screen.getByText("storage");
      const clickEvent = new MouseEvent("click", { bubbles: true });
      const stopPropagationSpy = vi.spyOn(clickEvent, "stopPropagation");
      const preventDefaultSpy = vi.spyOn(clickEvent, "preventDefault");

      fireEvent(nodeElement, clickEvent);

      expect(stopPropagationSpy).toHaveBeenCalled();
      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it("handles multiple node toggles correctly", async () => {
      const user = userEvent.setup();
      const propsWithMultipleExpanded = {
        ...defaultProps,
        commandTreeNodes: complexTreeData,
        expanded: ["node-1", "node-2"],
        selected: "node-1",
      };

      render(<WSEditorCommandTree {...propsWithMultipleExpanded} />);

      const storageNode = screen.getByText("storage");
      await user.click(storageNode);

      expect(defaultProps.onToggle).toHaveBeenCalledWith(["node-2"]);
    });
  });

  describe("Component State Management", () => {
    it("manages more menu open state correctly", async () => {
      const user = userEvent.setup();
      const propsWithMoreActions = {
        ...defaultProps,
        onEditClientConfig: vi.fn(),
      };

      render(<WSEditorCommandTree {...propsWithMoreActions} />);

      const moreButton = screen.getByRole("button", { name: /more operations/i });

      expect(screen.queryByRole("menu")).not.toBeInTheDocument();

      await user.click(moreButton);
      expect(screen.getByRole("menu")).toBeInTheDocument();

      await user.click(moreButton);
      await waitFor(() => {
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
      });
    });

    it("resets more menu state on menu item click", async () => {
      const user = userEvent.setup();
      const propsWithMoreActions = {
        ...defaultProps,
        onEditClientConfig: vi.fn(),
      };

      render(<WSEditorCommandTree {...propsWithMoreActions} />);

      const moreButton = screen.getByRole("button", { name: /more operations/i });
      await user.click(moreButton);

      const menuItem = screen.getByRole("menuitem", { name: /edit client config/i });
      await user.click(menuItem);

      await waitFor(() => {
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
      });
    });
  });
});
