import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import WSEditorCommandGroupContent from "../../views/workspace/WSEditorCommandGroupContent";
import * as commandApi from "../../services/commandApi";
import * as errorHandlerApi from "../../services/errorHandlerApi";

// Define the CommandGroup interface as it's defined locally in the component
interface CommandGroup {
  id: string;
  names: string[];
  stage: "Stable" | "Preview" | "Experimental";
  help?: {
    short: string;
    lines?: string[];
  };
  canDelete: boolean;
}

// Mock the required modules
vi.mock("../../services/commandApi");
vi.mock("../../services/errorHandlerApi");

const mockCommandApi = commandApi as any;
const mockErrorHandlerApi = errorHandlerApi as any;

describe("WSEditorCommandGroupContent", () => {
  const mockWorkspaceUrl = "https://test-workspace.com/workspace/ws1";

  const mockCommandGroup: CommandGroup = {
    id: "test-group-id",
    names: ["test-group"],
    stage: "Stable",
    help: {
      short: "Test command group help text",
      lines: ["Extended help for test command group"],
    },
    canDelete: true,
  };

  const mockOnUpdateCommandGroup = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    mockCommandApi.updateCommandGroup = vi.fn().mockResolvedValue({
      data: { ...mockCommandGroup, names: ["Updated Group"] },
    });

    mockCommandApi.deleteCommandGroup = vi.fn().mockResolvedValue({});

    mockCommandApi.renameCommandGroup = vi.fn().mockResolvedValue({
      data: { ...mockCommandGroup, names: ["Renamed Group"] },
    });

    mockErrorHandlerApi.onErrorAlert = vi.fn();
  });

  describe("Core Rendering", () => {
    it("renders command group card with basic information", () => {
      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Check for command group name display (with az prefix)
      expect(screen.getByText("az test-group")).toBeInTheDocument();

      // Check for GROUP label
      expect(screen.getByText("[ GROUP ]")).toBeInTheDocument();

      // Check for stage display
      expect(screen.getByText("Stable")).toBeInTheDocument();

      // Check for help text
      expect(screen.getByText("Test command group help text")).toBeInTheDocument();
    });

    it("renders Edit and Delete buttons", () => {
      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
    });

    it("handles command group without help text", () => {
      const noHelpCommandGroup = { ...mockCommandGroup, help: undefined };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={noHelpCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az test-group")).toBeInTheDocument();
      expect(screen.getByText("Please add command group short summary!")).toBeInTheDocument();
    });

    it("disables delete button when canDelete is false", () => {
      const nonDeletableCommandGroup = { ...mockCommandGroup, canDelete: false };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={nonDeletableCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      const deleteButton = screen.getByRole("button", { name: /delete/i });
      expect(deleteButton).toBeDisabled();
    });
  });

  describe("Edit Dialog Management", () => {
    it("opens edit dialog when Edit button is clicked", async () => {
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Find and click the Edit button
      const editButton = screen.getByRole("button", { name: /edit/i });
      await user.click(editButton);

      // Check if the edit dialog is displayed
      await waitFor(() => {
        expect(screen.getByText("Edit Command Group")).toBeInTheDocument();
        expect(screen.getByDisplayValue("test-group")).toBeInTheDocument();
      });
    });

    it("closes edit dialog when Cancel is clicked", async () => {
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Open dialog
      const editButton = screen.getByRole("button", { name: /edit/i });
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByText("Edit Command Group")).toBeInTheDocument();
      });

      // Close dialog
      const cancelButton = screen.getByRole("button", { name: /cancel/i });
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText("Edit Command Group")).not.toBeInTheDocument();
      });
    });

    it("saves changes and updates command group", async () => {
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Open dialog
      const editButton = screen.getByRole("button", { name: /edit/i });
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByText("Edit Command Group")).toBeInTheDocument();
      });

      // Modify name
      const nameInput = screen.getByDisplayValue("test-group");
      await user.clear(nameInput);
      await user.type(nameInput, "updated-group");

      // Save changes
      const saveButton = screen.getByRole("button", { name: /save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(mockOnUpdateCommandGroup).toHaveBeenCalled();
      });
    });
  });

  describe("Delete Dialog Management", () => {
    it("opens delete dialog when Delete button is clicked", async () => {
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Find and click the Delete button
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      // Check if the delete dialog is displayed
      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
        expect(screen.getByText("az test-group")).toBeInTheDocument();
      });
    });

    it("closes delete dialog when Cancel is clicked", async () => {
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Open dialog
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
      });

      // Close dialog
      const cancelButton = screen.getByRole("button", { name: /cancel/i });
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText("Delete Command Group")).not.toBeInTheDocument();
      });
    });

    it("confirms delete and removes command group", async () => {
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Open dialog
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
      });

      // Confirm delete - get the second Delete button (the one in the dialog)
      const confirmDeleteButton = screen.getAllByRole("button", { name: /delete/i })[1];
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(mockCommandApi.deleteCommandGroup).toHaveBeenCalled();
        expect(mockOnUpdateCommandGroup).toHaveBeenCalledWith(null);
      });
    });
  });

  describe("Error Handling", () => {
    it("handles update command group API error", async () => {
      const user = userEvent.setup();
      const mockError = new Error("Update failed");

      mockCommandApi.updateCommandGroup.mockRejectedValue(mockError);

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Open dialog and try to save
      const editButton = screen.getByRole("button", { name: /edit/i });
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByText("Edit Command Group")).toBeInTheDocument();
      });

      const saveButton = screen.getByRole("button", { name: /save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(mockCommandApi.updateCommandGroup).toHaveBeenCalled();
      });
    });

    it("handles delete command group API error", async () => {
      const user = userEvent.setup();
      const mockError = new Error("Delete failed");

      mockCommandApi.deleteCommandGroup.mockRejectedValue(mockError);

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Open dialog and try to delete
      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
      });

      const confirmDeleteButton = screen.getAllByRole("button", { name: /delete/i })[1];
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(mockCommandApi.deleteCommandGroup).toHaveBeenCalled();
      });
    });

    it("handles missing workspace URL gracefully", () => {
      render(
        <WSEditorCommandGroupContent
          workspaceUrl=""
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      // Component should still render the command group info
      expect(screen.getByText("az test-group")).toBeInTheDocument();
    });

    it("handles command group with minimal data", () => {
      const minimalCommandGroup: CommandGroup = {
        id: "minimal-group",
        names: ["minimal"],
        stage: "Stable",
        canDelete: true,
      };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={minimalCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az minimal")).toBeInTheDocument();
      expect(screen.getByText("Please add command group short summary!")).toBeInTheDocument();
    });
  });

  describe("Component Lifecycle", () => {
    it("updates when reloadTimestamp changes", () => {
      const { rerender } = render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={1000}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az test-group")).toBeInTheDocument();

      // Update with new timestamp
      rerender(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={2000}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az test-group")).toBeInTheDocument();
    });

    it("updates when command group prop changes", () => {
      const { rerender } = render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az test-group")).toBeInTheDocument();

      const updatedCommandGroup = { ...mockCommandGroup, names: ["updated-group"] };

      rerender(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={updatedCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az updated-group")).toBeInTheDocument();
    });
  });

  describe("Stage Management", () => {
    it("displays correct stage for Stable command group", () => {
      const stableCommandGroup: CommandGroup = { ...mockCommandGroup, stage: "Stable" as const };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={stableCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("Stable")).toBeInTheDocument();
    });

    it("displays correct stage for Preview command group", () => {
      const previewCommandGroup: CommandGroup = { ...mockCommandGroup, stage: "Preview" as const };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={previewCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("Preview")).toBeInTheDocument();
    });

    it("displays correct stage for Experimental command group", () => {
      const experimentalCommandGroup: CommandGroup = { ...mockCommandGroup, stage: "Experimental" as const };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={experimentalCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("Experimental")).toBeInTheDocument();
    });
  });

  describe("Help Text Display", () => {
    it("displays help text when provided", () => {
      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("Test command group help text")).toBeInTheDocument();
    });

    it("displays extended help lines when provided", () => {
      const commandGroupWithExtendedHelp = {
        ...mockCommandGroup,
        help: {
          short: "Short help text",
          lines: ["Extended help line 1", "Extended help line 2"],
        },
      };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={commandGroupWithExtendedHelp}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("Short help text")).toBeInTheDocument();
      expect(screen.getByText("Extended help line 1")).toBeInTheDocument();
      expect(screen.getByText("Extended help line 2")).toBeInTheDocument();
    });

    it("handles empty help text gracefully", () => {
      const noHelpTextCommandGroup = {
        ...mockCommandGroup,
        help: { short: "", lines: [] },
      };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={noHelpTextCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az test-group")).toBeInTheDocument();
      expect(screen.getByText("Please add command group short summary!")).toBeInTheDocument();
    });

    it("handles undefined help text gracefully", () => {
      const undefinedHelpTextCommandGroup = { ...mockCommandGroup, help: undefined };

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={undefinedHelpTextCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      expect(screen.getByText("az test-group")).toBeInTheDocument();
      expect(screen.getByText("Please add command group short summary!")).toBeInTheDocument();
    });
  });
});
