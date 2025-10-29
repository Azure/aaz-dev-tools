import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/AAZ/Editor/Workspaces", () => {
    console.log("🟢 [MSW] hit /AAZ/Editor/Workspaces");
    return HttpResponse.json([
      {
        name: "test-workspace-1",
        plane: "azure-cli",
        updated: Math.floor(Date.now() / 1000) - 86400,
        url: "/AAZ/Editor/Workspaces/test-workspace-1",
        folder: "/workspaces/test-workspace-1",
      },
      {
        name: "test-workspace-2",
        plane: "azure-cli-extensions",
        updated: Math.floor(Date.now() / 1000) - 172800,
        url: "/AAZ/Editor/Workspaces/test-workspace-2",
        folder: "/workspaces/test-workspace-2",
      },
    ]);
  }),

  http.post("/AAZ/Editor/Workspaces", async ({ request }) => {
    console.log("🟢 [MSW] hit /AAZ/Editor/Workspaces");
    const body = (await request.json()) as any;
    return HttpResponse.json(
      {
        name: body.name,
        plane: body.plane,
        modNames: body.modNames,
        resourceProvider: body.resourceProvider,
        updated: Math.floor(Date.now() / 1000),
        url: `/AAZ/Editor/Workspaces/${body.name}`,
        folder: `/workspaces/${body.name}`,
      },
      { status: 201 },
    );
  }),

  http.delete("/AAZ/Editor/Workspaces/:name", ({ params }) => {
    console.log("🟢 [MSW] hit /AAZ/Editor/Workspaces?:name");
    return HttpResponse.json({
      message: `Workspace ${params.name} deleted successfully`,
    });
  }),

  http.post("/AAZ/Editor/Workspaces/:name/Rename", async ({ request }) => {
    console.log("🟢 [MSW] hit /AAZ/Editor/Workspaces/:name/Rename");
    const body = (await request.json()) as any;
    return HttpResponse.json({
      name: body.name,
    });
  }),

  http.get("/AAZ/Editor/Workspaces/:name/ClientConfig", ({ request, params }) => {
    console.log("🟢 [MSW] hit /AAZ/Editor/Workspaces/:name/ClientConfig");
    const url = new URL(request.url);
    if (url.searchParams.get("simulate404") === "true" || params.name === "nonexistent") {
      return HttpResponse.json({ message: "Client config not found" }, { status: 404 });
    }

    return HttpResponse.json({
      version: "1.0.0",
      auth: {
        aad: {
          scopes: ["https://management.azure.com/.default"],
        },
      },
      endpoints: {
        type: "template",
        templates: [
          {
            cloud: "AzureCloud",
            template: "https://management.azure.com/AzureCloudTemplate",
          },
          {
            cloud: "AzureChinaCloud",
            template: "https://management.azure.com/AzureCloudChina",
          },
        ],
        cloudMetadata: {
          selectorIndex: "cloud",
          prefixTemplate: "https://{cloud}.management.azure.com/",
        },
      },
    });
  }),

  http.post("/AAZ/Editor/Workspaces/:name/ClientConfig", () => {
    return HttpResponse.json({ message: "Client config updated successfully" });
  }),

  http.get("/AAZ/Editor/Workspaces/:name", ({ params }) => {
    return HttpResponse.json({
      name: params.name,
      plane: `data-plane${params.name}`,
      folder: `/workspaces/${params.name}`,
      resourceProvider: `${params.name}`,
      commandTree: {
        names: ["aaz"],
      },
    });
  }),

  http.get("/AAZ/Specs/Planes", () => {
    return HttpResponse.json([
      {
        client: "MgmtClient",
        displayName: "Control plane",
        name: "mgmt-plane",
      },
      {
        client: "DataPlaneClient",
        displayName: "Data plane",
        name: "data-plane",
      },
    ]);
  }),

  http.get("/AAZ/Specs/Planes/:planeName/Modules", () => {
    return HttpResponse.json(["storage", "compute", "network", "keyvault"]);
  }),

  http.get("/Swagger/Specs/mgmt-plane", () => {
    return HttpResponse.json([
      { url: "/Swagger/Specs/mgmt-plane/addons", name: "addons" },
      { url: "/Swagger/Specs/mgmt-plane/compute", name: "compute" },
      { url: "/Swagger/Specs/mgmt-plane/network", name: "network" },
      { url: "/Swagger/Specs/mgmt-plane/keyvault", name: "keyvault" },
      { url: "/Swagger/Specs/mgmt-plane/containerservice", name: "containerservice" },
      { url: "/Swagger/Specs/mgmt-plane/storage", name: "storage" },
    ]);
  }),

  // Resources
  http.get("/Swagger/Specs/mgmt-plane/:moduleName/ResourceProviders/:rp/Resources", ({ params }) => {
    let rpName = params.rp + "";
    switch (rpName?.toLowerCase()) {
      case "storage":
        rpName = "Microsoft.Storage";
        break;
      case "compute":
        rpName = "Microsoft.Compute";
        break;
      case "network":
        rpName = "Microsoft.Network";
        break;
      case "keyvault":
        rpName = "Microsoft.KeyVault";
        break;
      case "addons":
        rpName = "Microsoft.Addons";
        break;
    }

    switch (rpName) {
      case "Microsoft.Storage":
        return HttpResponse.json([
          {
            id: "storageAccounts",
            versions: [
              { version: "2021-04-01", operations: { read: "GET", write: "PUT", delete: "DELETE", listKeys: "GET" } },
              { version: "2021-09-01", operations: { read: "GET", write: "PUT", delete: "DELETE", listKeys: "GET" } },
              { version: "2022-09-01", operations: { read: "GET", write: "PUT", delete: "DELETE", listKeys: "GET" } },
              { version: "2023-01-01", operations: { read: "GET", write: "PUT", delete: "DELETE", listKeys: "GET" } },
            ],
          },
          {
            id: "storageAccounts/blobServices",
            versions: [
              { version: "2021-04-01", operations: { read: "GET", write: "PUT" } },
              { version: "2021-09-01", operations: { read: "GET", write: "PUT" } },
              { version: "2022-09-01", operations: { read: "GET", write: "PUT" } },
            ],
          },
        ]);

      case "Microsoft.Compute":
        return HttpResponse.json([
          {
            id: "virtualMachines",
            versions: [
              {
                version: "2021-03-01",
                operations: { read: "GET", write: "PUT", delete: "DELETE", start: "POST", stop: "POST" },
              },
              {
                version: "2022-03-01",
                operations: { read: "GET", write: "PUT", delete: "DELETE", start: "POST", stop: "POST" },
              },
              {
                version: "2023-03-01",
                operations: { read: "GET", write: "PUT", delete: "DELETE", start: "POST", stop: "POST" },
              },
            ],
          },
          {
            id: "disks",
            versions: [
              { version: "2021-04-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
              { version: "2022-03-02", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
            ],
          },
        ]);

      case "Microsoft.Network":
        return HttpResponse.json([
          {
            id: "virtualNetworks",
            versions: [
              { version: "2021-02-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
              { version: "2022-01-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
              { version: "2023-02-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
            ],
          },
          {
            id: "loadBalancers",
            versions: [
              { version: "2021-02-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
              { version: "2022-01-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
            ],
          },
        ]);

      case "Microsoft.KeyVault":
        return HttpResponse.json([
          {
            id: "vaults",
            versions: [
              { version: "2021-10-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
              { version: "2022-07-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
              { version: "2023-02-01", operations: { read: "GET", write: "PUT", delete: "DELETE" } },
            ],
          },
        ]);

      case "Microsoft.Addons":
        return HttpResponse.json([
          {
            id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes/{}",
            opGroup: "SupportPlanType",
            versions: [
              {
                version: "2017-05-15",
                operations: {
                  SupportPlanTypes_CreateOrUpdate: "PUT",
                  SupportPlanTypes_Delete: "DELETE",
                  SupportPlanTypes_Get: "GET",
                },
              },
              {
                version: "2018-03-01",
                operations: {
                  SupportPlanTypes_CreateOrUpdate: "PUT",
                  SupportPlanTypes_Delete: "DELETE",
                  SupportPlanTypes_Get: "GET",
                },
              },
            ],
          },
          {
            id: "/subscriptions/{}/providers/microsoft.addons/supportproviders/{}/supportplantypes",
            opGroup: "CanonicalSupportPlanType",
            versions: [
              {
                version: "2017-05-15",
                operations: { CanonicalSupportPlanTypes_Get: "GET" },
              },
            ],
          },
        ]);

      default:
        return HttpResponse.json([]);
    }
  }),

  // Resource providers:
  http.get("/Swagger/Specs/:planeName/:moduleName/ResourceProviders", ({ params }) => {
    return HttpResponse.json([
      {
        entryFiles: [`specification/${params.moduleName}/Microsoft.BlobStorage/main.tsp`],
        name: `Microsoft.${params.moduleName}`,
        type: "TypeSpec",
        url: `/Swagger/Specs/${params.planeName}/${params.moduleName}/ResourceProviders/${params.moduleName}`,
      },
    ]);
  }),

  http.get("/CLI/Az/Modules", () => {
    return HttpResponse.json([
      {
        name: "test-module",
        path: "/modules/test-module",
      },
    ]);
  }),

  http.post("/CLI/Az/Modules/:module", async ({ params, request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json({
      message: `Module ${params.module} generated successfully`,
      profiles: body.profiles || {},
    });
  }),

  http.get("/AAZ/Editor/Workspaces/:name/CommandTree/Nodes/aaz/*/Leaves/:commandName", () => {
    const response = {
      names: ["network", "lb", "address-pool", "create"],
      help: {
        short: "Create a load balancer backend address pool",
        lines: [
          "Create a new load balancer backend address pool with specified parameters.",
          "This command creates a backend address pool in the specified load balancer.",
        ],
      },
      stage: "Stable",
      version: "2.0.0",
      examples: [
        {
          name: "Create a storage account",
          commands: [
            "network lb address-pool create --name mystorageaccount --resource-group myresourcegroup --location eastus",
          ],
        },
      ],
      resources: [
        {
          id: "Microsoft.Storage/storageAccounts",
          version: "2021-09-01",
          swagger: "/swagger/storage/2021-09-01/storage.json",
        },
      ],
      outputs: [
        {
          type: "object",
          ref: "StorageAccount",
          clientFlatten: false,
        },
      ],
      argGroups: [
        {
          name: "Properties",
          args: [
            {
              var: "backend_addresses",
              options: ["--backend-addresses"],
              help: {
                short: "An array of backend addresses.",
              },
              required: false,
              type: "array<object>",
              stage: "Stable",
              hide: false,
              group: "Properties",
              nullable: false,
              item: {
                type: "object",
                args: [
                  {
                    var: "name",
                    options: ["--name"],
                    help: {
                      short: "Name of the backend address.",
                    },
                    required: false,
                    type: "string",
                    stage: "Stable",
                    hide: false,
                    group: "",
                    nullable: false,
                  },
                  {
                    var: "ip_address",
                    options: ["--ip-address"],
                    help: {
                      short: "IP Address belonging to the referenced virtual network.",
                    },
                    required: false,
                    type: "string",
                    stage: "Stable",
                    hide: false,
                    group: "Properties",
                    nullable: false,
                  },
                ],
              },
            },
          ],
        },
      ],
      clsArgDefineMap: {},
    };
    return HttpResponse.json(response);
  }),

  http.get("/AAZ/Editor/Workspaces/:workspaceName/SwaggerDefault", ({ params }) => {
    return HttpResponse.json({
      modNames: [`${params.workspaceName}`],
      plane: `data-plane:${params.workspaceName}`,
      rpName: `${params.workspaceName}`,
      source: "TypeSpec",
    });
  }),

  http.get("/workspace/:name/Resources/*/V/*/Commands", () => {
    return HttpResponse.json([
      {
        names: ["storage", "account", "create"],
        help: {
          short: "Create a storage account",
        },
        stage: "Stable",
        version: "2.0.0",
        resources: [
          {
            id: "Microsoft.Storage/storageAccounts",
            version: "2021-09-01",
            swagger: "/swagger/storage/2021-09-01/storage.json",
          },
        ],
      },
    ]);
  }),

  http.get("/workspace/:name/Resources/*/V/*/Subresources/*/Commands", () => {
    return HttpResponse.json([
      {
        names: ["storage", "account", "create"],
        help: {
          short: "Create a storage account",
        },
        stage: "Stable",
        version: "2.0.0",
        resources: [
          {
            id: "Microsoft.Storage/storageAccounts",
            version: "2021-09-01",
            swagger: "/swagger/storage/2021-09-01/storage.json",
          },
        ],
      },
    ]);
  }),

  http.delete("/workspace/:name/Resources/*/V/*", () => {
    return HttpResponse.json({ message: "Resource deleted successfully" });
  }),

  http.delete("/workspace/:name/Resources/*/V/*/Subresources/*", () => {
    return HttpResponse.json({ message: "Subresource deleted successfully" });
  }),

  http.get("/AAZ/Editor/Workspaces/error", () => {
    return HttpResponse.json(
      { message: "Internal server error", details: "Database connection failed" },
      { status: 500 },
    );
  }),

  http.post("/AAZ/Editor/Workspaces/validation-error", () => {
    return HttpResponse.json({ message: "Validation failed", details: { name: "Name is required" } }, { status: 400 });
  }),
];
