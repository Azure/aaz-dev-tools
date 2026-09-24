import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { findObjectsWithKey } from "./util.js";

describe("http request parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("validate http request body with bytes", async () => {
    const code: string = `
    @versioned(Versions)
    @service(#{ title: "My service" })
    namespace Service;
    enum Versions {A, B, C}
    model P {
      @bodyRoot
      body: bytes;
    }
    model Q {
      q: string;
    }

    #suppress "@azure-tools/typespec-azure-core/use-standard-operations" "This is a test."
    @route("/test1")
    @get
    op test1(p: P): Q;
    `;
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
    const targetObj = findObjectsWithKey(resultObj[0].pathItem.get.read.http.request, "body");
    await expect(JSON.stringify(targetObj, null, 2)).toMatchFileSnapshot("./snapshots/http-request-bytes-body.json");
  });
});
