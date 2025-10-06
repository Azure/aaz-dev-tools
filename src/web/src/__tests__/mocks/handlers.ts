import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/AAZ/Editor/Workspaces", () => {
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
    return HttpResponse.json({
      message: `Workspace ${params.name} deleted successfully`,
    });
  }),

  http.post("/AAZ/Editor/Workspaces/:name/Rename", async ({ request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json({
      name: body.name,
    });
  }),

  http.get("/AAZ/Editor/Workspaces/:name/ClientConfig", ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get("simulate404") === "true") {
      return new HttpResponse(null, { status: 404 });
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
      plane: "azure-cli",
      folder: `/workspaces/${params.name}`,
      commandTree: {},
    });
  }),

  http.get("/AAZ/Specs/Planes", () => {
    return HttpResponse.json([
      {
        name: "azure-cli",
        displayName: "Azure CLI",
        moduleOptions: ["storage", "compute", "network"],
      },
      {
        name: "azure-cli-extensions",
        displayName: "Azure CLI Extensions",
        moduleOptions: [],
      },
    ]);
  }),

  http.get("/AAZ/Specs/Planes/:planeName/Modules", ({ params }) => {
    if (params.planeName === "azure-cli") {
      return HttpResponse.json(["storage", "compute", "network", "keyvault"]);
    }
    return HttpResponse.json(["extensions-module"]);
  }),

  http.get("/Swagger/Specs/:planeName/:moduleName/ResourceProviders", () => {
    const resourceProviders = ["Microsoft.Storage", "Microsoft.Compute", "Microsoft.Network", "Microsoft.KeyVault"];
    return HttpResponse.json(resourceProviders);
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
