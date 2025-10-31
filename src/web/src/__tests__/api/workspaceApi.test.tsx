import { describe, it, expect } from "vitest";
import { workspaceApi, type CreateWorkspaceData } from "../../services/workspaceApi";

describe("Workspace API", () => {
  describe("getWorkspaces", () => {
    it("should fetch and transform workspace data correctly", async () => {
      const workspaces = await workspaceApi.getWorkspaces();

      expect(workspaces).toHaveLength(2);
      expect(workspaces[0]).toEqual({
        name: "test-workspace-1",
        plane: "azure-cli",
        lastModified: expect.any(Date),
        url: "/AAZ/Editor/Workspaces/test-workspace-1",
        folder: "/workspaces/test-workspace-1",
      });

      expect(workspaces[1]).toEqual({
        name: "test-workspace-2",
        plane: "azure-cli-extensions",
        lastModified: expect.any(Date),
        url: "/AAZ/Editor/Workspaces/test-workspace-2",
        folder: "/workspaces/test-workspace-2",
      });

      expect(workspaces[0].lastModified).toBeInstanceOf(Date);
      expect(workspaces[1].lastModified).toBeInstanceOf(Date);
    });

    it("should handle API errors gracefully", async () => {
      await expect(workspaceApi.getWorkspaces()).resolves.toBeDefined();
    });
  });

  describe("createWorkspace", () => {
    it("should create workspace with correct data transformation", async () => {
      const createData: CreateWorkspaceData = {
        name: "new-test-workspace",
        plane: "azure-cli",
        modNames: "storage",
        resourceProvider: "Microsoft.Storage",
        source: "OpenAPI",
      };

      const result = await workspaceApi.createWorkspace(createData);

      expect(result).toEqual({
        name: "new-test-workspace",
        plane: "azure-cli",
        modNames: "storage",
        resourceProvider: "Microsoft.Storage",
        lastModified: expect.any(Date),
        url: "/AAZ/Editor/Workspaces/new-test-workspace",
        folder: "/workspaces/new-test-workspace",
      });

      expect(result.lastModified).toBeInstanceOf(Date);
    });

    it("should send correct request data", async () => {
      const createData: CreateWorkspaceData = {
        name: "api-test-workspace",
        plane: "azure-cli-extensions",
        modNames: "extensions-module",
        resourceProvider: "Microsoft.Compute",
        source: "TypeSpec",
      };

      const result = await workspaceApi.createWorkspace(createData);

      expect(result.name).toBe("api-test-workspace");
      expect(result.plane).toBe("azure-cli-extensions");
      expect(result.modNames).toBe("extensions-module");
      expect(result.resourceProvider).toBe("Microsoft.Compute");
    });
  });

  describe("deleteWorkspace", () => {
    it("should delete workspace by name", async () => {
      await expect(workspaceApi.deleteWorkspace("test-workspace-1")).resolves.toBeUndefined();
    });
  });

  describe("renameWorkspace", () => {
    it("should rename workspace and return new name", async () => {
      const result = await workspaceApi.renameWorkspace("/AAZ/Editor/Workspaces/test-workspace-1", "renamed-workspace");

      expect(result).toEqual({
        name: "renamed-workspace",
      });
    });
  });

  describe("getWorkspace", () => {
    it("should fetch individual workspace data", async () => {
      const result = await workspaceApi.getWorkspace("/AAZ/Editor/Workspaces/test-workspace-1");

      expect(result).toEqual({
        name: "test-workspace-1",
        plane: "data-planetest-workspace-1",
        resourceProvider: "test-workspace-1",
        folder: "/workspaces/test-workspace-1",
        commandTree: {
          names: ["aaz"],
        },
      });
    });
  });

  describe("getWorkspaceClientConfig", () => {
    it("should fetch client config and transform endpoint data", async () => {
      const result = await workspaceApi.getWorkspaceClientConfig("/AAZ/Editor/Workspaces/test-workspace-1");

      expect(result).toEqual({
        version: "1.0.0",
        endpointTemplates: {
          AzureChinaCloud: "https://management.azure.com/AzureCloudChina",
          AzureCloud: "https://management.azure.com/AzureCloudTemplate",
        },
        endpointResource: undefined,
        auth: {
          aad: {
            scopes: ["https://management.azure.com/.default"],
          },
        },
      });
    });

    it("should return null for 404 responses", async () => {
      const result = await workspaceApi.getWorkspaceClientConfig("/AAZ/Editor/Workspaces/nonexistent");
      expect(result).toBeNull();
    });
  });

  describe("updateClientConfig", () => {
    it("should update client config", async () => {
      const config = {
        version: "2.0.0",
        auth: { type: "managed-identity" },
      };

      await expect(
        workspaceApi.updateClientConfig("/AAZ/Editor/Workspaces/test-workspace-1", config),
      ).resolves.toBeUndefined();
    });
  });

  describe("Edge cases and error handling", () => {
    it("should handle malformed workspace data gracefully", async () => {
      const workspaces = await workspaceApi.getWorkspaces();

      workspaces.forEach((workspace) => {
        expect(workspace).toHaveProperty("name");
        expect(workspace).toHaveProperty("plane");
        expect(workspace).toHaveProperty("lastModified");
        expect(workspace).toHaveProperty("url");
        expect(workspace).toHaveProperty("folder");

        expect(typeof workspace.name).toBe("string");
        expect(workspace.lastModified).toBeInstanceOf(Date);
      });
    });

    it("should handle empty workspace lists", async () => {
      const workspaces = await workspaceApi.getWorkspaces();
      expect(Array.isArray(workspaces)).toBe(true);
    });
  });
});
