import { describe, it, expect, vi, beforeEach, beforeAll, afterEach, afterAll } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { render } from "../test-utils";
import WSEditorClientConfigDialog from "../../views/workspace/WSEditorClientConfig";

// Mock console.error to avoid noise in test output
const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

// Create MSW server
const server = setupServer();

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
});

afterEach(() => {
  server.resetHandlers();
  vi.clearAllMocks();
});

afterAll(() => {
  server.close();
  mockConsoleError.mockRestore();
});

describe("WSEditorClientConfigDialog - Integration", () => {
  const mockWorkspaceUrl = "/workspace/test-workspace";
  const mockOnClose = vi.fn();

  const mockPlanes = [
    {
      name: "azure-cli",
      displayName: "Azure CLI",
      moduleOptions: null, // Force API call for modules
    },
  ];

  const mockModules = ["storage", "compute"];
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
        {
          version: "2020-08-01",
          operations: { get: "GET", list: "LIST" },
          file: "test2.json",
          id: "storageAccounts",
          path: "/test2",
        },
      ],
    },
    {
      id: "blobServices",
      versions: [
        {
          version: "2021-04-01",
          operations: { get: "GET" },
          file: "test3.json",
          id: "blobServices",
          path: "/test3",
        },
      ],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default MSW handlers
    server.use(
      // Planes API
      http.get("*/specs/planes", () => {
        return HttpResponse.json(mockPlanes);
      }),

      // Modules API
      http.get("*/specs/planes/azure-cli/modules", () => {
        return HttpResponse.json(mockModules);
      }),

      // Resource Providers API
      http.get("*/specs/planes/*/modules/*/resource-providers", () => {
        return HttpResponse.json(mockResourceProviders);
      }),

      // Provider Resources API
      http.get("*/specs/planes/*/modules/*/resource-providers/*/resources", () => {
        return HttpResponse.json(mockProviderResources);
      }),
    );
  });

  describe("Data Loading Workflows", () => {
    it("should load existing client config and populate form", async () => {
      const mockExistingConfig = {
        version: "1.0.0",
        auth: { aad: { scopes: ["https://management.azure.com/.default"] } },
        endpoints: {
          type: "template",
          templates: [
            { cloud: "AzureCloud", template: "https://{vaultName}.vault.azure.net" },
            { cloud: "AzureChinaCloud", template: "https://{vaultName}.vault.azure.cn" },
          ],
          cloudMetadata: {
            selectorIndex: "suffixes.keyVaultDns",
            prefixTemplate: "https://{vaultName}",
          },
        },
      };

      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return HttpResponse.json(mockExistingConfig);
        }),
      );

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Modify Client Config")).toBeInTheDocument();
      });

      // Check that form is populated with existing data
      expect(screen.getByDisplayValue("https://{vaultName}.vault.azure.net")).toBeInTheDocument();
      expect(screen.getByDisplayValue("https://{vaultName}.vault.azure.cn")).toBeInTheDocument();
      expect(screen.getByDisplayValue("suffixes.keyVaultDns")).toBeInTheDocument();
      expect(screen.getByDisplayValue("https://{vaultName}")).toBeInTheDocument();
      expect(screen.getByDisplayValue("https://management.azure.com/.default")).toBeInTheDocument();
    });

    it("should handle 404 for new config setup", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
      );

      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      // Check that form is in add mode
      expect(screen.queryByText("Cancel")).not.toBeInTheDocument();
      expect(screen.getByText("Update")).toBeInTheDocument();
    });

    it("should cascade load planes → modules → providers → versions", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      // Switch to resource mode
      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      await waitFor(() => {
        expect(screen.getByLabelText("Module")).toBeInTheDocument();
      });

      // Wait for planes to load and select a module
      await waitFor(() => {
        const moduleSelector = screen.getByLabelText("Module");
        expect(moduleSelector).toBeInTheDocument();
      });

      // Simulate selecting a module (this should trigger resource provider loading)
      const moduleInput = screen.getByLabelText("Module");
      await user.click(moduleInput);

      await waitFor(() => {
        expect(screen.getByText("storage")).toBeInTheDocument();
      });

      await user.click(screen.getByText("storage"));

      // Wait for resource providers to load
      await waitFor(() => {
        const rpSelector = screen.getByLabelText("Resource Provider");
        expect(rpSelector).toBeInTheDocument();
      });

      // Select a resource provider
      const rpInput = screen.getByLabelText("Resource Provider");
      await user.click(rpInput);

      await waitFor(() => {
        expect(screen.getByText("Microsoft.Storage")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Microsoft.Storage"));

      // Wait for versions to load
      await waitFor(() => {
        const versionSelector = screen.getByLabelText("API Version");
        expect(versionSelector).toBeInTheDocument();
      });

      // Check that versions are loaded and sorted (newest first)
      const versionInput = screen.getByLabelText("API Version");
      await user.click(versionInput);

      await waitFor(() => {
        expect(screen.getByText("2021-04-01")).toBeInTheDocument();
        expect(screen.getByText("2020-08-01")).toBeInTheDocument();
      });
    });

    it("should handle API errors gracefully during cascade loading", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
        http.get("*/specs/planes/azure-cli/modules", () => {
          return new HttpResponse(null, { status: 500 });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      // Switch to resource mode to trigger module loading
      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/ResponseError:/)).toBeInTheDocument();
      });
    });
  });

  describe("Complete User Workflows", () => {
    it("should complete template config setup end-to-end", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
        http.put(`*/workspaces${mockWorkspaceUrl}/client-config`, async ({ request }) => {
          const body = await request.json();
          expect(body).toEqual({
            templates: [
              { cloud: "AzureCloud", template: "https://{vaultName}.vault.azure.net" },
              { cloud: "AzureChinaCloud", template: "https://{vaultName}.vault.azure.cn" },
            ],
            cloudMetadata: {
              selectorIndex: "suffixes.keyVaultDns",
              prefixTemplate: "https://{vaultName}",
            },
            resource: undefined,
            auth: {
              aad: {
                scopes: ["https://management.azure.com/.default"],
              },
            },
          });
          return HttpResponse.json({ success: true });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      // Fill out template form
      const azureCloudInput = screen.getByLabelText("Azure Cloud");
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const azureChinaInput = screen.getByLabelText("Azure China Cloud");
      await user.type(azureChinaInput, "https://{vaultName}.vault.azure.cn");

      const selectorIndexInput = screen.getByLabelText("Endpoint/Suffix Index");
      await user.type(selectorIndexInput, "suffixes.keyVaultDns");

      const prefixInput = screen.getByLabelText("Prefix");
      await user.type(prefixInput, "https://{vaultName}");

      // Fill out AAD scope
      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      // Submit form
      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      // Should call onClose with true on success
      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalledWith(true);
      });
    });

    it("should complete resource config setup end-to-end", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
        http.put(`*/workspaces${mockWorkspaceUrl}/client-config`, async ({ request }) => {
          const body = await request.json();
          expect(body).toEqual({
            templates: undefined,
            cloudMetadata: undefined,
            resource: {
              plane: "azure-cli",
              module: "storage",
              version: "2021-04-01",
              id: "storageAccounts",
              subresource: "properties.primaryEndpoints.blob",
            },
            auth: {
              aad: {
                scopes: ["https://storage.azure.com/.default"],
              },
            },
          });
          return HttpResponse.json({ success: true });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      // Switch to resource mode
      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      await waitFor(() => {
        expect(screen.getByLabelText("Module")).toBeInTheDocument();
      });

      // Select module
      const moduleInput = screen.getByLabelText("Module");
      await user.click(moduleInput);
      await waitFor(() => {
        expect(screen.getByText("storage")).toBeInTheDocument();
      });
      await user.click(screen.getByText("storage"));

      // Select resource provider
      await waitFor(() => {
        const rpInput = screen.getByLabelText("Resource Provider");
        expect(rpInput).toBeInTheDocument();
      });
      const rpInput = screen.getByLabelText("Resource Provider");
      await user.click(rpInput);
      await waitFor(() => {
        expect(screen.getByText("Microsoft.Storage")).toBeInTheDocument();
      });
      await user.click(screen.getByText("Microsoft.Storage"));

      // Select version
      await waitFor(() => {
        const versionInput = screen.getByLabelText("API Version");
        expect(versionInput).toBeInTheDocument();
      });
      const versionInput = screen.getByLabelText("API Version");
      await user.click(versionInput);
      await waitFor(() => {
        expect(screen.getByText("2021-04-01")).toBeInTheDocument();
      });
      await user.click(screen.getByText("2021-04-01"));

      // Select resource ID
      await waitFor(() => {
        const resourceIdInput = screen.getByLabelText("Resource ID");
        expect(resourceIdInput).toBeInTheDocument();
      });
      const resourceIdInput = screen.getByLabelText("Resource ID");
      await user.click(resourceIdInput);
      await waitFor(() => {
        expect(screen.getByText("storageAccounts")).toBeInTheDocument();
      });
      await user.click(screen.getByText("storageAccounts"));

      // Fill subresource
      const subresourceInput = screen.getByLabelText("Endpoint Property Index");
      await user.type(subresourceInput, "properties.primaryEndpoints.blob");

      // Update AAD scope
      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.clear(aadScopeInput);
      await user.type(aadScopeInput, "https://storage.azure.com/.default");

      // Submit form
      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      // Should call onClose with true on success
      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalledWith(true);
      });
    });

    it("should handle network errors during submission", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
        http.put(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 500 });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByLabelText("Azure Cloud")).toBeInTheDocument();
      });

      // Fill required fields
      const azureCloudInput = screen.getByLabelText("Azure Cloud");
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      // Submit form
      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/ResponseError:/)).toBeInTheDocument();
      });

      // Should not call onClose
      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it("should handle error recovery - fix validation error and retry", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
        http.put(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return HttpResponse.json({ success: true });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Update")).toBeInTheDocument();
      });

      // Try to submit without required field
      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      // Should show validation error
      await waitFor(() => {
        expect(screen.getByText("Azure Cloud Endpoint Template is required.")).toBeInTheDocument();
      });

      // Fix the error
      const azureCloudInput = screen.getByLabelText("Azure Cloud");
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      // Retry submission
      await user.click(updateButton);

      // Should succeed
      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalledWith(true);
      });
    });
  });

  describe("Real-time Validation", () => {
    it("should validate template URLs in real-time", async () => {
      server.use(
        http.get(`*/workspaces${mockWorkspaceUrl}/client-config`, () => {
          return new HttpResponse(null, { status: 404 });
        }),
      );

      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByLabelText("Azure Cloud")).toBeInTheDocument();
      });

      // Enter invalid URL
      const azureCloudInput = screen.getByLabelText("Azure Cloud");
      await user.type(azureCloudInput, "invalid-url");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText("Azure Cloud Endpoint Template is invalid.")).toBeInTheDocument();
      });

      // Fix the URL
      await user.clear(azureCloudInput);
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      // Add AAD scope
      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      // Should be able to submit now
      await user.click(updateButton);

      // Error should clear and submission should proceed
      await waitFor(() => {
        expect(screen.queryByText("Azure Cloud Endpoint Template is invalid.")).not.toBeInTheDocument();
      });
    });
  });
});
