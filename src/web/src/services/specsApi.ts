import axios from "axios";

export interface Plane {
  name: string;
  displayName: string;
  moduleOptions?: string[];
}

export interface Resource {
  id: string;
  version: string;
}

export const specsApi = {
  getPlanes: async (): Promise<Plane[]> => {
    const res = await axios.get(`/AAZ/Specs/Planes`);
    return res.data.map((v: any) => ({
      name: v.name,
      displayName: v.displayName,
      moduleOptions: undefined,
    }));
  },

  getPlaneNames: async (): Promise<string[]> => {
    const res = await axios.get(`/AAZ/Specs/Planes`);
    return res.data.map((v: any) => v.name);
  },

  getModulesForPlane: {
    // @TODO: revisit msg:
    loadingMessage: "Loading modules for plane... (this may take up to 40+ seconds)",
    fn: async (planeName: string): Promise<string[]> => {
      const res = await axios.get(`/Swagger/Specs/${planeName}`);
      return res.data.map((v: any) => v.url);
    },
  },

  getResourceProviders: async (moduleUrl: string): Promise<string[]> => {
    const res = await axios.get(`${moduleUrl}/ResourceProviders`);
    return res.data.map((v: any) => v.url);
  },

  getResources: async (resourceProviderUrl: string): Promise<Resource[]> => {
    const res = await axios.get(`${resourceProviderUrl}/Resources`);
    return res.data;
  },

  getSwaggerModules: async (plane: string): Promise<string[]> => {
    const res = await axios.get(`/Swagger/Specs/${plane}`);
    return res.data.map((v: any) => v.url);
  },

  getResourceProvidersWithType: async (moduleUrl: string, type?: string): Promise<string[]> => {
    let url = `${moduleUrl}/ResourceProviders`;
    if (type) {
      url += `?type=${type}`;
    }
    const res = await axios.get(url);
    return res.data.map((v: any) => v.url);
  },

  getProviderResources: async (resourceProviderUrl: string): Promise<any> => {
    const res = await axios.get(`${resourceProviderUrl}/Resources`);
    return res.data;
  },

  filterResourcesByPlane: async (plane: string, resourceIds: string[]): Promise<any> => {
    const filterBody = { resources: resourceIds };
    const res = await axios.post(`/AAZ/Specs/Resources/${plane}/Filter`, filterBody);
    return res.data;
  },
} as const;

export const specsHelper = {
  removeCommonPrefix: (options: string[], prefix: string): string[] => {
    return options.map((option) => option.replace(prefix, ""));
  },

  isClientConfigurablePlane: async (planeName: string): Promise<boolean> => {
    const planeNames = await specsApi.getPlaneNames();
    return !planeNames.includes(planeName);
  },

  buildResourceProviderUrl: (plane: string, modNames: string[], rpName: string, source: string): string => {
    const basePath = `/Swagger/Specs/${plane}/${modNames.join("/")}`;
    const resourceProviderPath = `/ResourceProviders/${rpName}`;
    const suffix = source.toLowerCase() === "typespec" ? "/TypeSpec" : "";
    return `${basePath}${resourceProviderPath}${suffix}`;
  },
} as const;
