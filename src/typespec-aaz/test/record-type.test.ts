import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { generateCompileArmResourceTemplate } from "./util.js";

describe("record type parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  // Record<> dict models have no usable identifier name (getOpenAPITypeName
  // returns "Record<string>"). They must be inlined as additionalProps, never
  // promoted to a shared cls schema, otherwise the generated Python identifier
  // "_schema_record<string>_read" is invalid syntax. See Azure/CLIPS#526.
  it("record<string> is inlined, never a cls", async () => {
    const modelVar = {
      // two Record<string> props reference the same builtin model -> would
      // trigger cls promotion (count >= 2) without the fix.
      modelKey:
        "@visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)\n    @doc(\"tags a\")\n    tagsA?: Record<string>;\n" +
        "    @visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)\n    @doc(\"tags b\")\n    tagsB?",
      modelContent: "Record<string>",
    };
    const result = await compileTypespecAAZOperations(
      generateCompileArmResourceTemplate(modelVar),
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/mockresources/{}"],
      },
      runner,
    );
    expect(result).toBeTruthy();
    expect(result!).not.toContain("Record<string>");
    expect(result!).toContain("additionalProps");
  });
});
