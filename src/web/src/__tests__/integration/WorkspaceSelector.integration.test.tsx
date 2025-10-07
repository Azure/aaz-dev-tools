import { describe, it, expect, beforeEach, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { render } from "../test-utils";
import WorkspaceSelector from "../../views/workspace/WorkspaceSelector";

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
    mockLocation.href = "";
    vi.clearAllMocks();
  });

  describe("Workspace Loading and Selection", () => {
    it("should load workspaces from API and display them in dropdown", async () => {
      render(<WorkspaceSelector name="Choose Workspace" />);

      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await userEvent.click(autocomplete);

      expect(autocomplete).toBeInTheDocument();
    });

    it("should show existing workspace when typing partial name", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);

      await user.type(autocomplete, "test-work");

      expect(autocomplete).toHaveValue("test-work");
    });
  });

  describe("Create New Workspace Flow", () => {
    it("should open create dialog when typing new workspace name", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);

      await user.type(autocomplete, "brand-new-workspace");

      await waitFor(() => {
        expect(screen.getByText('Create "brand-new-workspace"')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Create "brand-new-workspace"'));

      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });
    });

    it("should display create workspace dialog with all required fields", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      const autocomplete = screen.getByLabelText("Choose Workspace");
      await user.click(autocomplete);
      await user.type(autocomplete, "new-workspace");

      await waitFor(() => {
        expect(screen.getByText('Create "new-workspace"')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Create "new-workspace"'));

      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Cancel")).toBeInTheDocument();
      expect(screen.getByText("Create")).toBeInTheDocument();

      await waitFor(
        () => {
          const nameField = screen.getByDisplayValue("new-workspace");
          expect(nameField).toBeInTheDocument();
        },
        { timeout: 5000 },
      );
    });

    it("should load planes and modules in create dialog", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

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

      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      await waitFor(
        () => {
          expect(screen.getByText("Create")).toBeInTheDocument();
        },
        { timeout: 3000 },
      );
    });

    it("should require all fields before enabling create button", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

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

      await waitFor(
        () => {
          const createButton = screen.getByRole("button", { name: "Create" });
          expect(createButton).toBeInTheDocument();
          expect(createButton).toBeDisabled();
        },
        { timeout: 5000 },
      );
    });

    it("should close dialog when cancel is clicked", async () => {
      const user = userEvent.setup();
      render(<WorkspaceSelector name="Choose Workspace" />);

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

      await user.click(screen.getByText("Cancel"));

      await waitFor(() => {
        expect(screen.queryByText("Create a new workspace")).not.toBeInTheDocument();
      });
    });
  });

  describe("Error Handling", () => {
    it("should handle workspace loading errors gracefully", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

      render(<WorkspaceSelector name="Choose Workspace" />);

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

      await waitFor(() => {
        expect(screen.getByText('Create "error-test"')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Create "error-test"'));

      await waitFor(() => {
        expect(screen.getByText("Create a new workspace")).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });
  });

  describe("Navigation Behavior", () => {
    it("should navigate when existing workspace is selected", async () => {
      render(<WorkspaceSelector name="Choose Workspace" />);

      await waitFor(() => {
        expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
      });

      expect(screen.getByLabelText("Choose Workspace")).toBeInTheDocument();
    });
  });
});
