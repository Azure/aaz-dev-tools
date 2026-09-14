import { describe, expect, it } from "vitest";
import { compileTypespecAAZOperations } from "./test-aaz.js";

// Some data-plane services (e.g. monitor OperationalInsights) declare a literal property named
// `additionalProperties` on their error model. It must not stop the error format classification.
const code = `
  @versioned(Versions)
  @service(#{ title: "My service" })
  namespace Service;

  enum Versions {A}

  model ErrorInfo {
    code: string;
    message: string;
    details?: ErrorInfo[];
    innererror?: ErrorInfo;
    #suppress "@azure-tools/typespec-azure-core/bad-record-type" "This is an arbitrary object"
    additionalProperties?: Record<unknown>;
  }

  @error
  model ErrorResponse {
    error: ErrorInfo;
  }

  model Q {
    q: string;
  }

  #suppress "@azure-tools/typespec-azure-core/use-standard-operations" "This is a test."
  @route("/test1")
  @get
  op test1(): Q | ErrorResponse;
`.trim();

describe("Typespec AAZ Emitter Error Format", () => {
  it("classifies an error model carrying an `additionalProperties` property", async () => {
    const result = await compileTypespecAAZOperations(code, {
      "operation": "get-resources-operations",
      "api-version": "A",
      "resources": ["/test1"],
    });
    const responses = JSON.parse(result!)[0].pathItem.get.read.http.responses;
    const errorResponse = responses.find((r: any) => r.isError);
    expect(errorResponse.body.json.schema.type).toBe("@ODataV4Format");
  });
});
