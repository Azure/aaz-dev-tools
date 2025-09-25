import axios from "axios";

// Types for workspace operations
export interface Workspace {
  name: string;
  plane: string | null;
  modNames: string | null;
  resourceProvider: string | null;
  lastModified: Date | null;
  url: any | null;
  folder: string | null;
}

export interface CreateWorkspaceData {
  name: string;
  plane: string;
  modNames: string;
  resourceProvider: string;
  source: string;
}

export interface ClientConfig {
  version: string;
  endpointTemplates?: { [key: string]: string };
  endpointResource?: string;
  auth: any;
}

/**
 * Service for workspace-related API operations
 */
export class WorkspaceApiService {
  /**
   * Get all workspaces
   */
  static async getWorkspaces(): Promise<Workspace[]> {
    const res = await axios.get("/AAZ/Editor/Workspaces");
    return res.data.map((option: any) => ({
      name: option.name,
      lastModified: new Date(option.updated * 1000),
      url: option.url,
      plane: option.plane,
      folder: option.folder,
    }));
  }

  /**
   * Create a new workspace
   */
  static async createWorkspace(data: CreateWorkspaceData): Promise<Workspace> {
    const res = await axios.post("/AAZ/Editor/Workspaces", data);
    const workspace = res.data;
    return {
      name: workspace.name,
      plane: workspace.plane,
      modNames: workspace.modNames,
      resourceProvider: workspace.resourceProvider,
      lastModified: new Date(workspace.updated * 1000),
      url: workspace.url,
      folder: workspace.folder,
    };
  }

  /**
   * Get workspace details
   */
  static async getWorkspace(workspaceUrl: string): Promise<any> {
    const res = await axios.get(workspaceUrl);
    return res.data;
  }

  /**
   * Delete a workspace
   */
  static async deleteWorkspace(workspaceName: string): Promise<void> {
    const nodeUrl = `/AAZ/Editor/Workspaces/${workspaceName}`;
    await axios.delete(nodeUrl);
  }

  /**
   * Rename a workspace
   */
  static async renameWorkspace(workspaceUrl: string, newName: string): Promise<{ name: string }> {
    const res = await axios.post(`${workspaceUrl}/Rename`, { name: newName });
    return res.data;
  }

  /**
   * Get workspace client config
   */
  static async getWorkspaceClientConfig(workspaceUrl: string): Promise<ClientConfig | null> {
    try {
      const res = await axios.get(`${workspaceUrl}/ClientConfig`);
      const clientConfig: ClientConfig = {
        version: res.data.version,
        endpointTemplates: undefined,
        endpointResource: undefined,
        auth: res.data.auth,
      };

      if (res.data.endpoints.type === "template") {
        clientConfig.endpointTemplates = {};
        res.data.endpoints.templates.forEach((value: any) => {
          clientConfig.endpointTemplates![value.cloud] = value.template;
        });
      } else if (res.data.endpoints.type === "http-operation") {
        clientConfig.endpointResource = res.data.endpoints.endpointResource;
      }

      return clientConfig;
    } catch (err: any) {
      // catch 404 error
      if (err.response?.status === 404) {
        return null;
      }
      throw err;
    }
  }

  /**
   * Update workspace client config
   */
  static async updateClientConfig(workspaceUrl: string, config: any): Promise<void> {
    await axios.post(`${workspaceUrl}/ClientConfig`, config);
  }

  /**
   * Verify client config compatibility
   */
  static async verifyClientConfig(workspaceUrl: string): Promise<void> {
    const url = `${workspaceUrl}/ClientConfig/AAZ/Compare`;
    await axios.post(url);
  }

  /**
   * Inherit client config from AAZ
   */
  static async inheritClientConfig(workspaceUrl: string): Promise<void> {
    const url = `${workspaceUrl}/ClientConfig/AAZ/Inherit`;
    await axios.post(url);
  }

  /**
   * Generate/export workspace
   */
  static async generateWorkspace(workspaceUrl: string): Promise<void> {
    const url = `${workspaceUrl}/Generate`;
    await axios.post(url);
  }

  /**
   * Get workspace resources for reloading
   */
  static async getWorkspaceResources(workspaceUrl: string): Promise<any[]> {
    const res = await axios.get(`${workspaceUrl}/CommandTree/Nodes/aaz/Resources`);
    return res.data;
  }

  /**
   * Get workspace swagger default settings
   */
  static async getWorkspaceSwaggerDefault(workspaceName: string): Promise<any> {
    const res = await axios.get(`/AAZ/Editor/Workspaces/${workspaceName}/SwaggerDefault`);
    return res.data;
  }

  /**
   * Reload swagger resources
   */
  static async reloadSwaggerResources(workspaceUrl: string, data: any): Promise<void> {
    const reloadUrl = `${workspaceUrl}/Resources/ReloadSwagger`;
    await axios.post(reloadUrl, data);
  }

  /**
   * Reload TypeSpec resources
   */
  static async reloadTypespecResources(workspaceUrl: string, data: any): Promise<void> {
    const reloadUrl = `${workspaceUrl}/Resources/ReloadTypespec`;
    await axios.post(reloadUrl, data);
  }

  /**
   * Get workspace swagger default settings
   */
  static async getSwaggerDefault(workspaceName: string): Promise<any> {
    const res = await axios.get(`/AAZ/Editor/Workspaces/${workspaceName}/SwaggerDefault`);
    return res.data;
  }

  /**
   * Get workspace resources by workspace name (for swagger picker)
   */
  static async getWorkspaceResourcesByName(workspaceName: string): Promise<any[]> {
    const res = await axios.get(`/AAZ/Editor/Workspaces/${workspaceName}/CommandTree/Nodes/aaz/Resources`);
    return res.data;
  }

  /**
   * Add swagger resources to workspace
   */
  static async addSwaggerResources(workspaceName: string, requestBody: any): Promise<void> {
    await axios.post(`/AAZ/Editor/Workspaces/${workspaceName}/CommandTree/Nodes/aaz/AddSwagger`, requestBody);
  }

  /**
   * Add TypeSpec resources to workspace
   */
  static async addTypespecResources(workspaceName: string, requestBody: any): Promise<void> {
    await axios.post(`/AAZ/Editor/Workspaces/${workspaceName}/CommandTree/Nodes/aaz/AddTypespec`, requestBody);
  }
}
