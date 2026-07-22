import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { generateCompileArmResourceTemplate } from "./util.js";

describe("cls schema naming", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  // A cls-promoted schema must be named "<PascalCaseModelName>_<verb>" to match the Swagger
  // converter (utils/case.py + swagger cmd_builder). Two regressions used to break parity:
  //   1. toCamelCase lowercased the tail -> "Identityconfigurationproperties" (see #564 feedback).
  //   2. an extra getVisibilitySuffix infix -> "...CreateOrUpdate_create", absent in Swagger.
  it("preserves PascalCase and omits the verb-visibility infix", async () => {
    const modelVar = {
      // reference IdentityConfigurationProperties a second/third time so count >= 2 -> cls promotion.
      modelKey:
        "@visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)\n    @doc(\"extra a\")\n    extraIdentityA?: IdentityConfigurationProperties;\n" +
        "    @visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)\n    @doc(\"extra b\")\n    extraIdentityB?",
      modelContent: "IdentityConfigurationProperties",
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
    // PascalCase preserved with a plain "_<verb>" suffix, matching Swagger.
    expect(result!).toContain("IdentityConfigurationProperties_");
    // no lowercased-tail collapse and no CreateOrUpdate infix.
    expect(result!).not.toContain("Identityconfigurationproperties");
    expect(result!).not.toContain("CreateOrUpdate");
  });
});
