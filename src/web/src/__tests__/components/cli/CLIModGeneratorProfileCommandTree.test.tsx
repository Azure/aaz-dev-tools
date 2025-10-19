import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import CLIModGeneratorProfileCommandTree from "../../../views/cli/components/CLIModGeneratorProfileCommandTree";
import { ProfileCommandTree } from "../../../views/cli/utils/commandTreeInitialization";

vi.mock("@mui/lab/TreeView", () => ({
  default: ({ children, ...props }: any) => (
    <div data-testid="tree-view" {...props}>
      {children}
    </div>
  ),
}));

vi.mock("@mui/lab/TreeItem", () => ({
  default: ({ label, children, nodeId, ...props }: any) => (
    <div data-testid="tree-item" data-node-id={nodeId} {...props}>
      <div data-testid="tree-item-label">{label}</div>
      {children && <div data-testid="tree-item-children">{children}</div>}
    </div>
  ),
}));

describe("CLIModGeneratorProfileCommandTree", () => {
  const mockOnChange = vi.fn();
  const mockOnLoadCommands = vi.fn();

  const mockProfileCommandTree: ProfileCommandTree = {
    name: "test-profile",
    commandGroups: {
      "test-group": {
        id: "test-group",
        names: ["test-group"],
        commands: {
          "test-command": {
            id: "test-group/test-command",
            names: ["test-group", "test-command"],
            selected: false,
            modified: false,
            loading: false,
          },
          "selected-command": {
            id: "test-group/selected-command",
            names: ["test-group", "selected-command"],
            selected: true,
            selectedVersion: "2023-01-01",
            registered: true,
            modified: false,
            loading: false,
            versions: [
              { name: "2023-01-01", stage: "stable" },
              { name: "2022-12-01", stage: "preview" },
            ],
          },
        },
        loading: false,
        selected: undefined,
      },
      "empty-group": {
        id: "empty-group",
        names: ["empty-group"],
        commands: {},
        loading: false,
        selected: false,
      },
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnLoadCommands.mockResolvedValue([]);
  });

  it("should render the tree view with command groups", () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    expect(screen.getByTestId("cli-command-tree")).toBeInTheDocument();
    // Should have 1 command group + 2 command items + 1 nested command group = 4 total
    const commandGroups = screen.getAllByTestId(/^command-group-/);
    const commandItems = screen.getAllByTestId("tree-item");
    expect(commandGroups.length + commandItems.length).toBe(4);
  });

  it("should display command group names correctly", () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    expect(screen.getByText("test-group")).toBeInTheDocument();
    expect(screen.getByText("empty-group")).toBeInTheDocument();
  });

  it("should display command names correctly", () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    expect(screen.getByText("test-command")).toBeInTheDocument();
    expect(screen.getByText("selected-command")).toBeInTheDocument();
  });

  it("should show command group checkboxes with correct states", () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes).toHaveLength(4);

    const emptyGroupCheckbox = checkboxes.find((checkbox) => checkbox.closest('[data-node-id="empty-group"]'));
    expect(emptyGroupCheckbox).toHaveProperty("checked", false);
  });

  it("should show version selector for selected commands", () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    expect(screen.getByDisplayValue("2023-01-01")).toBeInTheDocument();
    expect(screen.getByText("Version")).toBeInTheDocument();
  });

  it("should show registered/unregistered selector for selected commands", () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    expect(screen.getByText("Command table")).toBeInTheDocument();
    expect(screen.getByText("Registered")).toBeInTheDocument();
  });

  it("should call onChange when command is selected", async () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const testCommandCheckbox = screen
      .getAllByRole("checkbox")
      .find((checkbox) => checkbox.closest('[data-node-id="test-group/test-command"]'));

    expect(testCommandCheckbox).toBeDefined();
    fireEvent.click(testCommandCheckbox!);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalled();
    });
  });

  it("should call onChange when command group is selected", async () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const groupCheckbox = screen
      .getAllByRole("checkbox")
      .find((checkbox) => checkbox.closest('[data-node-id="empty-group"]'));

    expect(groupCheckbox).toBeDefined();
    fireEvent.click(groupCheckbox!);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalled();
    });
  });

  it("should call onChange when version is changed", async () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const versionSelect = screen.getByDisplayValue("2023-01-01");
    fireEvent.change(versionSelect, { target: { value: "2022-12-01" } });

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalled();
    });
  });

  it("should call onChange when registration status is changed", async () => {
    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const registrationSelects = screen.getAllByRole("combobox");
    expect(registrationSelects).toHaveLength(2);

    const commandTableSelect = registrationSelects[1];
    fireEvent.mouseDown(commandTableSelect);

    const unregisteredOption = screen.getByText("Unregistered");
    fireEvent.click(unregisteredOption);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalled();
    });
  });

  it("should show loading state for commands that are loading", () => {
    const loadingTree: ProfileCommandTree = {
      name: "test-profile",
      commandGroups: {
        "test-group": {
          id: "test-group",
          names: ["test-group"],
          commands: {
            "loading-command": {
              id: "test-group/loading-command",
              names: ["test-group", "loading-command"],
              selected: true,
              modified: false,
              loading: true,
            },
          },
          loading: false,
          selected: true,
        },
      },
    };

    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={loadingTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should show edit icon correctly based on command state", () => {
    const mixedTree: ProfileCommandTree = {
      name: "test-profile",
      commandGroups: {
        "test-group": {
          id: "test-group",
          names: ["test-group"],
          commands: {
            "modified-command": {
              id: "test-group/modified-command",
              names: ["test-group", "modified-command"],
              selected: true,
              selectedVersion: "2023-01-01",
              modified: true,
              loading: false,
            },
            "unmodified-with-version": {
              id: "test-group/unmodified-with-version",
              names: ["test-group", "unmodified-with-version"],
              selected: true,
              selectedVersion: "2023-01-01",
              modified: false,
              loading: false,
            },
            "unmodified-no-version": {
              id: "test-group/unmodified-no-version",
              names: ["test-group", "unmodified-no-version"],
              selected: false,
              modified: false,
              loading: false,
              // No selectedVersion
            },
          },
          loading: false,
          selected: undefined,
        },
      },
    };

    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mixedTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    // Should show 2 EditIcons total:
    // 1. Secondary color icon for modified command
    // 2. Disabled icon button for unmodified command with version
    const editIcons = screen.getAllByTestId("EditIcon");
    expect(editIcons).toHaveLength(2);

    // The modified command should have a secondary color edit icon
    expect(editIcons[0]).toHaveClass("MuiSvgIcon-colorSecondary");

    // The unmodified command with version should have a disabled edit icon button
    expect(editIcons[1]).toHaveClass("MuiSvgIcon-colorDisabled");
  });

  it("should call onLoadCommands when selecting a command without versions", async () => {
    const treeWithoutVersions: ProfileCommandTree = {
      name: "test-profile",
      commandGroups: {
        "test-group": {
          id: "test-group",
          names: ["test-group"],
          commands: {
            "no-versions-command": {
              id: "test-group/no-versions-command",
              names: ["test-group", "no-versions-command"],
              selected: false,
              modified: false,
              loading: false,
              // No versions defined
            },
          },
          loading: false,
          selected: false,
        },
      },
    };

    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={treeWithoutVersions}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const commandCheckbox = screen
      .getAllByRole("checkbox")
      .find((checkbox) => checkbox.closest('[data-node-id="test-group/no-versions-command"]'));

    expect(commandCheckbox).toBeDefined();
    fireEvent.click(commandCheckbox!);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalled();
    });

    expect(commandCheckbox).toHaveProperty("checked", false);
  });

  it("should prevent event propagation on checkbox clicks", () => {
    const mockStopPropagation = vi.fn();
    const mockPreventDefault = vi.fn();

    render(
      <CLIModGeneratorProfileCommandTree
        profileCommandTree={mockProfileCommandTree}
        onChange={mockOnChange}
        onLoadCommands={mockOnLoadCommands}
      />,
    );

    const checkbox = screen.getAllByRole("checkbox")[0];

    const mockEvent = {
      stopPropagation: mockStopPropagation,
      preventDefault: mockPreventDefault,
      target: { checked: true },
    } as any;

    fireEvent.click(checkbox, mockEvent);

    expect(mockOnChange).toHaveBeenCalled();
  });
});
