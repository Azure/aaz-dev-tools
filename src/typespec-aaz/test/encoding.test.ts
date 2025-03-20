import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { ModelVar, generateCompileArmResourceTemplate, findObjectsWithKey } from "./util.js";

describe("encoding parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate encoding duration with default", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetValue",
      modelContent: "TargetEncodingModel",
      isComposite: true,
      appendModel: `
      model TargetEncodingModel {
        @encode(DurationKnownEncoding.seconds, int32)
        errorRateTimeWindowInSeconds?: duration = duration.fromISO("PT60S");
      }
      `,
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
    await expect(JSON.stringify(targetObj, null, 2)).toMatchFileSnapshot("./snapshots/encoding-duration-prop.json");
  });
});
