import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { ModelVar, generateCompileArmResourceTemplate, findObjectsWithKey } from "./util.js";

describe("discriminator parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate discriminator value", async () => {
    const modelTmp: ModelVar = {
      modelKey: "targetValue",
      modelContent: "TargetResourceConfigurations",
      isComposite: true,
      appendModel: `
      union ResourceKind {
        string,
        FunctionsFlexConsumption: "FunctionsFlexConsumption",
      }

      model FunctionFlexConsumptionResourceConfiguration {
        instanceMemoryMB: int64;
        httpConcurrency?: int64;
      }
        
      @discriminator("kind")
      model TargetResourceConfigurations {
        @visibility(Lifecycle.Create, Lifecycle.Read)
        kind: ResourceKind;
      }
      
      model FunctionFlexConsumptionTargetResourceConfigurations
        extends TargetResourceConfigurations {
        kind: ResourceKind.FunctionsFlexConsumption;
        configurations?: Record<FunctionFlexConsumptionResourceConfiguration>;
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
    await expect(JSON.stringify(targetObj, null, 2)).toMatchFileSnapshot("./snapshots/discriminator-prop.json");
  });
});
