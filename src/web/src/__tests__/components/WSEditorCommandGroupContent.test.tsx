import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import WSEditorCommandGroupContent from "../../views/workspace/components/WSEditorCommandGroupContent/WSEditorCommandGroupContent";
import { commandApi } from "../../services";

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

vi.mock("../../services", () => ({
  commandApi: {
    deleteCommandGroup: {
      loadingMessage: "Deleting command group...",
      fn: vi.fn(),
    },
    updateCommandGroup: vi.fn(),
    renameCommandGroup: vi.fn(),
  },
  errorHandlerApi: {
    getErrorMessage: vi.fn(),
  },
}));

const mockCommandApi = commandApi as any;

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
    mockCommandApi.deleteCommandGroup.fn.mockResolvedValue(undefined);
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

      expect(screen.getByText("az test-group")).toBeInTheDocument();

      expect(screen.getByText("[ GROUP ]")).toBeInTheDocument();

      expect(screen.getByText("Stable")).toBeInTheDocument();

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

      const groupCard = screen.getByText("az test-group").closest(".MuiCard-root");
      const editButton = within(groupCard as HTMLElement).getByRole("button", { name: /edit/i });
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument();
        expect(screen.getByRole("dialog")).toHaveAccessibleName("Command Group");
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

      const groupCard = screen.getByText("az test-group").closest(".MuiCard-root");
      const editButton = within(groupCard as HTMLElement).getByRole("button", { name: /edit/i });
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument();
        expect(screen.getByRole("dialog")).toHaveAccessibleName("Command Group");
      });

      const dialog = screen.getByRole("dialog");
      const cancelButton = within(dialog).getByRole("button", { name: /cancel/i });
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
      });
    });

    it.skip("saves changes and updates command group", async () => {
      // @NOTE: will change approach once mocking setup changes
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      await user.click(screen.getByRole("button", { name: /edit/i }));

      const shortSummary = await screen.findByDisplayValue("Test command group help text");
      await user.clear(shortSummary);
      await user.type(shortSummary, "Updated help text");

      const saveButton = screen.getByRole("button", { name: /save/i });
      await user.click(saveButton);

      await waitFor(() =>
        expect(mockCommandApi.updateCommandGroup).toHaveBeenCalledWith(
          expect.stringContaining(mockWorkspaceUrl),
          expect.objectContaining({
            help: expect.objectContaining({ short: "Updated help text" }),
          }),
        ),
      );

      expect(mockOnUpdateCommandGroup).toHaveBeenCalledWith(expect.objectContaining({ names: ["updated-group"] }));
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

      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        const dialog = screen.getByRole("dialog");
        expect(dialog).toBeInTheDocument();
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
        expect(within(dialog).getByText("az test-group")).toBeInTheDocument();
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

      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
      });

      const cancelButton = screen.getByRole("button", { name: /cancel/i });
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText("Delete Command Group")).not.toBeInTheDocument();
      });
    });

    it.skip("confirms delete and removes command group", async () => {
      // @NOTE: will adjust once mocking setup changes
      const user = userEvent.setup();

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
      });

      const confirmDeleteButton = screen.getAllByRole("button", { name: /delete/i })[1];
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(mockCommandApi.deleteCommandGroup.fn).toHaveBeenCalled();
        expect(mockOnUpdateCommandGroup).toHaveBeenCalledWith(null);
      });
    });
  });

  describe("Error Handling", () => {
    it.skip("handles update command group API error", async () => {
      // @NOTE: will adjust when mocking setup changes
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

    it.skip("handles delete command group API error", async () => {
      // @NOTE: will adjust when mocking setup changes
      const user = userEvent.setup();
      const mockError = new Error("Delete failed");

      mockCommandApi.deleteCommandGroup.fn.mockRejectedValue(mockError);

      render(
        <WSEditorCommandGroupContent
          workspaceUrl={mockWorkspaceUrl}
          commandGroup={mockCommandGroup}
          reloadTimestamp={Date.now()}
          onUpdateCommandGroup={mockOnUpdateCommandGroup}
        />,
      );

      const deleteButton = screen.getByRole("button", { name: /delete/i });
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText("Delete Command Group")).toBeInTheDocument();
      });

      const confirmDeleteButton = screen.getAllByRole("button", { name: /delete/i })[1];
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(mockCommandApi.deleteCommandGroup.fn).toHaveBeenCalled();
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
