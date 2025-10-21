import { describe, it, expect, beforeEach, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { render } from "../test-utils";
import WorkspaceSelector from "../../views/workspace/components/WorkspaceInstruction/WorkspaceSelector";
import { workspaceApi } from "../../services";

vi.mock("../../services", () => ({
  workspaceApi: {
    getWorkspaces: vi.fn(),
    createWorkspace: vi.fn(),
    deleteWorkspace: vi.fn(),
    renameWorkspace: vi.fn(),
  },
  specsApi: {
    getPlanes: vi.fn(),
    getModulesForPlane: vi.fn(),
    getResourceProviders: vi.fn(),
  },
  errorHandlerApi: {
    getErrorMessage: vi.fn(),
  },
}));

describe("Workspace Management", () => {
  const mockWorkspaces = [
    {
      name: "test-workspace-1",
      plane: "azure-cli",
      modNames: "storage",
      resourceProvider: "Microsoft.Storage",
      lastModified: new Date("2024-01-01"),
      url: "/workspace/test-workspace-1",
      folder: "/workspaces/test-workspace-1",
    },
    {
      name: "test-workspace-2",
      plane: "azure-cli",
      modNames: "compute",
      resourceProvider: "Microsoft.Compute",
      lastModified: new Date("2024-01-02"),
      url: "/workspace/test-workspace-2",
      folder: "/workspaces/test-workspace-2",
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    (workspaceApi.getWorkspaces as any).mockResolvedValue(mockWorkspaces);
  });

  describe("WorkspaceSelector Component", () => {
    it("should render workspace selector with label", () => {
      render(<WorkspaceSelector name="Select Workspace" />);

      expect(screen.getByLabelText("Select Workspace")).toBeInTheDocument();
    });

    it("should load and display workspaces on mount", async () => {
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalledTimes(1);
      });
    });

    it("should allow user to open workspace selection dropdown", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);

      expect(autocomplete).toBeInTheDocument();
    });

    it("should show create option when typing new workspace name", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "new-workspace");

      await waitFor(() => {
        expect(screen.getByText('Create "new-workspace"')).toBeInTheDocument();
      });
    });

    it("should handle workspace loading errors gracefully", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      (workspaceApi.getWorkspaces as any).mockRejectedValue(new Error("Network error"));

      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error));
      consoleSpy.mockRestore();
    });

    it("should update URL when workspace is selected", async () => {
      delete (window as any).location;
      window.location = { href: "" } as any;

      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      expect(workspaceApi.getWorkspaces).toHaveBeenCalledTimes(1);
    });

    it("should filter workspaces based on input text", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "test-workspace-1");

      await waitFor(() => {
        expect(screen.getByText("test-workspace-1")).toBeInTheDocument();
        expect(screen.queryByText("test-workspace-2")).not.toBeInTheDocument();
      });
    });

    it("should not show create option for existing workspace names", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "test-workspace-1");

      await waitFor(() => {
        expect(screen.getByText("test-workspace-1")).toBeInTheDocument();
        expect(screen.queryByText('Create "test-workspace-1"')).not.toBeInTheDocument();
      });
    });

    it("should handle partial matching when filtering workspaces", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "workspace");

      await waitFor(() => {
        expect(screen.getByText("test-workspace-1")).toBeInTheDocument();
        expect(screen.getByText("test-workspace-2")).toBeInTheDocument();
        expect(screen.getByText('Create "workspace"')).toBeInTheDocument();
      });
    });

    it("should show all workspaces when dropdown is opened without input", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);

      await waitFor(() => {
        expect(screen.getByText("test-workspace-1")).toBeInTheDocument();
        expect(screen.getByText("test-workspace-2")).toBeInTheDocument();
      });
    });

    it("should not show create option when input is empty", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);

      await waitFor(() => {
        expect(screen.queryByText(/Create "/)).not.toBeInTheDocument();
      });
    });

    it("should handle case-insensitive filtering correctly", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Select Workspace" />);

      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "TEST-WORKSPACE");

      await waitFor(() => {
        expect(screen.getByText("test-workspace-1")).toBeInTheDocument();
        expect(screen.getByText("test-workspace-2")).toBeInTheDocument();
        expect(screen.getByText('Create "TEST-WORKSPACE"')).toBeInTheDocument();
      });
    });
  });

  describe("Workspace API Integration", () => {
    it("should fetch workspaces successfully", async () => {
      const workspaces = await workspaceApi.getWorkspaces();

      expect(workspaces).toEqual(mockWorkspaces);
      expect(workspaceApi.getWorkspaces).toHaveBeenCalledTimes(1);
    });

    it("should create new workspace successfully", async () => {
      const newWorkspaceData = {
        name: "new-workspace",
        plane: "azure-cli",
        modNames: "storage",
        resourceProvider: "Microsoft.Storage",
        source: "OpenAPI",
      };

      const expectedWorkspace = {
        name: "new-workspace",
        plane: "azure-cli",
        modNames: "storage",
        resourceProvider: "Microsoft.Storage",
        lastModified: new Date("2024-01-03"),
        url: "/workspace/new-workspace",
        folder: "/workspaces/new-workspace",
      };

      (workspaceApi.createWorkspace as any).mockResolvedValue(expectedWorkspace);

      const result = await workspaceApi.createWorkspace(newWorkspaceData);

      expect(workspaceApi.createWorkspace).toHaveBeenCalledWith(newWorkspaceData);
      expect(result).toEqual(expectedWorkspace);
    });

    it("should handle workspace creation errors", async () => {
      const newWorkspaceData = {
        name: "invalid-workspace",
        plane: "azure-cli",
        modNames: "storage",
        resourceProvider: "Microsoft.Storage",
        source: "OpenAPI",
      };

      const error = new Error("Workspace name already exists");
      (workspaceApi.createWorkspace as any).mockRejectedValue(error);

      await expect(workspaceApi.createWorkspace(newWorkspaceData)).rejects.toThrow("Workspace name already exists");
    });

    it("should delete workspace successfully", async () => {
      (workspaceApi.deleteWorkspace as any).mockResolvedValue(undefined);

      await workspaceApi.deleteWorkspace("test-workspace-1");

      expect(workspaceApi.deleteWorkspace).toHaveBeenCalledWith("test-workspace-1");
    });

    it("should rename workspace successfully", async () => {
      const expectedResult = { name: "renamed-workspace" };
      (workspaceApi.renameWorkspace as any).mockResolvedValue(expectedResult);

      const result = await workspaceApi.renameWorkspace("/workspace/test-workspace-1", "renamed-workspace");

      expect(workspaceApi.renameWorkspace).toHaveBeenCalledWith("/workspace/test-workspace-1", "renamed-workspace");
      expect(result).toEqual(expectedResult);
    });
  });

  describe("WorkspaceCreateDialog Component", () => {
    it("should pre-select the first plane after planes are loaded in the create dialog", async () => {
      const user = userEvent.setup();
      const mockPlanes = [
        { name: "MgmtClient", displayName: "Control plane", moduleOptions: ["mod1", "mod2"] },
        { name: "DataPlaneClient", displayName: "Data plane", moduleOptions: ["mod3"] },
      ];
      const { specsApi } = await import("../../services");
      (specsApi.getPlanes as any).mockResolvedValue(mockPlanes);

      render(<WorkspaceSelector name="Select Workspace" />);

      // Wait for workspaces to load
      await waitFor(() => {
        expect(workspaceApi.getWorkspaces).toHaveBeenCalled();
      });

      // Type a new workspace name to trigger create option
      const autocomplete = screen.getByLabelText("Select Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "new-test-workspace");

      // Click on the create option
      const createOption = await screen.findByText('Create "new-test-workspace"');
      await user.click(createOption);

      // Wait for the dialog to appear
      await screen.findByText("Create a new workspace");

      // Wait for the getPlanes API to be called
      await waitFor(() => {
        expect(specsApi.getPlanes).toHaveBeenCalled();
      });

      // The plane dropdown should be populated with the first plane
      const planeDropdown = await screen.findByLabelText(/Plane/i);
      expect(planeDropdown).toHaveValue("Control plane");
    });
  });
});
