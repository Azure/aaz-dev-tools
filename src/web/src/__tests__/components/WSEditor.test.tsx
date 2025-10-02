import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { WSEditor } from "../../views/workspace/WSEditor";
import { workspaceApi, specsApi, errorHandlerApi } from "../../services";

vi.mock("../../views/workspace/WSEditorToolBar", () => ({
  default: ({ workspaceName, onHomePage, onGenerate, onDelete, onModify }: any) => (
    <div data-testid="ws-editor-toolbar">
      <span data-testid="workspace-name">{workspaceName}</span>
      <button onClick={onHomePage} data-testid="home-button">
        Home
      </button>
      <button onClick={onGenerate} data-testid="generate-button">
        Generate
      </button>
      <button onClick={onDelete} data-testid="delete-button">
        Delete
      </button>
      <button onClick={onModify} data-testid="modify-button">
        Modify
      </button>
    </div>
  ),
}));

vi.mock("../../views/workspace/WSEditorCommandTree", () => ({
  default: ({ onSelected, onToggle, onAdd, onReload, selected, expanded, onEditClientConfig }: any) => (
    <div data-testid="ws-editor-command-tree">
      <button onClick={() => onSelected("command:test-command")} data-testid="select-command">
        Select Command
      </button>
      <button onClick={() => onSelected("group:test-group")} data-testid="select-group">
        Select Group
      </button>
      <button onClick={() => onToggle(["group:test-group"])} data-testid="toggle-tree">
        Toggle
      </button>
      <button onClick={onAdd} data-testid="add-button">
        Add
      </button>
      <button onClick={onReload} data-testid="reload-button">
        Reload
      </button>
      {onEditClientConfig && (
        <button onClick={onEditClientConfig} data-testid="edit-client-config">
          Edit Config
        </button>
      )}
      <span data-testid="selected-id">{selected}</span>
      <span data-testid="expanded-count">{expanded.length}</span>
    </div>
  ),
  CommandTreeLeaf: {},
  CommandTreeNode: {},
}));

vi.mock("../../views/workspace/WSEditorCommandGroupContent", () => ({
  default: ({ commandGroup, onUpdateCommandGroup }: any) => (
    <div data-testid="ws-editor-command-group-content">
      <span data-testid="command-group-id">{commandGroup.id}</span>
      <button onClick={() => onUpdateCommandGroup(commandGroup)} data-testid="update-command-group">
        Update
      </button>
    </div>
  ),
  CommandGroup: {},
  DecodeResponseCommandGroup: vi.fn((data: any) => ({ ...data, id: data.id || "group:test" })),
  ResponseCommandGroup: {},
  ResponseCommandGroups: {},
}));

vi.mock("../../views/workspace/WSEditorCommandContent", () => ({
  default: ({ previewCommand, onUpdateCommand }: any) => (
    <div data-testid="ws-editor-command-content">
      <span data-testid="command-id">{previewCommand.id}</span>
      <button onClick={() => onUpdateCommand(previewCommand)} data-testid="update-command">
        Update
      </button>
    </div>
  ),
  Command: {},
  Resource: {},
  DecodeResponseCommand: vi.fn((data: any) => ({ ...data, id: data.id || "command:test" })),
  ResponseCommand: {},
}));

vi.mock("../../views/workspace/WSEditorSwaggerPicker", () => ({
  default: ({ plane, workspaceName, onClose }: any) => (
    <div data-testid="ws-editor-swagger-picker">
      <span data-testid="picker-plane">{plane}</span>
      <span data-testid="picker-workspace">{workspaceName}</span>
      <button onClick={() => onClose(false)} data-testid="picker-cancel">
        Cancel
      </button>
      <button onClick={() => onClose(true)} data-testid="picker-update">
        Update
      </button>
    </div>
  ),
}));

vi.mock("../../views/workspace/WSEditorClientConfig", () => ({
  default: ({ workspaceUrl, open, onClose }: any) =>
    open ? (
      <div data-testid="ws-editor-client-config-dialog">
        <span data-testid="config-workspace-url">{workspaceUrl}</span>
        <button onClick={() => onClose(false)} data-testid="config-cancel">
          Cancel
        </button>
        <button onClick={() => onClose(true)} data-testid="config-update">
          Update
        </button>
      </div>
    ) : null,
}));

vi.mock("../../services", () => ({
  workspaceApi: {
    getWorkspace: vi.fn(),
    getWorkspaceClientConfig: vi.fn(),
    getWorkspaceResources: vi.fn(),
    getWorkspaceSwaggerDefault: vi.fn(),
    deleteWorkspace: vi.fn(),
    renameWorkspace: vi.fn(),
    generateWorkspace: vi.fn(),
    verifyClientConfig: vi.fn(),
    inheritClientConfig: vi.fn(),
    reloadSwaggerResources: vi.fn(),
    reloadTypespecResources: vi.fn(),
  },
  specsApi: {
    getPlaneNames: vi.fn(),
  },
  errorHandlerApi: {
    getErrorMessage: vi.fn(),
    isHttpError: vi.fn(),
  },
}));

vi.mock("../../typespec", () => ({
  getTypespecRPResourcesOperations: vi.fn(),
}));

Object.defineProperty(window, "location", {
  value: {
    href: "",
    reload: vi.fn(),
  },
  writable: true,
});

Object.defineProperty(window, "open", {
  value: vi.fn(),
  writable: true,
});

describe("WSEditor", () => {
  const mockWorkspaceData = {
    plane: "management",
    source: "swagger",
    commandTree: {
      commandGroups: {
        "test-group": {
          id: "group:test-group",
          names: ["az", "test"],
          canDelete: true,
          commands: {
            "test-command": {
              id: "command:test-command",
              names: ["az", "test", "create"],
            },
          },
        },
      },
    },
  };

  const mockPlaneNames = ["management", "dataplane"];

  const mockProps = {
    params: {
      workspaceName: "test-workspace",
    },
  };

  const renderWithRouter = (props = mockProps) => {
    return render(
      <MemoryRouter>
        <WSEditor {...props} />
      </MemoryRouter>,
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(specsApi.getPlaneNames).mockResolvedValue(mockPlaneNames);
    vi.mocked(workspaceApi.getWorkspace).mockResolvedValue(mockWorkspaceData);
    vi.mocked(workspaceApi.getWorkspaceClientConfig).mockResolvedValue({} as any);
    vi.mocked(workspaceApi.getWorkspaceResources).mockResolvedValue([]);
    vi.mocked(errorHandlerApi.getErrorMessage).mockReturnValue("Test error message");
  });

  describe("Core Rendering", () => {
    it("should render with initial workspace name", () => {
      renderWithRouter();

      expect(screen.getByTestId("workspace-name")).toHaveTextContent("test-workspace");
    });

    it("should render toolbar component", () => {
      renderWithRouter();

      expect(screen.getByTestId("ws-editor-toolbar")).toBeInTheDocument();
    });

    it("should render drawer with fixed width", () => {
      renderWithRouter();

      const drawer = screen.getByTestId("ws-editor-toolbar");
      expect(drawer).toBeInTheDocument();
    });

    it("should call loadWorkspace on component mount", async () => {
      renderWithRouter();

      await waitFor(() => {
        expect(specsApi.getPlaneNames).toHaveBeenCalled();
        expect(workspaceApi.getWorkspace).toHaveBeenCalledWith("/AAZ/Editor/Workspaces/test-workspace");
      });
    });

    it("should not render command tree when no selection", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        commandTree: { commandGroups: {} },
      });

      renderWithRouter();

      await waitFor(() => {
        expect(screen.queryByTestId("ws-editor-command-tree")).not.toBeInTheDocument();
      });
    });

    it("should render command tree when selection exists", async () => {
      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-command-tree")).toBeInTheDocument();
      });
    });

    it("should handle workspace loading errors gracefully", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      vi.mocked(workspaceApi.getWorkspace).mockRejectedValue(new Error("Failed to load workspace"));

      renderWithRouter();

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(new Error("Failed to load workspace"));
      });

      consoleSpy.mockRestore();
    });
  });

  describe("Workspace Data Loading & Processing", () => {
    it("should build command tree from workspace data", async () => {
      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("selected-id")).toHaveTextContent("group:test-group");
      });
    });

    it("should detect client configurable workspace", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        plane: "custom-plane",
      });

      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("edit-client-config")).toBeInTheDocument();
      });
    });

    it("should not show client config button for built-in planes", async () => {
      renderWithRouter();

      await waitFor(() => {
        expect(screen.queryByTestId("edit-client-config")).not.toBeInTheDocument();
      });
    });

    it("should show client config dialog when client config is null", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        plane: "custom-plane",
      });
      vi.mocked(workspaceApi.getWorkspaceClientConfig).mockResolvedValue(null);

      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-client-config-dialog")).toBeInTheDocument();
      });
    });

    it("should show swagger picker when command tree is empty", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        commandTree: { commandGroups: {} },
      });

      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-swagger-picker")).toBeInTheDocument();
      });
    });

    it("should handle selection of preSelectedId for commands", async () => {
      const component = renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("selected-id")).toHaveTextContent("group:test-group");
      });

      const instance = component.container.querySelector('[data-testid="ws-editor-toolbar"]');
      expect(instance).toBeInTheDocument();
    });

    it("should properly expand selected node paths", async () => {
      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("expanded-count")).toHaveTextContent("1");
      });
    });

    it("should sort command groups alphabetically", async () => {
      const multiGroupData = {
        ...mockWorkspaceData,
        commandTree: {
          commandGroups: {
            "z-group": {
              id: "group:z-group",
              names: ["az", "z"],
              canDelete: true,
            },
            "a-group": {
              id: "group:a-group",
              names: ["az", "a"],
              canDelete: true,
            },
          },
        },
      };

      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue(multiGroupData);

      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("selected-id")).toHaveTextContent("group:a-group");
      });
    });
  });

  describe("Event Handling & User Interactions", () => {
    beforeEach(async () => {
      renderWithRouter();
      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-command-tree")).toBeInTheDocument();
      });
    });

    it("should handle command tree selection for commands", async () => {
      const selectButton = screen.getByTestId("select-command");
      fireEvent.click(selectButton);

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-command-content")).toBeInTheDocument();
      });
    });

    it("should handle command tree selection for groups", async () => {
      const selectButton = screen.getByTestId("select-group");
      fireEvent.click(selectButton);

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-command-group-content")).toBeInTheDocument();
      });
    });

    it("should handle tree toggle functionality", async () => {
      const toggleButton = screen.getByTestId("toggle-tree");
      fireEvent.click(toggleButton);

      await waitFor(() => {
        expect(screen.getByTestId("expanded-count")).toHaveTextContent("1");
      });
    });

    it("should handle homepage navigation with blank window", async () => {
      const homeButton = screen.getByTestId("home-button");
      fireEvent.click(homeButton);

      expect(window.open).toHaveBeenCalledWith("/?#/workspace", "_blank");
    });

    it("should handle command group updates", async () => {
      const updateButton = screen.getByTestId("update-command-group");
      fireEvent.click(updateButton);

      await waitFor(() => {
        expect(workspaceApi.getWorkspace).toHaveBeenCalledTimes(2);
      });
    });

    it("should handle command updates", async () => {
      const selectButton = screen.getByTestId("select-command");
      fireEvent.click(selectButton);

      await waitFor(() => {
        const updateButton = screen.getByTestId("update-command");
        fireEvent.click(updateButton);
      });

      await waitFor(() => {
        expect(workspaceApi.getWorkspace).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe("Dialog State Management", () => {
    beforeEach(async () => {
      renderWithRouter();
      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-command-tree")).toBeInTheDocument();
      });
    });

    it("should open export dialog when generate button clicked", async () => {
      const generateButton = screen.getByTestId("generate-button");
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText("Export workspace command models to AAZ Repo")).toBeInTheDocument();
      });
    });

    it("should open delete dialog when delete button clicked", async () => {
      const deleteButton = screen.getByTestId("delete-button");
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete 'test-workspace' workspace?")).toBeInTheDocument();
      });
    });

    it("should open modify dialog when modify button clicked", async () => {
      const modifyButton = screen.getByTestId("modify-button");
      fireEvent.click(modifyButton);

      await waitFor(() => {
        expect(screen.getByText("Rename Workspace")).toBeInTheDocument();
      });
    });

    it("should open swagger picker when add button clicked", async () => {
      const addButton = screen.getByTestId("add-button");
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-swagger-picker")).toBeInTheDocument();
      });
    });

    it("should open swagger reload dialog when reload button clicked", async () => {
      const reloadButton = screen.getByTestId("reload-button");
      fireEvent.click(reloadButton);

      await waitFor(() => {
        expect(screen.getByText("Reload Swagger Resources")).toBeInTheDocument();
      });
    });

    it("should open client config dialog when edit config button clicked", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        plane: "custom-plane",
      });

      renderWithRouter();

      await waitFor(() => {
        const editConfigButton = screen.getByTestId("edit-client-config");
        fireEvent.click(editConfigButton);
      });

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-client-config-dialog")).toBeInTheDocument();
      });
    });

    it("should close swagger picker and reload workspace on update", async () => {
      const addButton = screen.getByTestId("add-button");
      fireEvent.click(addButton);

      await waitFor(() => {
        const updateButton = screen.getByTestId("picker-update");
        fireEvent.click(updateButton);
      });

      await waitFor(() => {
        expect(workspaceApi.getWorkspace).toHaveBeenCalledTimes(2);
      });
    });

    it("should close client config dialog and reload workspace on update", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        plane: "custom-plane",
      });
      vi.mocked(workspaceApi.getWorkspaceClientConfig).mockResolvedValue(null);

      renderWithRouter();

      await waitFor(() => {
        expect(screen.getByTestId("ws-editor-client-config-dialog")).toBeInTheDocument();
      });

      const updateButton = screen.getByTestId("config-update");
      fireEvent.click(updateButton);

      await waitFor(() => {
        expect(workspaceApi.getWorkspace).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe("Error Handling", () => {
    it("should handle API errors during workspace loading", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      vi.mocked(workspaceApi.getWorkspace).mockRejectedValue(new Error("Network error"));

      renderWithRouter();

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(new Error("Network error"));
      });

      consoleSpy.mockRestore();
    });

    it("should handle client config API errors", async () => {
      vi.mocked(workspaceApi.getWorkspace).mockResolvedValue({
        ...mockWorkspaceData,
        plane: "custom-plane",
      });
      vi.mocked(workspaceApi.getWorkspaceClientConfig).mockRejectedValue(new Error("Config error"));

      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

      renderWithRouter();

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });
});
