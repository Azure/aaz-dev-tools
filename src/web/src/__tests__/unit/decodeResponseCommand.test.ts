import { describe, it, expect } from "vitest";
import { DecodeResponseCommand } from "../../views/workspace/utils/decodeResponseCommand";
import type { ResponseCommand } from "../../views/workspace/interfaces";

describe("DecodeResponseCommand", () => {
  it("should decode basic response command", () => {
    const responseCommand: ResponseCommand = {
      names: ["group", "command"],
      help: {
        short: "Test command",
        lines: ["This is a test command", "With multiple lines"],
      },
      stage: "Stable",
      version: "1.0.0",
      resources: [
        {
          id: "test-resource",
          version: "1.0.0",
          swagger: "https://example.com/swagger",
        },
      ],
    };

    const result = DecodeResponseCommand(responseCommand);

    expect(result).toEqual({
      id: "command:group/command",
      names: ["group", "command"],
      help: {
        short: "Test command",
        lines: ["This is a test command", "With multiple lines"],
      },
      stage: "Stable",
      version: "1.0.0",
      resources: [
        {
          id: "test-resource",
          version: "1.0.0",
          swagger: "https://example.com/swagger",
        },
      ],
    });
  });

  it("should handle default stage when not provided", () => {
    const responseCommand: ResponseCommand = {
      names: ["test"],
      version: "1.0.0",
      resources: [],
    };

    const result = DecodeResponseCommand(responseCommand);

    expect(result.stage).toBe("Stable");
    expect(result.id).toBe("command:test");
  });

  it("should handle confirmation message", () => {
    const responseCommand: ResponseCommand = {
      names: ["test"],
      version: "1.0.0",
      resources: [],
      confirmation: "Are you sure?",
    };

    const result = DecodeResponseCommand(responseCommand);

    expect(result.confirmation).toBe("Are you sure?");
  });

  it("should decode arguments when argGroups are provided", () => {
    const responseCommand: ResponseCommand = {
      names: ["test"],
      version: "1.0.0",
      resources: [],
      argGroups: [
        {
          args: [
            {
              var: "name",
              options: ["--name", "-n"],
              type: "string",
              required: true,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              help: {
                short: "Resource name",
              },
            },
          ],
        },
      ],
    };

    const result = DecodeResponseCommand(responseCommand);

    expect(result.args).toBeDefined();
    expect(result.args).toHaveLength(1);
    expect(result.args![0].var).toBe("name");
    expect(result.clsArgDefineMap).toBeDefined();
  });

  it("should handle optional properties correctly", () => {
    const responseCommand: ResponseCommand = {
      names: ["test"],
      version: "1.0.0",
      resources: [],
      examples: [
        {
          name: "Example 1",
          commands: ["az test --name myname"],
        },
      ],
      outputs: [
        {
          type: "string",
          ref: "#/definitions/TestOutput",
          value: "result",
        },
      ],
    };

    const result = DecodeResponseCommand(responseCommand);

    expect(result.examples).toEqual([
      {
        name: "Example 1",
        commands: ["az test --name myname"],
      },
    ]);
    expect(result.outputs).toEqual([
      {
        type: "string",
        ref: "#/definitions/TestOutput",
        value: "result",
      },
    ]);
  });

  it("should generate correct command ID from names", () => {
    const testCases = [
      { names: ["single"], expected: "command:single" },
      { names: ["group", "command"], expected: "command:group/command" },
      { names: ["a", "b", "c", "d"], expected: "command:a/b/c/d" },
    ];

    testCases.forEach(({ names, expected }) => {
      const responseCommand: ResponseCommand = {
        names,
        version: "1.0.0",
        resources: [],
      };

      const result = DecodeResponseCommand(responseCommand);
      expect(result.id).toBe(expected);
    });
  });
});
