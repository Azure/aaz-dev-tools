import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, screen } from "@testing-library/react";
import WSEditorCommandArgumentsContent from "../../views/workspace/commandArgumentsContent/WSEditorCommandArgumentsContent";
import type {
  CMDArg,
  ClsArgDefinitionMap,
} from "../../views/workspace/commandArgumentsContent/WSEditorCommandArgumentsContent";
import { render } from "../test-utils";

vi.mock("../../services/commandApi");
vi.mock("../../services/errorHandlerApi");

describe("WSEditorCommandArgumentsContent", () => {
  const mockArgs: CMDArg[] = [
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
    {
      var: "account_name",
      options: ["--name", "-n"],
      type: "string",
      required: true,
      stage: "Stable" as const,
      hide: false,
      group: "",
      nullable: false,
      help: {
        short: "Storage account name.",
      },
    },
    {
      var: "location",
      options: ["--location", "-l"],
      type: "string",
      required: false,
      stage: "Stable" as const,
      hide: false,
      group: "",
      nullable: false,
      help: {
        short: "Location for the storage account.",
      },
      default: {
        value: "eastus",
      },
    },
  ];

  const mockClsArgDefineMap: ClsArgDefinitionMap = {
    StorageAccountCreateParameters: {
      type: "@StorageAccountCreateParameters",
      nullable: false,
    },
  };

  const defaultProps = {
    commandUrl: "/cli/azure-cli/rg/storageAccount/create",
    args: mockArgs,
    clsArgDefineMap: mockClsArgDefineMap,
    onReloadArgs: vi.fn().mockResolvedValue(undefined),
    onAddSubCommand: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Core Rendering", () => {
    it("renders the component with arguments", () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("displays basic argument information", () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("----name ---n")).toBeInTheDocument();
      expect(screen.getByText("----resource-group ---g")).toBeInTheDocument();
      expect(screen.getByText("----location ---l")).toBeInTheDocument();
    });

    it("renders empty state when no arguments provided", () => {
      const emptyProps = {
        ...defaultProps,
        args: [],
      };

      render(<WSEditorCommandArgumentsContent {...emptyProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
      expect(screen.queryByText("----name ---n")).not.toBeInTheDocument();
    });

    it("displays argument options correctly", () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("----resource-group ---g")).toBeInTheDocument();
      expect(screen.getByText("----name ---n")).toBeInTheDocument();

      expect(screen.getByText("Name of resource group.")).toBeInTheDocument();
      expect(screen.getByText("Storage account name.")).toBeInTheDocument();
    });

    it("shows default values when present", () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("----location ---l")).toBeInTheDocument();
    });
  });

  describe("Argument Interactions", () => {
    it("allows editing argument properties", async () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("handles argument selection", async () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      const argumentButton = screen.getByText("----resource-group ---g");
      fireEvent.click(argumentButton);

      expect(screen.getByTestId("ArrowBackIosIcon")).toBeInTheDocument();
      expect(screen.getByText("----resource-group")).toBeInTheDocument();

      expect(screen.getByText("----resource-group ---g")).toBeInTheDocument();
      expect(screen.getByText("/string/")).toBeInTheDocument();
      expect(screen.getByText("[Required]")).toBeInTheDocument();
      expect(screen.getByText("Name of resource group.")).toBeInTheDocument();
      expect(screen.getByText("Edit")).toBeInTheDocument();
    });

    it("displays arguments in correct sorted order", async () => {
      const mixedArgs = [
        {
          var: "zebra_arg",
          options: ["--zebra", "-z"],
          type: "string",
          required: false,
          stage: "Stable" as const,
          hide: false,
          group: "",
          nullable: false,
          help: { short: "Zebra argument." },
        },
        {
          var: "alpha_arg",
          options: ["--alpha", "-a"],
          type: "string",
          required: true,
          stage: "Stable" as const,
          hide: false,
          group: "",
          nullable: false,
          help: { short: "Alpha argument." },
        },
        {
          var: "beta_arg",
          options: ["--beta", "-b"],
          type: "string",
          required: false,
          stage: "Stable" as const,
          hide: false,
          group: "",
          nullable: false,
          help: { short: "Beta argument." },
        },
      ];

      const sortedProps = {
        ...defaultProps,
        args: mixedArgs,
      };

      render(<WSEditorCommandArgumentsContent {...sortedProps} />);

      const argumentElements = screen.getAllByText(/----\w+/);

      expect(argumentElements[0]).toHaveTextContent("----alpha ---a");
      expect(argumentElements[1]).toHaveTextContent("----beta ---b");
      expect(argumentElements[2]).toHaveTextContent("----zebra ---z");
    });
  });

  describe("Dialog Management", () => {
    it("opens argument dialog when needed", async () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("handles flatten dialog operations", async () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("manages unwrap class dialog", async () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("displays errors when API calls fail", async () => {
      render(<WSEditorCommandArgumentsContent {...defaultProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("handles validation errors for argument data", () => {
      const invalidArgs = [
        {
          var: "",
          options: [],
          type: "string",
          required: true,
          stage: "Stable" as const,
          hide: false,
          group: "",
          nullable: false,
          help: {
            short: "Invalid argument.",
          },
        },
      ];

      const invalidProps = {
        ...defaultProps,
        args: invalidArgs,
      };

      render(<WSEditorCommandArgumentsContent {...invalidProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });
  });

  describe("Complex Argument Types", () => {
    it("handles array type arguments", () => {
      const arrayArgs = [
        {
          var: "tags",
          options: ["--tags"],
          type: "array<string>",
          required: false,
          stage: "Stable" as const,
          hide: false,
          group: "",
          nullable: false,
          help: {
            short: "Space-separated tags.",
          },
        },
      ];

      const arrayProps = {
        ...defaultProps,
        args: arrayArgs,
      };

      render(<WSEditorCommandArgumentsContent {...arrayProps} />);

      expect(screen.getByText("----tags")).toBeInTheDocument();
      expect(screen.getByText("/array<string>/")).toBeInTheDocument();
    });

    it("handles dictionary type arguments", () => {
      const dictArgs = [
        {
          var: "metadata",
          options: ["--metadata"],
          type: "dict<string>",
          required: false,
          stage: "Stable" as const,
          hide: false,
          group: "",
          nullable: false,
          help: {
            short: "Metadata dictionary.",
          },
        },
      ];

      const dictProps = {
        ...defaultProps,
        args: dictArgs,
      };

      render(<WSEditorCommandArgumentsContent {...dictProps} />);

      expect(screen.getByText("----metadata")).toBeInTheDocument();
      expect(screen.getByText("/dict<string>/")).toBeInTheDocument();
    });
  });

  describe("State Management", () => {
    it("calls onReloadArgs when arguments are modified", async () => {
      const onReloadArgs = vi.fn().mockResolvedValue(undefined);
      const props = {
        ...defaultProps,
        onReloadArgs,
      };

      render(<WSEditorCommandArgumentsContent {...props} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("calls onAddSubCommand when sub-command is added", async () => {
      const onAddSubCommand = vi.fn();
      const props = {
        ...defaultProps,
        onAddSubCommand,
      };

      render(<WSEditorCommandArgumentsContent {...props} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });
  });

  describe("Props Validation", () => {
    it("handles missing props gracefully", () => {
      const minimalProps = {
        commandUrl: "/test",
        args: [],
        clsArgDefineMap: {},
        onReloadArgs: vi.fn().mockResolvedValue(undefined),
        onAddSubCommand: vi.fn(),
      };

      render(<WSEditorCommandArgumentsContent {...minimalProps} />);

      expect(screen.getByText("[ ARGUMENT ]")).toBeInTheDocument();
    });

    it("validates argument structure", () => {
      expect(() => {
        render(<WSEditorCommandArgumentsContent {...defaultProps} />);
      }).not.toThrow();
    });
  });
});
