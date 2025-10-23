import { describe, it, expect } from "vitest";
import { DecodeArgs } from "../../views/workspace/utils/decodeArgs";

describe("Argument Decoding Functions", () => {
  describe("DecodeArgs", () => {
    it("should decode empty argument groups", () => {
      const result = DecodeArgs([]);

      expect(result.args).toEqual([]);
      expect(result.clsArgDefineMap).toEqual({});
    });

    it("should decode basic string arguments", () => {
      const argGroups = [
        {
          args: [
            {
              var: "resource_group",
              options: ["--resource-group", "-g"],
              type: "string",
              required: true,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              help: {
                short: "Resource group name",
                lines: ["The name of the resource group"],
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "resource_group",
        options: ["--resource-group", "-g"],
        type: "string",
        required: true,
        stage: "Stable",
        hide: false,
        group: "",
        nullable: false,
      });
      expect(result.args[0].help?.short).toBe("Resource group name");
      expect(result.args[0].help?.lines).toEqual(["The name of the resource group"]);
    });

    it("should decode integer arguments with defaults", () => {
      const argGroups = [
        {
          args: [
            {
              var: "count",
              options: ["--count", "-c"],
              type: "integer",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              default: {
                value: 1,
              },
              help: {
                short: "Number of instances",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "count",
        type: "integer",
        required: false,
        default: {
          value: 1,
        },
      });
    });

    it("should decode boolean arguments", () => {
      const argGroups = [
        {
          args: [
            {
              var: "force",
              options: ["--force"],
              type: "boolean",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              help: {
                short: "Force the operation",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "force",
        type: "boolean",
        required: false,
      });
    });

    it("should decode array arguments", () => {
      const argGroups = [
        {
          args: [
            {
              var: "tags",
              options: ["--tags"],
              type: "array<string>",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              item: {
                type: "string",
                nullable: false,
              },
              singularOptions: ["--tag"],
              help: {
                short: "Tags for the resource",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "tags",
        type: "array<string>",
        required: false,
        singularOptions: ["--tag"],
      });
    });

    it("should decode object arguments with nested properties", () => {
      const argGroups = [
        {
          args: [
            {
              var: "properties",
              options: ["--properties"],
              type: "object",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              args: [
                {
                  var: "name",
                  options: ["--name"],
                  type: "string",
                  required: true,
                  stage: "Stable",
                  hide: false,
                  group: "",
                  nullable: false,
                  help: {
                    short: "Property name",
                  },
                },
                {
                  var: "value",
                  options: ["--value"],
                  type: "string",
                  required: true,
                  stage: "Stable",
                  hide: false,
                  group: "",
                  nullable: false,
                  help: {
                    short: "Property value",
                  },
                },
              ],
              help: {
                short: "Object properties",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "properties",
        type: "object",
        required: false,
      });
      // For object args with nested properties, they are stored directly on the arg
      const objArg = result.args[0] as any;
      expect(objArg.args).toHaveLength(2);
      expect(objArg.args[0].var).toBe("name");
      expect(objArg.args[1].var).toBe("value");
    });

    it("should decode dictionary arguments", () => {
      const argGroups = [
        {
          args: [
            {
              var: "metadata",
              options: ["--metadata"],
              type: "object",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              additionalProps: {
                item: {
                  type: "string",
                  nullable: false,
                },
              },
              help: {
                short: "Metadata dictionary",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "metadata",
        type: "dict<string, string>",
        required: false,
      });
    });

    it("should decode enum arguments", () => {
      const argGroups = [
        {
          args: [
            {
              var: "sku",
              options: ["--sku"],
              type: "string",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              enum: {
                items: [
                  { name: "Standard", value: "Standard", hide: false },
                  { name: "Premium", value: "Premium", hide: false },
                  { name: "Basic", value: "Basic", hide: true },
                ],
              },
              help: {
                short: "SKU type",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "sku",
        type: "string",
        required: false,
        hasEnum: true,
      });
      // The enum information is encoded into the argument during decoding
      // We can test that hasEnum is true, which indicates enum processing occurred
      expect(result.args[0].hasEnum).toBe(true);
    });

    it("should decode class reference arguments", () => {
      const argGroups = [
        {
          args: [
            {
              var: "config",
              options: ["--config"],
              type: "@ConfigurationClass",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              clsName: "ConfigurationClass",
              help: {
                short: "Configuration object",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "config",
        type: "@ConfigurationClass",
        required: false,
        clsName: "ConfigurationClass",
      });
    });

    it("should decode password arguments with prompt", () => {
      const argGroups = [
        {
          args: [
            {
              var: "password",
              options: ["--password", "-p"],
              type: "password",
              required: true,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              prompt: {
                msg: "Enter password:",
                confirm: true,
              },
              help: {
                short: "User password",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "password",
        type: "password",
        required: true,
      });
      expect(result.args[0].prompt).toMatchObject({
        msg: "Enter password:",
        confirm: true,
      });
    });

    it("should handle multiple argument groups", () => {
      const argGroups = [
        {
          args: [
            {
              var: "name",
              options: ["--name", "-n"],
              type: "string",
              required: true,
              stage: "Stable",
              hide: false,
              group: "Basic",
              nullable: false,
              help: {
                short: "Resource name",
              },
            },
          ],
        },
        {
          args: [
            {
              var: "location",
              options: ["--location", "-l"],
              type: "string",
              required: false,
              stage: "Stable",
              hide: false,
              group: "Advanced",
              nullable: false,
              help: {
                short: "Resource location",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(2);
      expect(result.args[0].var).toBe("name");
      expect(result.args[0].group).toBe("Basic");
      expect(result.args[1].var).toBe("location");
      expect(result.args[1].group).toBe("Advanced");
    });

    it("should handle complex nested class definitions", () => {
      const argGroups = [
        {
          args: [
            {
              var: "properties",
              options: ["--properties"],
              type: "object",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              cls: "PropertiesClass",
              args: [
                {
                  var: "nested_config",
                  options: ["--nested-config"],
                  type: "object",
                  required: false,
                  stage: "Stable",
                  hide: false,
                  group: "",
                  nullable: false,
                  cls: "NestedConfigClass",
                  args: [
                    {
                      var: "deep_property",
                      options: ["--deep-property"],
                      type: "string",
                      required: false,
                      stage: "Stable",
                      hide: false,
                      group: "",
                      nullable: false,
                      help: {
                        short: "Deep nested property",
                      },
                    },
                  ],
                  help: {
                    short: "Nested configuration",
                  },
                },
              ],
              help: {
                short: "Properties object",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "properties",
        type: "@PropertiesClass",
        clsName: "PropertiesClass",
      });
      expect(result.clsArgDefineMap).toHaveProperty("PropertiesClass");
      expect(result.clsArgDefineMap).toHaveProperty("NestedConfigClass");
    });

    it("should sort options by length in descending order", () => {
      const argGroups = [
        {
          args: [
            {
              var: "name",
              options: ["-n", "--name", "--full-name"],
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
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args[0].options).toEqual(["--full-name", "--name", "-n"]);
    });

    it("should handle missing optional properties gracefully", () => {
      const argGroups = [
        {
          args: [
            {
              var: "minimal",
              options: ["--minimal"],
              type: "string",
              // Missing optional properties like required, stage, hide, etc.
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "minimal",
        options: ["--minimal"],
        type: "string",
        required: false, // Default value
        stage: "Stable", // Default value
        hide: false, // Default value
        group: "", // Default value
        nullable: false, // Default value
      });
    });

    it("should handle blank values for different types", () => {
      const argGroups = [
        {
          args: [
            {
              var: "optional_string",
              options: ["--optional-string"],
              type: "string",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              blank: {
                value: "",
              },
              help: {
                short: "Optional string with blank",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "optional_string",
        type: "string",
        blank: {
          value: "",
        },
      });
    });

    it("should handle array of different primitive types", () => {
      const testCases = [
        { type: "array<integer>", itemType: "integer" },
        { type: "array<float>", itemType: "float" },
        { type: "array<boolean>", itemType: "boolean" },
      ];

      testCases.forEach(({ type, itemType }) => {
        const argGroups = [
          {
            args: [
              {
                var: "test_array",
                options: ["--test-array"],
                type,
                required: false,
                stage: "Stable",
                hide: false,
                group: "",
                nullable: false,
                item: {
                  type: itemType,
                  nullable: false,
                },
                help: {
                  short: `Array of ${itemType}`,
                },
              },
            ],
          },
        ];

        const result = DecodeArgs(argGroups);

        expect(result.args).toHaveLength(1);
        expect(result.args[0]).toMatchObject({
          var: "test_array",
          type,
          required: false,
        });
      });
    });

    it("should handle configuration keys and ID parts", () => {
      const argGroups = [
        {
          args: [
            {
              var: "subscription_id",
              options: ["--subscription"],
              type: "SubscriptionId",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              idPart: "subscription",
              configurationKey: "core.subscription_id",
              help: {
                short: "Subscription ID",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "subscription_id",
        type: "SubscriptionId",
        idPart: "subscription",
        configurationKey: "core.subscription_id",
      });
    });

    it("should handle enum extension support", () => {
      const argGroups = [
        {
          args: [
            {
              var: "extensible_enum",
              options: ["--extensible-enum"],
              type: "string",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              enum: {
                items: [
                  { name: "Option1", value: "option1", hide: false },
                  { name: "Option2", value: "option2", hide: false },
                ],
                supportExtension: true,
              },
              help: {
                short: "Extensible enum",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "extensible_enum",
        type: "string",
        supportEnumExtension: true,
        hasEnum: true,
      });
    });
  });

  describe("Edge Cases and Error Handling", () => {
    it("should handle null and undefined responses gracefully", () => {
      expect(() => DecodeArgs([])).not.toThrow();
      expect(() => DecodeArgs([{ args: [] }])).not.toThrow();
    });

    it("should handle arguments with missing help", () => {
      const argGroups = [
        {
          args: [
            {
              var: "no_help",
              options: ["--no-help"],
              type: "string",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              // No help property
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0].help).toBeUndefined();
    });

    it("should handle arguments with missing defaults", () => {
      const argGroups = [
        {
          args: [
            {
              var: "no_default",
              options: ["--no-default"],
              type: "string",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              // No default property
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0].default).toBeUndefined();
    });

    it("should handle array arguments without item definition", () => {
      const argGroups = [
        {
          args: [
            {
              var: "invalid_array",
              options: ["--invalid-array"],
              type: "array<string>",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              // Missing item property - this should cause an error
            },
          ],
        },
      ];

      expect(() => DecodeArgs(argGroups)).toThrow("Invalid array object. Item is not defined");
    });

    it("should handle unknown argument types", () => {
      const argGroups = [
        {
          args: [
            {
              var: "unknown_type",
              options: ["--unknown-type"],
              type: "unknown_custom_type",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
            },
          ],
        },
      ];

      expect(() => DecodeArgs(argGroups)).toThrow("Unknown type 'unknown_custom_type'");
    });

    it("should handle dict with any type", () => {
      const argGroups = [
        {
          args: [
            {
              var: "any_dict",
              options: ["--any-dict"],
              type: "object",
              required: false,
              stage: "Stable",
              hide: false,
              group: "",
              nullable: false,
              additionalProps: {
                anyType: true,
              },
              help: {
                short: "Dictionary with any value type",
              },
            },
          ],
        },
      ];

      const result = DecodeArgs(argGroups);

      expect(result.args).toHaveLength(1);
      expect(result.args[0]).toMatchObject({
        var: "any_dict",
        type: "dict<string, Any>",
        anyType: true,
      });
    });
  });
});
