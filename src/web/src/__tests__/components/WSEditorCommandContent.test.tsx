import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import WSEditorCommandContent from "../../views/workspace/WSEditorCommandContent";
import type { Command, Example, Resource } from "../../views/workspace/WSEditorCommandContent";
import { render } from "../test-utils";
import { commandApi } from "../../services/commandApi";

vi.mock("../../services/commandApi");

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

  const complexArg: Command = {
    id: "command:network/lb/address-pool/create",
    names: ["network", "lb", "address-pool", "create"],
    help: {
      short: "Create a load balancer backend address pool",
      lines: [
        "Create a new load balancer backend address pool with specified parameters.",
        "This command creates a backend address pool in the specified load balancer.",
      ],
    },
    stage: "Stable" as const,
    version: "2.0.0",
    examples: [
      {
        name: "Create a load balancer address pool",
        commands: [
          "network lb address-pool create --name myaddresspool --resource-group myresourcegroup --lb-name mylb",
        ],
      },
    ],
    resources: [
      {
        id: "Microsoft.Network/loadBalancers/backendAddressPools",
        version: "2021-09-01",
        swagger: "/swagger/network/2021-09-01/network.json",
      },
    ],
    outputs: [
      {
        type: "object" as const,
        ref: "BackendAddressPool",
        clientFlatten: false,
      },
    ],
    args: [
      {
        var: "backend_addresses",
        options: ["--backend-addresses"],
        help: {
          short: "An array of backend addresses.",
        },
        required: false,
        type: "array<object>",
        stage: "Stable" as const,
        hide: false,
        group: "Properties",
        nullable: false,
        singularOptions: ["--backend-address"],
      } as any, // Use 'as any' to bypass TypeScript for complex array argument
    ],
    clsArgDefineMap: {},
  };

  const complexCommandProps = {
    workspaceUrl: "https://example.com/workspace",
    previewCommand: complexArg,
    reloadTimestamp: Date.now(),
    onUpdateCommand: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(commandApi).getCommand.mockResolvedValue(mockCommand);
    vi.mocked(commandApi).getCommandsForResource.mockResolvedValue([mockCommand]);
    vi.mocked(commandApi).deleteResource.mockResolvedValue(undefined);
    vi.mocked(commandApi).updateCommand.mockResolvedValue(mockCommand);
    vi.mocked(commandApi).updateCommandExamples.mockResolvedValue(mockCommand);
    vi.mocked(commandApi).updateCommandOutputs.mockResolvedValue(mockCommand);
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
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        expect(within(commandCard as HTMLElement).getByText("Edit")).toBeInTheDocument();
        expect(within(commandCard as HTMLElement).getByText("Delete")).toBeInTheDocument();
      });
    });

    it("opens command dialog when edit button is clicked", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        const editButton = within(commandCard as HTMLElement).getByText("Edit");
        fireEvent.click(editButton);
      });

      await waitFor(() => {
        expect(screen.getByText("Command")).toBeInTheDocument();
      });
    });

    it("opens delete dialog when delete button is clicked", async () => {
      render(<WSEditorCommandContent {...defaultProps} />);

      await waitFor(() => {
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        const deleteButton = within(commandCard as HTMLElement).getByText("Delete");
        fireEvent.click(deleteButton);
      });

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
        expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
      });

      await waitFor(() => {
        const argsCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        expect(argsCard).toBeInTheDocument();
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

    it("handles add subcommand callback", async () => {
      const complexCommandResponse = {
        names: ["network", "lb", "address-pool", "create"],
        help: {
          short: "Create a load balancer backend address pool",
          lines: [
            "Create a new load balancer backend address pool with specified parameters.",
            "This command creates a backend address pool in the specified load balancer.",
          ],
        },
        stage: "Stable",
        version: "2.0.0",
        examples: [],
        outputs: [],
        resources: [],
        argGroups: [
          {
            name: "Properties",
            args: [
              {
                var: "backend_addresses",
                options: ["--backend-addresses"],
                help: {
                  short: "An array of backend addresses.",
                },
                required: false,
                type: "array<object>",
                stage: "Stable",
                hide: false,
                group: "Properties",
                nullable: false,
                item: {
                  type: "object",
                  args: [
                    {
                      var: "name",
                      options: ["--name"],
                      help: {
                        short: "Name of the backend address.",
                      },
                      required: false,
                      type: "string",
                      stage: "Stable",
                      hide: false,
                      group: "",
                      nullable: false,
                    },
                  ],
                },
              },
            ],
          },
        ],
        clsArgDefineMap: {},
      };

      vi.mocked(commandApi).getCommand.mockResolvedValue(complexCommandResponse);

      render(<WSEditorCommandContent {...complexCommandProps} />);

      await waitFor(() => {
        expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText("az network lb address-pool create")).toBeInTheDocument();
      });

      await waitFor(() => {
        const backendAddressesButton = screen.getByText(/backend-addresses/);
        fireEvent.click(backendAddressesButton);
      });

      await waitFor(() => {
        const addSubcommandButton = screen.getByText("Subcommands");
        fireEvent.click(addSubcommandButton);
      });

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument();
        expect(screen.getByRole("dialog")).toHaveTextContent("Add Subcommands");
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
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        const editButton = within(commandCard as HTMLElement).getByText("Edit");
        fireEvent.click(editButton);
      });

      await waitFor(() => {
        const cancelButton = screen.getByRole("button", { name: /cancel/i });
        fireEvent.click(cancelButton);
      });

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
        const exampleCard = screen.getByText("[ EXAMPLE ]").closest(".MuiCard-root");
        const editButton = within(exampleCard as HTMLElement).getByText("Edit");
        fireEvent.click(editButton);
      });

      await waitFor(() => {
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
        const commandCard = screen.getByText("[ COMMAND ]").closest(".MuiCard-root");
        const deleteButton = within(commandCard as HTMLElement).getByText("Delete");
        fireEvent.click(deleteButton);
      });

      await waitFor(() => {
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

      expect(screen.getByText("[ COMMAND ]")).toBeInTheDocument();
    });
  });

  describe("Component Lifecycle", () => {
    it("reloads command when props change", async () => {
      const { rerender } = render(<WSEditorCommandContent {...defaultProps} />);

      expect(vi.mocked(commandApi).getCommand).toHaveBeenCalledTimes(1);

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
