import { http, HttpResponse } from "msw";

export const handlers = [
  // Workspace API handlers - using full URLs to match axios requests
  http.get("http://localhost:3000/AAZ/Editor/Workspaces", () => {
    return HttpResponse.json([
      {
        name: "test-workspace-1",
        plane: "azure-cli",
        updated: Math.floor(Date.now() / 1000) - 86400, // Yesterday
        url: "/workspace/test-workspace-1",
        folder: "/workspaces/test-workspace-1",
      },
      {
        name: "test-workspace-2",
        plane: "azure-cli-extensions",
        updated: Math.floor(Date.now() / 1000) - 172800, // 2 days ago
        url: "/workspace/test-workspace-2",
        folder: "/workspaces/test-workspace-2",
      },
    ]);
  }),

  http.post("http://localhost:3000/AAZ/Editor/Workspaces", async ({ request }) => {
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

  http.delete("http://localhost:3000/AAZ/Editor/Workspaces/:name", ({ params }) => {
    return HttpResponse.json({
      message: `Workspace ${params.name} deleted successfully`,
    });
  }),

  http.post("http://localhost:3000/workspace/:name/Rename", async ({ request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json({
      name: body.name,
    });
  }),

  http.get("http://localhost:3000/workspace/:name/ClientConfig", () => {
    return HttpResponse.json({
      version: "1.0.0",
      auth: {
        type: "default",
      },
      endpoints: {
        type: "template",
        templates: [
          {
            cloud: "AzureCloud",
            template: "https://management.azure.com/",
          },
        ],
      },
    });
  }),

  http.post("http://localhost:3000/workspace/:name/ClientConfig", () => {
    return HttpResponse.json({ message: "Client config updated successfully" });
  }),

  http.get("http://localhost:3000/workspace/:name", ({ params }) => {
    return HttpResponse.json({
      name: params.name,
      plane: "azure-cli",
      folder: `/workspaces/${params.name}`,
      commandTree: {},
    });
  }),

  // Specs API handlers
  http.get("http://localhost:3000/AAZ/Specs/Planes", () => {
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

  http.get("http://localhost:3000/AAZ/Specs/Planes/:planeName/Modules", ({ params }) => {
    if (params.planeName === "azure-cli") {
      return HttpResponse.json(["storage", "compute", "network", "keyvault"]);
    }
    return HttpResponse.json(["extensions-module"]);
  }),

  http.get("http://localhost:3000/Swagger/Specs/:planeName/:moduleName/ResourceProviders", () => {
    const resourceProviders = ["Microsoft.Storage", "Microsoft.Compute", "Microsoft.Network", "Microsoft.KeyVault"];
    return HttpResponse.json(resourceProviders);
  }),

  // CLI API handlers
  http.get("http://localhost:3000/CLI/Az/Modules", () => {
    return HttpResponse.json([
      {
        name: "test-module",
        path: "/modules/test-module",
      },
    ]);
  }),

  http.post("http://localhost:3000/CLI/Az/Modules/:module", async ({ params, request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json({
      message: `Module ${params.module} generated successfully`,
      profiles: body.profiles || {},
    });
  }),

  // Error scenarios for testing
  http.get("http://localhost:3000/AAZ/Editor/Workspaces/error", () => {
    return HttpResponse.json(
      { message: "Internal server error", details: "Database connection failed" },
      { status: 500 },
    );
  }),

  http.post("http://localhost:3000/AAZ/Editor/Workspaces/validation-error", () => {
    return HttpResponse.json({ message: "Validation failed", details: { name: "Name is required" } }, { status: 400 });
  }),
];
