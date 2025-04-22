import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { generateCompileArmResourceTemplate } from "./util.js";

describe("arm resource parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate arm resource template", async () => {
    const code: string = generateCompileArmResourceTemplate();
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
    expect(resultObj[0].id).toBe("/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/mockresources/{}");
    expect(resultObj[0].path).toBe(
      "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Mock/mockResources/{mockName}",
    );
    expect(resultObj[0].version).toBe("A");
    const requestJson = JSON.stringify(resultObj[0].pathItem.get.read.http.request, null, 2);
    const responsesJson = JSON.stringify(resultObj[0].pathItem.get.read.http.responses, null, 2);
    await expect(requestJson).toMatchFileSnapshot("./snapshots/arm-resource-template-request.json");
    await expect(responsesJson).toMatchFileSnapshot("./snapshots/arm-resource-template-resources.json");
  });
});
