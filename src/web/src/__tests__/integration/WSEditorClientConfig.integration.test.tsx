import { describe, it, expect, vi, beforeEach, beforeAll, afterEach, afterAll } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { setupServer } from "msw/node";
import { render } from "../test-utils";
import WSEditorClientConfigDialog from "../../views/workspace/components/WSEditor/WSEditorClientConfig";

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

  beforeEach(() => {
    vi.clearAllMocks();
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
          workspaceUrl={`${mockWorkspaceUrl}?simulate404=true`}
          open={true}
          onClose={mockOnClose}
        />,
      );

      await waitFor(() => {
        expect(screen.getByText("Setup Client Config")).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /update/i })).toBeInTheDocument();
      });

      expect(screen.queryByText("Cancel")).not.toBeInTheDocument();
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
    it("should handle user inputs for relevant fields", async () => {
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
  });
});
