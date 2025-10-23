import { spliceArgOptionsString } from "../../views/workspace/utils/spliceArgOptionsString";

const createMockArg = (overrides: any = {}): any => ({
  options: [],
  type: "string",
  var: "test",
  group: "",
  required: false,
  hide: false,
  stage: "Stable" as const,
  nullable: false,
  ...overrides,
});

describe("spliceArgOptionsString", () => {
  describe("Basic option formatting", () => {
    it("should format single character options with single dash at depth 0", () => {
      const arg = createMockArg({
        options: ["v", "h"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("-v -h");
    });

    it("should format multi-character options with double dash at depth 0", () => {
      const arg = createMockArg({
        options: ["verbose", "help"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--verbose --help");
    });

    it("should format mixed single and multi-character options at depth 0", () => {
      const arg = createMockArg({
        options: ["v", "verbose", "h", "help"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("-v --verbose -h --help");
    });

    it("should format options with dot prefix at depth > 0", () => {
      const arg = createMockArg({
        options: ["property", "prop"],
      });

      const result = spliceArgOptionsString(arg, 1);
      expect(result).toBe(".property .prop");
    });
  });

  describe("Array arguments with singular options", () => {
    it("should append singular options for array arguments at depth 0", () => {
      const arg = createMockArg({
        options: ["items"],
        type: "array<string>",
        item: { type: "string" },
        singularOptions: ["item", "i"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--items (--item -i)");
    });

    it("should append singular options for array arguments at depth > 0", () => {
      const arg = createMockArg({
        options: ["items"],
        type: "array<string>",
        item: { type: "string" },
        singularOptions: ["item"],
      });

      const result = spliceArgOptionsString(arg, 1);
      expect(result).toBe(".items (.item)");
    });

    it("should handle array arguments without singular options", () => {
      const arg = createMockArg({
        options: ["items"],
        type: "array<string>",
        item: { type: "string" },
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--items");
    });
  });

  describe("Class arguments with singular options", () => {
    it("should append singular options for class arguments at depth 0", () => {
      const arg = createMockArg({
        options: ["configs"],
        type: "@Config",
        clsName: "Config",
        singularOptions: ["config", "c"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--configs (--config -c)");
    });

    it("should append singular options for class arguments at depth > 0", () => {
      const arg = createMockArg({
        options: ["configs"],
        type: "@Config",
        clsName: "Config",
        singularOptions: ["config"],
      });

      const result = spliceArgOptionsString(arg, 2);
      expect(result).toBe(".configs (.config)");
    });

    it("should handle class arguments without singular options", () => {
      const arg = createMockArg({
        options: ["config"],
        type: "@Config",
        clsName: "Config",
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--config");
    });
  });

  describe("Edge cases", () => {
    it("should handle empty options array", () => {
      const arg = createMockArg({
        options: [],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("");
    });

    it("should handle single option", () => {
      const arg = createMockArg({
        options: ["single"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--single");
    });

    it("should handle different depths", () => {
      const arg = createMockArg({
        options: ["test"],
      });

      expect(spliceArgOptionsString(arg, 0)).toBe("--test");
      expect(spliceArgOptionsString(arg, 1)).toBe(".test");
      expect(spliceArgOptionsString(arg, 5)).toBe(".test");
    });

    it("should handle both array and class singular options pattern correctly", () => {
      const argWithBothPatterns = createMockArg({
        options: ["items"],
        type: "array<@Config>",
        item: { type: "@Config" },
        singularOptions: ["item"],
        clsName: "Config",
      });

      const result = spliceArgOptionsString(argWithBothPatterns, 0);
      expect(result).toBe("--items (--item)");
    });
  });

  describe("Complex scenarios", () => {
    it("should handle complex array argument with mixed option lengths", () => {
      const arg = createMockArg({
        options: ["resource-groups", "rg"],
        type: "array<string>",
        var: "resourceGroups",
        required: true,
        item: { type: "string" },
        singularOptions: ["resource-group", "g"],
      });

      const result = spliceArgOptionsString(arg, 0);
      expect(result).toBe("--resource-groups --rg (--resource-group -g)");
    });

    it("should handle nested class argument with singular options", () => {
      const arg = createMockArg({
        options: ["configurations"],
        type: "@Configuration",
        var: "configs",
        group: "advanced",
        clsName: "Configuration",
        singularOptions: ["configuration", "config", "c"],
      });

      const result = spliceArgOptionsString(arg, 1);
      expect(result).toBe(".configurations (.configuration .config .c)");
    });
  });
});
