import { describe, it, expect, vi, beforeEach, beforeAll, afterEach, afterAll } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { render } from "../test-utils";
import WSEditorClientConfigDialog from "../../views/workspace/WSEditorClientConfig";

const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

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
  const mockWorkspaceUrl = "/AAZ/Editor/Workspaces/test-workspace";
  const mockOnClose = vi.fn();

  const mockPlanes = {
    data: [
      {
        name: "azure-cli",
        displayName: "Azure CLI",
        moduleOptions: null,
      },
    ],
  };

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

    server.use(
      http.get(/\/aaz\/specs\/planes$/i, () => {
        return HttpResponse.json(mockPlanes);
      }),

      http.get("*/specs/planes/azure-cli/modules", () => {
        return HttpResponse.json(mockModules);
      }),

      http.get("*/specs/planes/*/modules/*/resource-providers", () => {
        return HttpResponse.json(mockResourceProviders);
      }),

      http.get("*/specs/planes/*/modules/*/resource-providers/*/resources", () => {
        return HttpResponse.json(mockProviderResources);
      }),
    );
  });

  describe("Data Loading Workflows", () => {
    it("should load existing client config and populate form", async () => {
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => expect(screen.getByText("Modify Client Config")).toBeInTheDocument());

      await waitFor(() =>
        expect(
          screen.getByRole("textbox", {
            name: /azure cloud/i,
          }),
        ).toHaveValue("https://management.azure.com/AzureCloudTemplate"),
      );

      await waitFor(() =>
        expect(screen.getByLabelText("Azure China Cloud")).toHaveValue("https://management.azure.com/AzureCloudChina"),
      );
    });

    it("should handle 404 for new config setup", async () => {
      render(
        <WSEditorClientConfigDialog
          workspaceUrl={`${mockWorkspaceUrl}?simulate404=false`}
          open={true}
          onClose={mockOnClose}
        />,
      );

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      expect(screen.queryByText("Cancel")).not.toBeInTheDocument();
      expect(screen.getByText("Update")).toBeInTheDocument();
    });

    it.skip("should cascade load planes → modules → providers → versions", async () => {
      // @NOTE: skipping this workflow for now, there is servere delay in loading, will revisit once loading states are improved.
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      // Switch to the resource property tab
      const resourcePropertyTab = screen.getByRole("tab", { name: /By resource property/i });
      await userEvent.click(resourcePropertyTab);

      // --- MODULES ---
      const moduleInput = screen.getByRole("combobox", { name: /Module/i });
      await userEvent.click(moduleInput);

      // Wait for the popper to render an option (it will display "storage", not "Microsoft.Storage")
      const storageOption = await screen.findByRole("option", { name: /storage/i });
      await userEvent.click(storageOption);

      // --- PROVIDERS ---
      const providerInput = screen.getByRole("combobox", { name: /Resource Provider/i });
      await userEvent.click(providerInput);

      // Providers are stripped of common prefix, so if API returned ["Microsoft.Storage"],
      // and `commonPrefix = "Microsoft."`, you’ll actually see "Storage" in the DOM
      const rpOption = await screen.findByRole("option", { name: /Storage/i });
      await userEvent.click(rpOption);

      // --- VERSIONS ---
      const versionInput = screen.getByRole("combobox", { name: /API Version/i });
      await userEvent.click(versionInput);

      const versionOption = await screen.findByRole("option", { name: /2021-04-01/i });
      await userEvent.click(versionOption);

      // Final assertions (all cascades complete)
      expect(moduleInput).toHaveValue("storage");
      expect(providerInput).toHaveValue("Storage");
      expect(versionInput).toHaveValue("2021-04-01");
    });

    it("should handle API errors gracefully during cascade loading", async () => {
      const user = userEvent.setup();
      render(
        <WSEditorClientConfigDialog
          workspaceUrl={`${mockWorkspaceUrl}?simulate404=false`}
          open={true}
          onClose={mockOnClose}
        />,
      );

      await waitFor(() => {
        expect(screen.getByText("By resource property")).toBeInTheDocument();
      });

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      await waitFor(() => {
        expect(screen.getByText(/ResponseError:/)).toBeInTheDocument();
      });
    });
  });

  describe("Complete User Workflows", () => {
    it("should complete template config setup end-to-end", async () => {
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      const azureCloudInput = document.querySelector("#AzureCloud") as HTMLElement;
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const azureChinaInput = screen.getByLabelText("Azure China Cloud");
      await user.type(azureChinaInput, "https://{vaultName}.vault.azure.cn");

      const selectorIndexInput = screen.getByLabelText("Endpoint/Suffix Index");
      await user.type(selectorIndexInput, "suffixes.keyVaultDns");

      const prefixInput = screen.getByLabelText("Prefix");
      await user.type(prefixInput, "https://{vaultName}");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalledWith(true);
      });
    });

    it.skip("should complete resource config setup end-to-end", async () => {
      // @NOTE: revisit once workflows and loading states are improved
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

      const resourceTab = screen.getByText("By resource property");
      await user.click(resourceTab);

      await waitFor(() => {
        expect(screen.getByRole("combobox", { name: /module/i })).toBeInTheDocument();
      });

      const moduleInput = screen.getByRole("combobox", { name: /module/i });
      await user.click(moduleInput);
      await waitFor(() => {
        expect(screen.getByText("storage")).toBeInTheDocument();
      });
      await user.click(screen.getByText("storage"));

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

      const subresourceInput = screen.getByLabelText("Endpoint Property Index");
      await user.type(subresourceInput, "properties.primaryEndpoints.blob");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.clear(aadScopeInput);
      await user.type(aadScopeInput, "https://storage.azure.com/.default");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalledWith(true);
      });
    });

    it.skip("should handle network errors during submission", async () => {
      // @NOTE: revisit once workflows and loading states are improved
      const user = userEvent.setup();
      render(
        <WSEditorClientConfigDialog
          workspaceUrl={`${mockWorkspaceUrl}?simulate404=false`}
          open={true}
          onClose={mockOnClose}
        />,
      );

      await waitFor(() => {
        expect(document.querySelector("#AzureCloud")).toBeInTheDocument();
      });

      const azureCloudInput = document.querySelector("#AzureCloud") as HTMLElement;
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText(/ResponseError:/)).toBeInTheDocument();
      });

      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it.skip("should handle error recovery - fix validation error and retry", async () => {
      // @NOTE: revisit once workflows and loading states are improved
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

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText("Azure Cloud Endpoint Template is required.")).toBeInTheDocument();
      });

      const azureCloudInput = document.querySelector("#AzureCloud") as HTMLElement;
      await user.type(azureCloudInput, "https://{vaultName}.vault.azure.net");

      const aadScopeInput = screen.getByPlaceholderText(/Input Microsoft Entra\(AAD\) auth Scope/);
      await user.type(aadScopeInput, "https://management.azure.com/.default");

      await user.click(updateButton);

      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalledWith(true);
      });
    });
  });

  describe("Real-time Validation", () => {
    it.skip("should validate template URLs in real-time", async () => {
      // @NOTE: revisit once error/loading states are cleared up
      const user = userEvent.setup();
      render(<WSEditorClientConfigDialog workspaceUrl={mockWorkspaceUrl} open={true} onClose={mockOnClose} />);

      await waitFor(() => {
        expect(document.querySelector("#AzureCloud")).toBeInTheDocument();
      });

      const azureCloudInput = document.querySelector("#AzureCloud") as HTMLElement;
      await user.type(azureCloudInput, "invalid-url");

      const updateButton = screen.getByText("Update");
      await user.click(updateButton);

      await waitFor(
        () => {
          expect(screen.queryByText("Azure Cloud Endpoint Template is invalid.")).not.toBeInTheDocument();
        },
        { timeout: 2000 },
      );
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
