import { http, HttpResponse } from "msw";

export const handlers = [
  // Workspace API handlers
  http.get("/AAZ/Workspaces", () => {
    return HttpResponse.json([
      {
        name: "test-workspace-1",
        folder: "/workspaces/test-workspace-1",
        readme: "Test workspace for integration tests",
      },
      {
        name: "test-workspace-2",
        folder: "/workspaces/test-workspace-2",
        readme: "Another test workspace",
      },
    ]);
  }),

  http.post("/AAZ/Workspaces", async ({ request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json(
      {
        name: body.name,
        folder: `/workspaces/${body.name}`,
        readme: body.readme || "",
      },
      { status: 201 },
    );
  }),

  http.delete("/AAZ/Workspaces/:name", ({ params }) => {
    return HttpResponse.json({
      message: `Workspace ${params.name} deleted successfully`,
    });
  }),

  // CLI API handlers
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

  // Error scenarios for testing
  http.get("/AAZ/Workspaces/error", () => {
    return HttpResponse.json(
      { message: "Internal server error", details: "Database connection failed" },
      { status: 500 },
    );
  }),

  http.post("/AAZ/Workspaces/validation-error", () => {
    return HttpResponse.json({ message: "Validation failed", details: { name: "Name is required" } }, { status: 400 });
  }),
];
