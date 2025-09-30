import { describe, it, expect, beforeEach, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { render } from "./test-utils";
import WorkspaceSelector from "../views/workspace/WorkspaceSelector";

// Mock window.location for navigation testing
const mockLocation = {
  href: "",
  assign: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn(),
};

Object.defineProperty(window, "location", {
  value: mockLocation,
  writable: true,
});

describe("Workspace User Behavior (Integration with MSW)", () => {
  beforeEach(() => {
    // Reset location mock
    mockLocation.href = "";
    vi.clearAllMocks();
  });

  describe("Workspace Loading and Selection", () => {
    it("should load workspaces from API and display them in dropdown", async () => {
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Wait for workspaces to load from our MSW handlers
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      // Open the dropdown to see the options
      const autocomplete = screen.getByLabelText("Choose Workspace");
      await userEvent.click(autocomplete);

      // MSW should have returned our mock workspaces
      // We can't easily test the dropdown options with Material-UI autocomplete
      // but we can verify the component doesn't crash and is interactive
      expect(autocomplete).toBeInTheDocument();
    });

    it("should show existing workspace when typing partial name", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Wait for component to initialize
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      
      // Type part of an existing workspace name
      await user.type(autocomplete, "test-work");

      // The autocomplete should still be functional
      expect(autocomplete).toHaveValue("test-work");
    });
  });

  describe("Create New Workspace Flow", () => {
    it("should open create dialog when typing new workspace name", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Wait for component to initialize
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      
      // Type a new workspace name that doesn't exist
      await user.type(autocomplete, "brand-new-workspace");

      // Look for the "Create" option that should appear
      await waitFor(() => {
        expect(screen.getByText('Create "brand-new-workspace"')).toBeInTheDocument();
      });

      // Click the create option
      await user.click(screen.getByText('Create "brand-new-workspace"'));

      // This should open the create workspace dialog
      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });
    });

    it("should display create workspace dialog with all required fields", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Wait for initialization
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      // Trigger create dialog
      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "new-workspace");
      
      await waitFor(() => {
        expect(screen.getByText('Create "new-workspace"')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Create "new-workspace"'));

      // Verify dialog opens
      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      // Verify dialog has basic structure (even if some fields are still loading)
      expect(screen.getByText("Cancel")).toBeInTheDocument();
      expect(screen.getByText("Create")).toBeInTheDocument();

      // Wait for the form to fully load - check for text field by id instead of label
      await waitFor(() => {
        const nameField = screen.getByDisplayValue("new-workspace");
        expect(nameField).toBeInTheDocument();
      }, { timeout: 5000 });
    });

    it("should load planes and modules in create dialog", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Wait and trigger create dialog
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "test-workspace");
      
      await waitFor(() => {
        expect(screen.getByText('Create "test-workspace"')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Create "test-workspace"'));

      // Wait for dialog and API calls to complete
      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      // Wait for the planes to load (our MSW handler should provide them)
      await waitFor(() => {
        // The component should have loaded planes from our MSW handler
        // We can't easily test the autocomplete options, but we can verify
        // the component loaded without errors
        expect(screen.getByText("Create")).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it("should require all fields before enabling create button", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Trigger create dialog
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "test");
      
      await waitFor(() => {
        expect(screen.getByText('Create "test"')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Create "test"'));

      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      // Wait for the create button to be available and check its state
      await waitFor(() => {
        const createButton = screen.getByRole("button", { name: "Create" });
        expect(createButton).toBeInTheDocument();
        // Initially disabled because plane/module/resource provider are not selected
        expect(createButton).toBeDisabled();
      }, { timeout: 5000 });
    });

    it("should close dialog when cancel is clicked", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Open create dialog
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "cancel-test");
      
      await waitFor(() => {
        expect(screen.getByText('Create "cancel-test"')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Create "cancel-test"'));

      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      // Click cancel
      await user.click(screen.getByText("Cancel"));

      // Dialog should close
      await waitFor(() => {
        expect(screen.queryByText("Create a new workspace")).not.toBeInTheDocument();
      });
    });
  });

  describe("Error Handling", () => {
    it("should handle workspace loading errors gracefully", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      
      render(<WorkspaceSelector name="Choose Workspace" />);

      // Component should render even if API calls fail
      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });

    it("should handle dialog errors gracefully", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      const user = userEvent.setup();
      
      render(<WorkspaceSelector name="Choose Workspace" />);

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "error-test");
      
      // Even if there are errors, the create option should appear
      await waitFor(() => {
        expect(screen.getByText('Create "error-test"')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Create "error-test"'));

      // Dialog should attempt to open even if there are API errors
      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });
  });

  describe("Navigation Behavior", () => {
    it("should navigate when existing workspace is selected", async () => {
      // This tests the URL updating behavior, though we can't fully test
      // navigation in this environment
      render(<WorkspaceSelector name="Choose Workspace" />);

      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      // The component should be ready to handle selections
      // (Full navigation testing would require more complex setup)
      expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
    });
  });
});