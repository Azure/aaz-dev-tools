import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/AAZ/Editor/Workspaces", () => {
    return HttpResponse.json([
      {
        name: "test-workspace-1",
        plane: "azure-cli",
        updated: Math.floor(Date.now() / 1000) - 86400,
        url: "/workspace/test-workspace-1",
        folder: "/workspaces/test-workspace-1",
      },
      {
        name: "test-workspace-2",
        plane: "azure-cli-extensions",
        updated: Math.floor(Date.now() / 1000) - 172800,
        url: "/workspace/test-workspace-2",
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
        url: `/workspace/${body.name}`,
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

  http.post("/workspace/:name/Rename", async ({ request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json({
      name: body.name,
    });
  }),

  http.get("/workspace/:name/ClientConfig", ({ request }) => {
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

  http.post("/workspace/:name/ClientConfig", () => {
    return HttpResponse.json({ message: "Client config updated successfully" });
  }),

  http.get("/workspace/:name", ({ params }) => {
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
