type JSONValue = string | number | boolean | null | JSONObject | JSONArray;
interface JSONObject {
  [key: string]: JSONValue;
}
interface JSONArray extends Array<JSONValue> {}

export interface ModelVar {
  modelKey: string;
  modelContent: string;
  isComposite?: boolean;
  appendModel?: string;
}

function generateModelBase(modelVar: ModelVar | undefined) {
  if (modelVar && modelVar.modelKey && modelVar.modelContent) {
    return `${modelVar.modelKey}: ${modelVar.modelContent};`;
  } else {
    return ``;
  }
}

function generateCompositeModel(modelVar: ModelVar | undefined) {
  if (modelVar && modelVar.isComposite && modelVar.appendModel) {
    return `${modelVar.appendModel};`;
  } else {
    return ``;
  }
}

export function generateCompileTemplate(modelVar?: ModelVar) {
  return `
    @versioned(Versions)
    @service(#{ title: "My service" })
    namespace Service;

    enum Versions {A, B, C}
    
    ${generateCompositeModel(modelVar)}

    model P {
      p: string;
      ${generateModelBase(modelVar)}
    }
    model Q {
      q: string;
    }

    #suppress "@azure-tools/typespec-azure-core/use-standard-operations" "This is a test."
    @route("/test1")
    @get
    op test1(p: P): Q;
    `.trim();
}

export function generateCompileArmResourceTemplate(modelVar?: ModelVar) {
  return `
  @armProviderNamespace("Microsoft.Mock")
  @service(#{ title: "Microsoft.Mock" })
  @versioned(Versions)
  namespace Microsoft.Mock;

  enum Versions {
    A,
  }

  interface Operations extends Azure.ResourceManager.Operations {}

  @doc("A Mock resource")
  model MockResource is TrackedResource<MockResourceProperties> {
    @doc("The name of the Mock Resource")
    @pattern("^[a-zA-Z0-9-]{3,24}$")
    @key("mockName")
    @segment("mockResources")
    @path
    name: string;

    ...ResourceSkuProperty;
  }

  @doc("The status of the current operation.")
  @Azure.Core.lroStatus
  union ProvisioningState {
    string,
    ResourceProvisioningState,

    @doc("Initial provisioning in progress")
    Provisioning: "Provisioning",

    @doc("Update in progress")
    Updating: "Updating",

    @doc("Deletion in progress")
    Deleting: "Deleting",

    @doc("Change accepted for processing")
    Accepted: "Accepted",
  }

  @doc("Details of the mock Identity Configuration")
  model IdentityConfigurationProperties {
    @visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)
    @doc("The identity type of the mock Resource")
    identityType: string;

    @visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)
    @doc("To indicate whether the mock Resource has Teams enabled")
    teamsEnabled?: boolean = false;

    @visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)
    @doc("The name of the authentication policy registered in ADB2C for the mock Resource")
    b2cAuthenticationPolicy?: string;
  }

  ${generateCompositeModel(modelVar)}

  @doc("Details of the mock property.")
  model MockResourceProperties {
    ${generateModelBase(modelVar)}
  
    @visibility(Lifecycle.Read, Lifecycle.Create)
    @doc("The portal name (website name) of the mock instance")
    portalName: string;

    @visibility(Lifecycle.Read, Lifecycle.Create, Lifecycle.Update)
    @doc("The identity configuration of the mock resource")
    identityConfiguration: IdentityConfigurationProperties;
    
    @visibility(Lifecycle.Read, Lifecycle.Create)
    @doc("To indicate whether the mock instance has Zone Redundancy enabled")
    zoneRedundancyEnabled: boolean;

    @visibility(Lifecycle.Read, Lifecycle.Create)
    @doc("To indicate whether the mock instance has Disaster Recovery enabled")
    disasterRecoveryEnabled: boolean;

    @visibility(Lifecycle.Read)
    @doc("The status of the last operation.")
    provisioningState?: ProvisioningState;
  }

  #suppress "deprecated" "Existing API"
  @armResourceOperations
  interface MockResources {
    get is ArmResourceRead<MockResource>;
    #suppress "@azure-tools/typespec-azure-core/invalid-final-state" "MUST CHANGE ON NEXT UPDATE"
    @Azure.Core.useFinalStateVia("azure-async-operation")
    create is ArmResourceCreateOrUpdateAsync<
      MockResource,
      LroHeaders = Azure.Core.Foundations.RetryAfterHeader
    >;
    update is ArmCustomPatchAsync<
      MockResource,
      Azure.ResourceManager.Foundations.ResourceUpdateModel<
        MockResource,
        MockResourceProperties
      >
    >;
    delete is ArmResourceDeleteAsync<MockResource>;
    listByResourceGroup is ArmResourceListByParent<MockResource>;
    listBySubscription is ArmListBySubscription<MockResource>;
  }
  `;
}

export function findObjectsWithKey(obj: JSONValue, targetKey: string) {
  let result: JSONObject | undefined = undefined;

  function search(value: JSONValue) {
    if (Array.isArray(value)) {
      value.forEach((item) => search(item));
    } else if (typeof value === "object" && value !== null) {
      const jsonObj = value as JSONObject;
      if (targetKey === jsonObj.name) {
        result = jsonObj;
      }
      Object.values(jsonObj).forEach((val) => search(val));
    }
  }
  search(obj);
  return result;
}
