import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { generateCompileTemplate } from "./util.js";

describe("Typespec AAZ Emitter Operations", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate list resources", async () => {
    const code: string = generateCompileTemplate();
    const result = await compileTypespecAAZOperations(code, { operation: "list-resources" }, runner);
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    expect(resultObj[0]).toMatchObject({
      id: "/test1",
      versions: expect.any(Array),
    });
    resultObj![0].versions.forEach((item: any) => {
      expect(item).toMatchObject({
        id: "/test1",
        path: "/test1",
        version: expect.any(String),
      });
    });
    expect(resultObj![0].versions[0].version).toBe("A");
    expect(resultObj![0].versions[1].version).toBe("B");
    expect(resultObj![0].versions[2].version).toBe("C");
  });

  it("validate get resources operations", async () => {
    const code: string = generateCompileTemplate();
    const result = await compileTypespecAAZOperations(code, {
      "operation": "get-resources-operations",
      "api-version": "A",
      "resources": ["/test1"],
    });
    const resultObj = JSON.parse(result!);
    expect(Array.isArray(resultObj)).toBe(true);
    expect(resultObj.length).toBe(1);
    expect(resultObj[0].id).toBe("/test1");
    expect(resultObj[0].path).toBe("/test1");
    expect(resultObj[0].version).toBe("A");
    await expect(JSON.stringify(resultObj[0].pathItem.get.read.http.request, null, 2)).toMatchFileSnapshot(
      "./snapshots/emitter-operation-request-object.json",
    );
    await expect(JSON.stringify(resultObj[0].pathItem.get.read.http.request, null, 2)).toMatchFileSnapshot(
      "./snapshots/emitter-operation-responses-object.json",
    );
  });
});
