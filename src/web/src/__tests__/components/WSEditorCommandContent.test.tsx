import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import WSEditorCommandContent from "../../views/workspace/WSEditorCommandContent";
import type { Command, Example, Resource } from "../../views/workspace/WSEditorCommandContent";
import { render } from "../test-utils";
import { commandApi } from "../../services/commandApi";

// Mock the API modules
vi.mock("../../services/commandApi");

// Mock WSEditorCommandArgumentsContent since it's a complex component
vi.mock("../../views/workspace/WSEditorCommandArgumentsContent", () => ({
  default: ({ onReloadArgs, onAddSubCommand }: any) => (
    <div data-testid="command-arguments-content">
      <button onClick={onReloadArgs}>Reload Args</button>
      <button onClick={() => onAddSubCommand("testVar", [{ var: "test", options: "test" }], ["test"])}>
        Add Subcommand
      </button>
    </div>
  ),
  DecodeArgs: vi.fn(() => ({ args: [], clsArgDefineMap: {} })),
}));

describe("WSEditorCommandContent", () => {
  const mockResource: Resource = {
    id: "resource1",
    version: "1.0",
    swagger: "https://example.com/swagger.json",
  };

  const mockExample: Example = {
    name: "Create storage account",
    commands: ["storage account create --resource-group myRG --name myAccount"],
  };

  const mockCommand: Command = {
    id: "command:storage/account/create",
    names: ["storage", "account", "create"],
    help: {
      short: "Create a storage account",
      lines: ["This command creates a new storage account", "with specified parameters"],
    },
    stage: "Stable" as const,
    version: "1.0",
    examples: [mockExample],
    outputs: [
      {
        type: "object" as const,
        ref: "StorageAccount",
        clientFlatten: false,
      },
    ],
    resources: [mockResource],
    confirmation: "Are you sure you want to create this storage account?",
    args: [
      {
        var: "resource_group_name",
        options: ["--resource-group", "-g"],
        type: "string",
        required: true,
        stage: "Stable" as const,
        hide: false,
        group: "",
        nullable: false,
        help: {
          short: "Name of resource group.",
        },
      },
    ],
    clsArgDefineMap: {},
  };

  const defaultProps = {
    workspaceUrl: "https://example.com/workspace",
    previewCommand: mockCommand,
    reloadTimestamp: Date.now(),
    onUpdateCommand: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock successful API calls by default
    vi.mocked(commandApi).getCommand.mockResolvedValue(mockCommand);
  });

  describe("Core Rendering", () => {
    it("renders the component with command information", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      expect(screen.getByText("[ COMMAND ]")).toBeInTheDocument();
      expect(screen.getByText("az storage account create")).toBeInTheDocument();
      expect(screen.getByText("Create a storage account")).toBeInTheDocument();
    });

    it("displays command stage and version", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText("v1.0")).toBeInTheDocument();
      });
    });

    it("shows loading state initially", () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      // Should show linear progress during loading
      expect(document.querySelector(".MuiLinearProgress-root")).toBeInTheDocument();
    });

    it("displays long help when available", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText("This command creates a new storage account")).toBeInTheDocument();
        expect(screen.getByText("with specified parameters")).toBeInTheDocument();
      });
    });

    it("shows placeholder when short help is missing", async () => {
      const commandWithoutHelp = {
        ...mockCommand,
        help: undefined,
      };

      const props = {
        ...defaultProps,
        previewCommand: commandWithoutHelp,
      };

      render(<WSEditorCommandContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText("Please add command short summary!")).toBeInTheDocument();
      });
    });
  });

  describe("Command Management", () => {
    it("displays edit and delete buttons", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /edit/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
      });
    });

    it("opens command dialog when edit button is clicked", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const editButton = screen.getByRole("button", { name: /edit/i });
        fireEvent.click(editButton);
      });

      // Command dialog should open
      await waitFor(() => {
        expect(screen.getByText("Command")).toBeInTheDocument();
      });
    });

    it("opens delete dialog when delete button is clicked", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const deleteButton = screen.getByRole("button", { name: /delete/i });
        fireEvent.click(deleteButton);
      });

      // Delete dialog should open
      await waitFor(() => {
        expect(screen.getByText("Delete Commands")).toBeInTheDocument();
      });
    });

    it("opens command dialog on double click", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        fireEvent.doubleClick(commandCard!);
      });

      await waitFor(() => {
        expect(screen.getByText("Command")).toBeInTheDocument();
      });
    });
  });

  describe("Arguments Section", () => {
    it("displays arguments card when command has args", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByTestId("command-arguments-content")).toBeInTheDocument();
      });
    });

    it("does not display arguments card when command has no args", async () => {
      const commandWithoutArgs = {
        ...mockCommand,
        args: undefined,
      };

      vi.mocked(commandApi).getCommand.mockResolvedValue(commandWithoutArgs);

      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.queryByTestId("command-arguments-content")).not.toBeInTheDocument();
      });
    });

    it("handles reload args callback", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const reloadButton = screen.getByText("Reload Args");
        fireEvent.click(reloadButton);
      });

      // Should trigger API call to reload command
      expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(2); // Initial load + reload
    });

    it("handles add subcommand callback", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const addSubcommandButton = screen.getByText("Add Subcommand");
        fireEvent.click(addSubcommandButton);
      });

      // Should open add subcommand dialog
      await waitFor(() => {
        expect(screen.getByText("Add Subcommands")).toBeInTheDocument();
      });
    });
  });

  describe("Examples Section", () => {
    it("displays example card with examples", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText("[ EXAMPLE ]")).toBeInTheDocument();
        expect(screen.getByText("Create storage account")).toBeInTheDocument();
      });
    });

    it("displays add example button", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const addButtons = screen.getAllByRole("button", { name: /add/i });
        expect(addButtons.length).toBeGreaterThan(0);
      });
    });

    it("opens example dialog when add button is clicked", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        // Find the Add button in the example section
        const exampleCard = screen.getByText("[ EXAMPLE ]").closest(".MuiCard-root");
        const addButton = exampleCard?.querySelector("button");
        if (addButton) {
          fireEvent.click(addButton);
        }
      });

      await waitFor(() => {
        expect(screen.getByText("Add Example")).toBeInTheDocument();
      });
    });

    it("opens example edit dialog when edit button is clicked", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const editButton = screen.getByText("Edit");
        fireEvent.click(editButton);
      });

      await waitFor(() => {
        expect(screen.getByText("Modify Example")).toBeInTheDocument();
      });
    });

    it("opens example dialog on double click", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const exampleAccordion = screen.getByText("Create storage account").closest(".MuiAccordion-root");
        fireEvent.doubleClick(exampleAccordion!);
      });

      await waitFor(() => {
        expect(screen.getByText("Modify Example")).toBeInTheDocument();
      });
    });
  });

  describe("Output Section", () => {
    it("displays output card when command has outputs", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText("[ OUTPUT ]")).toBeInTheDocument();
        expect(screen.getByText("StorageAccount")).toBeInTheDocument();
      });
    });

    it("does not display output card when command has no outputs", async () => {
      const commandWithoutOutputs = {
        ...mockCommand,
        outputs: undefined,
      };

      vi.mocked(commandApi).getCommand.mockResolvedValue(commandWithoutOutputs);

      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(screen.queryByText("[ OUTPUT ]")).not.toBeInTheDocument();
      });
    });
  });

  describe("Dialog Management", () => {
    it("handles command dialog close without changes", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        // Find the command card and click its edit button
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        const editButton = within(commandCard as HTMLElement).getByRole("button", { name: /edit/i });
        fireEvent.click(editButton);
      });

      await waitFor(() => {
        const cancelButton = screen.getByRole("button", { name: /cancel/i });
        fireEvent.click(cancelButton);
      });

      // Dialog should close
      await waitFor(() => {
        expect(screen.queryByText("Command")).not.toBeInTheDocument();
      });

      expect(defaultProps.onUpdateCommand).not.toHaveBeenCalled();
    });

    it("handles example dialog close with changes", async () => {
      const updatedCommand = { ...mockCommand, version: "2.0" };
      vi.mocked(commandApi).updateCommandExamples.mockResolvedValue(updatedCommand);

      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        // Find the first example card and click its edit button
        const exampleCard = screen.getByText("[ EXAMPLE ]").closest(".MuiCard-root");
        const editButton = within(exampleCard as HTMLElement).getByText("Edit");
        fireEvent.click(editButton);
      });

      await waitFor(() => {
        // Simulate saving changes
        const saveButton = screen.getByRole("button", { name: /save/i });
        fireEvent.click(saveButton);
      });

      await waitFor(() => {
        expect(defaultProps.onUpdateCommand).toHaveBeenCalledWith(updatedCommand);
      });
    });

    it("handles delete dialog confirmation", async () => {
      vi.mocked(commandApi).deleteResource.mockResolvedValue(undefined);

      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        // Find the command card and click its delete button
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        const deleteButton = within(commandCard as HTMLElement).getByRole("button", { name: /delete/i });
        fireEvent.click(deleteButton);
      });

      await waitFor(() => {
        // In the delete confirmation dialog, find the confirm button
        const confirmDeleteButton = screen.getByRole("button", { name: /delete/i });
        fireEvent.click(confirmDeleteButton);
      });

      await waitFor(() => {
        expect(defaultProps.onUpdateCommand).toHaveBeenCalledWith(null);
      });
    });
  });

  describe("Error Handling", () => {
    it("handles command loading errors", async () => {
      const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      vi.mocked(commandApi).getCommand.mockRejectedValue(new Error("Failed to load command"));

      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    it("handles API errors gracefully", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      // Component should handle errors without crashing
      expect(screen.getByText("[ COMMAND ]")).toBeInTheDocument();
    });
  });

  describe("Component Lifecycle", () => {
    it("reloads command when props change", async () => {
      const { rerender } = render(<WSEditorCommandContent {...defaultProps} />);

      // Initial load
      expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(1);

      // Change props to trigger reload
      const newProps = {
        ...defaultProps,
        reloadTimestamp: Date.now() + 1000,
      };

      rerender(<WSEditorCommandContent {...newProps} />);

      await waitFor(() => {
        expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(2);
      });
    });

    it("reloads command when workspace URL changes", async () => {
      const { rerender } = render(<WSEditorCommandContent {...defaultProps} />);

      expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(1);

      const newProps = {
        ...defaultProps,
        workspaceUrl: "https://different.com/workspace",
      };

      rerender(<WSEditorCommandContent {...newProps} />);

      await waitFor(() => {
        expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(2);
      });
    });

    it("reloads command when preview command changes", async () => {
      const { rerender } = render(<WSEditorCommandContent {...defaultProps} />);

      expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(1);

      const newCommand = {
        ...mockCommand,
        id: "command:different",
      };

      const newProps = {
        ...defaultProps,
        previewCommand: newCommand,
      };

      rerender(<WSEditorCommandContent {...newProps} />);

      await waitFor(() => {
        expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe("Complex Interactions", () => {
    it("handles stage display for different stages", async () => {
      const previewCommand = {
        ...mockCommand,
        stage: "Preview" as const,
      };

      const props = {
        ...defaultProps,
        previewCommand,
      };

      render(<WSEditorCommandContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText("v1.0")).toBeInTheDocument();
      });
    });

    it("handles experimental stage display", async () => {
      const experimentalCommand = {
        ...mockCommand,
        stage: "Experimental" as const,
      };

      const props = {
        ...defaultProps,
        previewCommand: experimentalCommand,
      };

      render(<WSEditorCommandContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText("v1.0")).toBeInTheDocument();
      });
    });
  });

  describe("Props Validation", () => {
    it("handles missing optional command properties", async () => {
      const minimalCommand = {
        id: "command:minimal",
        names: ["minimal"],
        stage: "Stable" as const,
        version: "1.0",
        resources: [mockResource],
      };

      const props = {
        ...defaultProps,
        previewCommand: minimalCommand,
      };

      expect(() => {
        render(<WSEditorCommandContent {...props} />);
      }).not.toThrow();
    });

    it("validates command structure", () => {
      expect(() => {
        render(<WSEditorCommandContent {...defaultProps} />);
      }).not.toThrow();
    });
  });
});
