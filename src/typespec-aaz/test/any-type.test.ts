import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { ModelVar, generateCompileArmResourceTemplate, findObjectsWithKey } from "./util.js";

describe("any type parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate any type value", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetValue",
      modelContent: "unknown",
    };

    const code: string = generateCompileArmResourceTemplate(modelTmp);
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/mockresources/{}"],
      },
      runner,
    );
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    const targetObj = findObjectsWithKey(resultObj[0].pathItem.get.read.http.responses, "targetValue");
    const anyTypeObj = JSON.stringify(targetObj, null, 2);
    await expect(anyTypeObj).toMatchFileSnapshot("./snapshots/any-type-prop.json");
  });

  it("validate any type object", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetValue",
      modelContent: "Record<unknown>",
    };

    const code: string = generateCompileArmResourceTemplate(modelTmp);
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/mockresources/{}"],
      },
      runner,
    );
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    const targetObj = findObjectsWithKey(resultObj[0].pathItem.get.read.http.responses, "targetValue");
    const anyTypeObj = JSON.stringify(targetObj, null, 2);
    await expect(anyTypeObj).toMatchFileSnapshot("./snapshots/any-type-object.json");
  });
});
