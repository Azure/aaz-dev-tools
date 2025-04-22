import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner } from "./test-aaz.js";

describe("AAZ Compiler Validation", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate basic compiler", async () => {
    const code: string = `
      namespace Test;
      @test
      model Simple {
        id: string;
        name: string;
      }
    `;
    const result = await runner.compile(code, {
      emit: ["@azure-tools/typespec-aaz"],
      options: {
        "@azure-tools/typespec-aaz": { operation: "list-resources" },
      },
      outputDir: "tsp-output",
    });
    expect(result.Simple).toBeDefined();
    expect(result.Simple.kind).toBe("Model");

    if (result.Simple.kind === "Model") {
      expect(result.Simple.properties.has("id")).toBe(true);
      expect(result.Simple.properties.has("name")).toBe(true);
    }
  });
});
