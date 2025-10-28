import { describe, it, expect, beforeEach, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { render } from "../test-utils";
import WSEditorClientConfigDialog from "../../views/workspace/components/WSEditor/WSEditorClientConfig";
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
    (specsApi.getSwaggerModules as any).mockResolvedValue(["storage", "compute"]);
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
        expect(screen.getByText("Module is required.")).toBeInTheDocument();
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
        expect(screen.getByPlaceholderText(/Endpoint template in Azure Cloud/i)).toBeInTheDocument();
      });

      const azureCloudInput = screen.getByPlaceholderText(/Endpoint template in Azure Cloud/i);
      await user.clear(azureCloudInput);
      await user.type(azureCloudInput, "https://vault123.vault.azure.net");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.clear(aadScopeInput);
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
                template: "https://vault123.vault.azure.net",
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

  describe("Resource ID Cascade Loading Bug", () => {
    it("should populate Resource ID options immediately when first API version is auto-selected", async () => {
      const user = userEvent.setup();

      // Mock data with aligned module/provider selection
      const mockSwaggerModules = ["addons"];
      const mockResourceProvidersForAddons = ["Microsoft.Addons"];
      const mockProviderResourcesWithMultipleVersions = [
        {
          id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
          opGroup: "SupportPlanType",
          url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded1",
          versions: [
            {
              version: "2018-03-01",
              operations: {
                SupportPlanTypes_CreateOrUpdate: "put",
                SupportPlanTypes_Delete: "delete",
                SupportPlanTypes_Get: "get",
              },
              file: "addons-swagger.json",
              id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
              path: "/subscriptions/{subscriptionId}/providers/Microsoft.Addons/supportProviders/{providerName}/supportPlanTypes/{planTypeName}",
              url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded1/V/version1",
            },
            {
              version: "2017-05-15",
              operations: {
                SupportPlanTypes_CreateOrUpdate: "put",
                SupportPlanTypes_Delete: "delete",
                SupportPlanTypes_Get: "get",
              },
              file: "Addons.json",
              id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
              path: "/subscriptions/{subscriptionId}/providers/Microsoft.Addons/supportProviders/{providerName}/supportPlanTypes/{planTypeName}",
              url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded1/V/version2",
            },
          ],
        },
        {
          id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes",
          opGroup: "CanonicalSupportPlanType",
          url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded2",
          versions: [
            {
              version: "2017-05-15",
              operations: { CanonicalSupportPlanTypes_Get: "get" },
              file: "Addons.json",
              id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes",
              path: "/subscriptions/{subscriptionId}/providers/Microsoft.Addons/supportProviders/{providerName}/supportPlanTypes",
              url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded2/V/version1",
            },
          ],
        },
      ];

      // Setup complete mocks for cascade loading
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);
      (specsApi.getSwaggerModules as any).mockResolvedValue(mockSwaggerModules);
      (specsApi.getResourceProviders as any).mockResolvedValue(mockResourceProvidersForAddons);
      (specsApi.getProviderResources as any).mockResolvedValue(mockProviderResourcesWithMultipleVersions);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      // Wait for initial load and switch to http-operation tab
      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      // Wait for Module selector to be available and select aligned module
      await waitFor(() => {
        expect(screen.getByRole("combobox", { name: /Module/i })).toBeInTheDocument();
      });

      const moduleInput = screen.getByRole("combobox", { name: /Module/i });
      await user.click(moduleInput);
      await user.type(moduleInput, "addons{enter}");

      // Wait for Resource Provider selector to be available and select aligned provider
      await waitFor(() => {
        expect(screen.getByRole("combobox", { name: /Resource Provider/i })).toBeInTheDocument();
      });

      const resourceProviderInput = screen.getByRole("combobox", { name: /Resource Provider/i });
      await user.click(resourceProviderInput);
      await user.type(resourceProviderInput, "Microsoft.Addons{enter}");

      // Wait for API Version selector to be populated - this should auto-select the first version (2018-03-01)
      await waitFor(() => {
        expect(screen.getByRole("combobox", { name: /API Version/i })).toBeInTheDocument();
      });

      // Check that the first version is auto-selected and Resource ID options are populated
      await waitFor(() => {
        const resourceIdSelector = screen.getByRole("combobox", { name: /Resource ID/i });
        expect(resourceIdSelector).toBeInTheDocument();
      });

      // The bug: Resource ID dropdown should be populated immediately when the first API version is auto-selected
      // Currently it stays empty until you manually switch versions
      const resourceIdInput = screen.getByRole("combobox", { name: /Resource ID/i });
      await user.click(resourceIdInput);

      // This should show the resource options for 2018-03-01 version immediately
      await waitFor(
        () => {
          expect(
            screen.getByText("/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}"),
          ).toBeInTheDocument();
        },
        { timeout: 1000 },
      );
    });

    it("should update Resource ID options when switching between API versions", async () => {
      const user = userEvent.setup();

      // Use the same aligned mock data
      const mockSwaggerModules = ["addons"];
      const mockResourceProvidersForAddons = ["Microsoft.Addons"];
      const mockProviderResourcesWithMultipleVersions = [
        {
          id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
          opGroup: "SupportPlanType",
          url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded1",
          versions: [
            {
              version: "2018-03-01",
              operations: {
                SupportPlanTypes_CreateOrUpdate: "put",
                SupportPlanTypes_Delete: "delete",
                SupportPlanTypes_Get: "get",
              },
              file: "addons-swagger.json",
              id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
              path: "/subscriptions/{subscriptionId}/providers/Microsoft.Addons/supportProviders/{providerName}/supportPlanTypes/{planTypeName}",
              url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded1/V/version1",
            },
            {
              version: "2017-05-15",
              operations: {
                SupportPlanTypes_CreateOrUpdate: "put",
                SupportPlanTypes_Delete: "delete",
                SupportPlanTypes_Get: "get",
              },
              file: "Addons.json",
              id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
              path: "/subscriptions/{subscriptionId}/providers/Microsoft.Addons/supportProviders/{providerName}/supportPlanTypes/{planTypeName}",
              url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded1/V/version2",
            },
          ],
        },
        {
          id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes",
          opGroup: "CanonicalSupportPlanType",
          url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded2",
          versions: [
            {
              version: "2017-05-15",
              operations: { CanonicalSupportPlanTypes_Get: "get" },
              file: "Addons.json",
              id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes",
              path: "/subscriptions/{subscriptionId}/providers/Microsoft.Addons/supportProviders/{providerName}/supportPlanTypes",
              url: "/Swagger/Specs/mgmt-plane/addons/ResourceProviders/Microsoft.Addons/Resources/encoded2/V/version1",
            },
          ],
        },
      ];

      // Setup complete mocks for cascade loading
      (workspaceApi.getClientConfig as any).mockRejectedValue(new Error("404"));
      (errorHandlerApi.isHttpError as any).mockReturnValue(true);
      (specsApi.getSwaggerModules as any).mockResolvedValue(mockSwaggerModules);
      (specsApi.getResourceProviders as any).mockResolvedValue(mockResourceProvidersForAddons);
      (specsApi.getProviderResources as any).mockResolvedValue(mockProviderResourcesWithMultipleVersions);

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      // Navigate to resource property tab and select module/provider
      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      const moduleInput = await screen.findByRole("combobox", { name: /Module/i });
      await user.click(moduleInput);
      await user.type(moduleInput, "addons{enter}");

      const resourceProviderInput = await screen.findByRole("combobox", { name: /Resource Provider/i });
      await user.click(resourceProviderInput);
      await user.type(resourceProviderInput, "Microsoft.Addons{enter}");

      // Wait for API Version to be auto-selected (2018-03-01 should be first)
      await waitFor(() => {
        expect(screen.getByRole("combobox", { name: /API Version/i })).toBeInTheDocument();
      });

      // Switch to the second API version (2017-05-15)
      const apiVersionInput = screen.getByRole("combobox", { name: /API Version/i });
      await user.click(apiVersionInput);
      await user.type(apiVersionInput, "2017-05-15{enter}");

      // Check that Resource ID options are now populated for 2017-05-15
      await waitFor(() => {
        const resourceIdInput = screen.getByRole("combobox", { name: /Resource ID/i });
        expect(resourceIdInput).toBeInTheDocument();
      });

      const resourceIdInput = screen.getByRole("combobox", { name: /Resource ID/i });
      await user.click(resourceIdInput);

      // Should show 2 resource options for 2017-05-15
      await waitFor(() => {
        expect(
          screen.getByText("/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}"),
        ).toBeInTheDocument();
        expect(
          screen.getByText("/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes"),
        ).toBeInTheDocument();
      });

      // Switch back to first API version (2018-03-01)
      await user.click(apiVersionInput);
      await user.type(apiVersionInput, "2018-03-01{enter}");

      // Now Resource ID should show only 1 option for 2018-03-01
      await user.click(resourceIdInput);

      await waitFor(() => {
        expect(
          screen.getByText("/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}"),
        ).toBeInTheDocument();
        // The second resource should not be available for 2018-03-01
        expect(
          screen.queryByText("/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes"),
        ).not.toBeInTheDocument();
      });
    });
  });
});
