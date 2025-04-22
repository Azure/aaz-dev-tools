import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { ModelVar, generateCompileTemplate, findObjectsWithKey } from "./util.js";

describe("literal value parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate literal string", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetProp",
      modelContent: '"AzureVM"',
    };
    const code: string = generateCompileTemplate(modelTmp);
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/test1"],
      },
      runner,
    );
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    const targetObj = findObjectsWithKey(resultObj[0].pathItem.get.read.http.request, "targetProp");
    await expect(JSON.stringify(targetObj, null, 2)).toMatchFileSnapshot("./snapshots/literal-string-prop.json");
  });

  it("validate literal int", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetProp",
      modelContent: "12",
    };
    const code: string = generateCompileTemplate(modelTmp);
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/test1"],
      },
      runner,
    );
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    const targetObj = findObjectsWithKey(resultObj[0].pathItem.get.read.http.request, "targetProp");
    await expect(JSON.stringify(targetObj, null, 2)).toMatchFileSnapshot("./snapshots/literal-int-prop.json");
  });

  it("validate literal float", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetProp",
      modelContent: "12.5",
    };
    const code: string = generateCompileTemplate(modelTmp);
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/test1"],
      },
      runner,
    );
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    const targetObj = findObjectsWithKey(resultObj[0].pathItem.get.read.http.request, "targetProp");
    await expect(JSON.stringify(targetObj, null, 2)).toMatchFileSnapshot("./snapshots/literal-float-prop.json");
  });
});
