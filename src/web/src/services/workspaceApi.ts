import axios from "axios";

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

export class WorkspaceApiService {
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

  static async getWorkspace(workspaceUrl: string): Promise<any> {
    const res = await axios.get(workspaceUrl);
    return res.data;
  }

  static async deleteWorkspace(workspaceName: string): Promise<void> {
    const nodeUrl = `/AAZ/Editor/Workspaces/${workspaceName}`;
    await axios.delete(nodeUrl);
  }

  static async renameWorkspace(workspaceUrl: string, newName: string): Promise<{ name: string }> {
    const res = await axios.post(`${workspaceUrl}/Rename`, { name: newName });
    return res.data;
  }

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
      if (err.response?.status === 404) {
        return null;
      }
      throw err;
    }
  }

  static async updateClientConfig(workspaceUrl: string, config: any): Promise<void> {
    await axios.post(`${workspaceUrl}/ClientConfig`, config);
  }

  static async verifyClientConfig(workspaceUrl: string): Promise<void> {
    const url = `${workspaceUrl}/ClientConfig/AAZ/Compare`;
    await axios.post(url);
  }

  static async inheritClientConfig(workspaceUrl: string): Promise<void> {
    const url = `${workspaceUrl}/ClientConfig/AAZ/Inherit`;
    await axios.post(url);
  }

  static async generateWorkspace(workspaceUrl: string): Promise<void> {
    const url = `${workspaceUrl}/Generate`;
    await axios.post(url);
  }

  static async getWorkspaceResources(workspaceUrl: string): Promise<any[]> {
    const res = await axios.get(`${workspaceUrl}/CommandTree/Nodes/aaz/Resources`);
    return res.data;
  }

  static async getWorkspaceSwaggerDefault(workspaceName: string): Promise<any> {
    const res = await axios.get(`/AAZ/Editor/Workspaces/${workspaceName}/SwaggerDefault`);
    return res.data;
  }

  static async reloadSwaggerResources(workspaceUrl: string, data: any): Promise<void> {
    const reloadUrl = `${workspaceUrl}/Resources/ReloadSwagger`;
    await axios.post(reloadUrl, data);
  }

  static async reloadTypespecResources(workspaceUrl: string, data: any): Promise<void> {
    const reloadUrl = `${workspaceUrl}/Resources/ReloadTypespec`;
    await axios.post(reloadUrl, data);
  }

  static async getSwaggerDefault(workspaceName: string): Promise<any> {
    const res = await axios.get(`/AAZ/Editor/Workspaces/${workspaceName}/SwaggerDefault`);
    return res.data;
  }

  static async getWorkspaceResourcesByName(workspaceName: string): Promise<any[]> {
    const res = await axios.get(`/AAZ/Editor/Workspaces/${workspaceName}/CommandTree/Nodes/aaz/Resources`);
    return res.data;
  }

  static async addSwaggerResources(workspaceName: string, requestBody: any): Promise<void> {
    await axios.post(`/AAZ/Editor/Workspaces/${workspaceName}/CommandTree/Nodes/aaz/AddSwagger`, requestBody);
  }

  static async addTypespecResources(workspaceName: string, requestBody: any): Promise<void> {
    await axios.post(`/AAZ/Editor/Workspaces/${workspaceName}/CommandTree/Nodes/aaz/AddTypespec`, requestBody);
  }

  static async getClientConfig(workspaceUrl: string): Promise<any> {
    const res = await axios.get(`${workspaceUrl}/ClientConfig`);
    return res.data;
  }
}
