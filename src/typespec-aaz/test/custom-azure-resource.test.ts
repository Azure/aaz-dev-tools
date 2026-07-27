import { TestHost, BasicTestRunner } from "@typespec/compiler/testing";
import { describe, expect, it, beforeEach } from "vitest";
import { createTypespecAazTestHost, createTypespecAazTestRunner, compileTypespecAAZOperations } from "./test-aaz.js";
import { findObjectsWithKey } from "./util.js";

function collectObjectsWithName(obj: any, targetName: string): any[] {
  const results: any[] = [];
  const search = (value: any): void => {
    if (Array.isArray(value)) {
      value.forEach(search);
    } else if (typeof value === "object" && value !== null) {
      if (value.name === targetName) {
        results.push(value);
      }
      Object.values(value).forEach(search);
    }
  };
  search(obj);
  return results;
}

// Legacy specs (e.g. Microsoft.Network) do not use the standard TrackedResource
// template. They mark their resource envelope with
// @Azure.ResourceManager.Legacy.customAzureResource(#{ isAzureResource: true }).
// isAzureResource() does not recognize those, so the emitter used to emit the
// resource "location" as a plain string instead of a ResourceLocation. See
// Azure/aaz-dev-tools#564.
const code = `
  @armProviderNamespace("Microsoft.Mock")
  @service(#{ title: "Microsoft.Mock" })
  @versioned(Versions)
  namespace Microsoft.Mock;

  enum Versions { A }

  interface Operations extends Azure.ResourceManager.Operations {}

  #suppress "@azure-tools/typespec-azure-core/no-legacy-usage" "test"
  @Azure.ResourceManager.Legacy.customAzureResource(#{ isAzureResource: true })
  model BaseResource {
    id?: string;
    @visibility(Lifecycle.Read) name?: string;
    @visibility(Lifecycle.Read) type?: string;
    location?: string;
    #suppress "@azure-tools/typespec-azure-resource-manager/arm-no-record" "test"
    tags?: Record<string>;
  }

  model MockResourceProperties {
    portalName?: string;
    subResource?: MockSubResource;
  }

  model MockSubResource {
    id?: string;
    subName?: string;
  }


  #suppress "@azure-tools/typespec-azure-core/composition-over-inheritance" "test"
  #suppress "@azure-tools/typespec-azure-core/no-legacy-usage" "test"
  model MockResource extends BaseResource {
    properties?: MockResourceProperties;

    @visibility(Lifecycle.Read)
    @path
    @key("mockName")
    @segment("mockResources")
    name: string;
  }

  #suppress "@azure-tools/typespec-azure-core/no-legacy-usage" "test"
  @armResourceOperations
  interface MockResources {
    createOrUpdate is ArmResourceCreateOrReplaceAsync<MockResource>;
  }
`;

describe("custom azure resource (legacy) parsing", () => {
  let host: TestHost;
  let runner: BasicTestRunner;

  beforeEach(async () => {
    host = await createTypespecAazTestHost();
    runner = await createTypespecAazTestRunner(host);
  });

  it("emits location as ResourceLocation for customAzureResource models", async () => {
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/mockresources/{}"],
      },
      runner,
    );
    expect(result).toBeTruthy();
    const location = findObjectsWithKey(JSON.parse(result!), "location") as { type?: string } | undefined;
    expect(location).toBeTruthy();
    expect(location?.type).toBe("ResourceLocation");
  });

  it("emits the resource envelope id as ResourceId while leaving nested ids as string", async () => {
    const result = await compileTypespecAAZOperations(
      code,
      {
        "operation": "get-resources-operations",
        "api-version": "A",
        "resources": ["/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/mockresources/{}"],
      },
      runner,
    );
    expect(result).toBeTruthy();
    const ids = collectObjectsWithName(JSON.parse(result!), "id");
    expect(ids.length).toBeGreaterThan(0);
    // The resource's own envelope id is converted to a ResourceId (so it gets hidden downstream).
    expect(ids.some((id) => id.type === "ResourceId")).toBe(true);
    // A nested, non-resource object's id must remain a plain string.
    expect(ids.some((id) => id.type === "string")).toBe(true);
  });
});
