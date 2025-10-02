import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { render } from "../test-utils";
import WSEditorClientConfigDialog from "../../views/workspace/WSEditorClientConfig";
import { workspaceApi, specsApi, errorHandlerApi } from "../../services";

vi.mock("../../services", () => ({
  workspaceApi: {
    getClientConfig: vi.fn(),
    updateClientConfig: vi.fn(),
  },
  specsApi: {
    getPlanes: vi.fn(),
    getSwaggerModules: vi.fn(),
    getResourceProviders: vi.fn(),
    getProviderResources: vi.fn(),
  },
  errorHandlerApi: {
    getErrorMessage: vi.fn(),
    isHttpError: vi.fn(),
  },
}));

describe("WSEditorClientConfigDialog", () => {
  const mockWorkspaceUrl = "/workspace/test-workspace";
  const mockOnClose = vi.fn();

  const mockPlanes = [
    {
      name: "azure-cli",
      displayName: "Azure CLI",
      moduleOptions: ["storage", "compute"],
    },
  ];

  const mockResourceProviders = ["Microsoft.Storage", "Microsoft.Compute"];

  const mockProviderResources = [
    {
      id: "storageAccounts",
      versions: [
        {
          version: "2021-04-01",
          operations: { get: "GET", put: "PUT" },
          file: "test.json",
          id: "storageAccounts",
          path: "/test",
        },
      ],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    (specsApi.getPlanes as any).mockResolvedValue(mockPlanes);
    (specsApi.getResourceProviders as any).mockResolvedValue(mockResourceProviders);
    (specsApi.getProviderResources as any).mockResolvedValue(mockProviderResources);
    (errorHandlerApi.getErrorMessage as any).mockReturnValue("Mock error message");
    (errorHandlerApi.isHttpError as any).mockReturnValue(false);
  });

  describe("Core Rendering", () => {
    it("should render setup dialog for new config", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
      });
    });

    it("should render modify dialog for existing config", async () => {
      const mockExistingConfig = {
        version: "1.0.0",
        auth: { aad: { scopes: ["https://management.azure.com/.default"] } },
        endpoints: {
          type: "template",
          templates: [{ cloud: "AzureCloud", template: "https://{vaultName}.vault.azure.net" }],
        },
      };
      (workspaceApi.getClientConfig as any).mockResolvedValue(mockExistingConfig);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Modify Client Config")).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
      });
    });

    it("should display error alert when invalidText is set", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("Network error"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(false);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("ResponseError: Mock error message")).toBeInTheDocument();
      });
    });

    it("should switch between template and http-operation tabs", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("By templates")).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
      });

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      const moduleInput = await screen.findByRole("combobox", { name: /Module/i });
      expect(moduleInput).toBeInTheDocument();
    });

    it("should show loading indicator when updating", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByRole("progressbar")).toBeInTheDocument();
      });
    });
  });

  describe("Form Validation", () => {
    beforeEach(async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);
    });

    it("should validate required Azure Cloud template", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
      });

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText("Azure Cloud Endpoint Template is required.")).toBeInTheDocument();
      });
    });

    it("should validate template URL format", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      const templatesTab = screen.getByRole("tab", { name: /By templates/i });
      await user.click(templatesTab);

      const azureCloudInput = await screen.findByLabelText(/Azure Cloud/i);

      await user.clear(azureCloudInput);
      await user.type(azureCloudInput, "invalid-url");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      const errorMessage = await screen.findByText(/Azure Cloud Endpoint Template is invalid./i);
      expect(errorMessage).toBeInTheDocument();
    });

    it("shows error when AAD scopes are empty", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      const azureInput = screen.getByPlaceholderText(
        /Endpoint template in Azure Cloud, e.g. https:\/\/\{vaultName\}\.vault\.azure\.net/i,
      );
      await user.type(azureInput, "https://management.azure.com");

      const aadInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope here/i);
      await user.clear(aadInput);

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      expect(await screen.findByText("MS Entra(AAD) Auth Scopes is required.")).toBeInTheDocument();
    });

    it("should validate cloud metadata selector index when prefix is provided", async () => {
      const user = userEvent.setup();

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      const azureInput = screen.getByPlaceholderText(
        /Endpoint template in Azure Cloud, e.g. https:\/\/\{vaultName\}\.vault\.azure\.net/i,
      );
      await user.type(azureInput, "https://management.azure.com");

      const prefixInput = screen.getByLabelText("Prefix");
      await user.type(prefixInput, "https://{vaultName}");

      const aadInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope here/i);
      await user.type(aadInput, "dummy");
      await user.clear(aadInput);

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(
          screen.getByText((content) => content.includes("Cloud Metadata Selector Index is required.")),
        ).toBeInTheDocument();
      });
    });

    it("should validate required fields in http-operation mode", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText("Plane is required.")).toBeInTheDocument();
      });
    });
  });

  describe("User Interactions", () => {
    beforeEach(async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);
    });

    it("should add AAD scope when add button is clicked", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByLabelText("add")).toBeInTheDocument();
      });

      const addButton = screen.getByLabelText("add");
      await user.click(addButton);

      const aadScopeInputs = screen.getAllByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      expect(aadScopeInputs).toHaveLength(2);
    });

    it("should remove AAD scope when remove button is clicked", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByLabelText("add")).toBeInTheDocument();
      });

      const addButton = screen.getByLabelText("add");
      await user.click(addButton);

      const removeButtons = screen.getAllByLabelText("remove");
      await user.click(removeButtons[0]);

      const aadScopeInputs = screen.getAllByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      expect(aadScopeInputs).toHaveLength(1);
    });

    it("should update AAD scope value when typing", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/)).toBeInTheDocument();
      });

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      expect(aadScopeInput).toHaveValue("https://management.azure.com/.default");
    });

    it("should call onClose with false when Cancel is clicked", async () => {
      const mockExistingConfig = {
        version: "1.0.0",
        auth: { aad: { scopes: ["https://management.azure.com/.default"] } },
        endpoints: {
          type: "template",
          templates: [{ cloud: "AzureCloud", template: "https://{vaultName}.vault.azure.net" }],
        },
      };
      (workspaceApi.getClientConfig as any).mockResolvedValue(mockExistingConfig);

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Cancel")).toBeInTheDocument();
      });

      const cancelButton = screen.getByText("Cancel");
      await user.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalledWith(false);
    });
  });

  describe("State Management", () => {
    it("should initialize with correct default state for new config", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      const azureInput = screen.getByRole("textbox", { name: /Azure Cloud/i });
      expect(azureInput).toBeInTheDocument();

      const aadInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/i);
      expect(aadInput).toBeInTheDocument();
    });

    it("should populate form with existing config data", async () => {
      const mockExistingConfig = {
        version: "1.0.0",
        auth: { aad: { scopes: ["https://management.azure.com/.default"] } },
        endpoints: {
          type: "template",
          templates: [{ cloud: "AzureCloud", template: "https://{vaultName}.vault.azure.net" }],
        },
      };
      (workspaceApi.getClientConfig as any).mockResolvedValue(mockExistingConfig);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByDisplayValue("https://{vaultName}.vault.azure.net")).toBeInTheDocument();
      });

      expect(screen.getByDisplayValue("https://management.azure.com/.default")).toBeInTheDocument();
    });

    it("should handle error state and display error message", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("Network error"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(false);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("ResponseError: Mock error message")).toBeInTheDocument();
      });
    });

    it("should clear error state when switching tabs", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Update")).toBeInTheDocument();
      });

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText("Azure Cloud Endpoint Template is required.")).toBeInTheDocument();
      });

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      const templateTab = screen.getByText("By templates");
      await user.click(templateTab);

      expect(screen.getByText("Azure Cloud Endpoint Template is required.")).toBeInTheDocument();
    });
  });

  describe("API Integration", () => {
    it("should call workspaceApi.getClientConfig on mount", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(workspaceApi.getClientConfig).toHaveBeenCalledWith(mockWorkspaceUrl);
      });
    });

    it("should call specsApi.getPlanes on mount", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(specsApi.getPlanes).toHaveBeenCalled();
      });
    });

    it("should handle successful config update", async () => {
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);
      (workspaceApi.updateClientConfig as any).mockResolvedValue({});

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByLabelText("Azure Cloud")).toBeInTheDocument();
      });

      const azureCloudInput = screen.getByLabelText("Azure Cloud");
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(workspaceApi.updateClientConfig).toHaveBeenCalledWith(
          mockWorkspaceUrl,
          expect.objectContaining({
            templates: expect.arrayContaining([
              expect.objectContaining({
                cloud: "AzureCloud",
                template: "https://{vaultName}.vault.azure.net",
              }),
            ]),
            auth: expect.objectContaining({
              aad: expect.objectContaining({
                scopes: ["https://management.azure.com/.default"],
              }),
            }),
          }),
        );
      });

      expect(mockOnClose).toHaveBeenCalledWith(true);
    });
  });
});
