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

export class SpecsApiService {
  static async getPlanes(): Promise<Plane[]> {
    const res = await axios.get(`/AAZ/Specs/Planes`);
    return res.data.map((v: any) => ({
      name: v.name,
      displayName: v.displayName,
      moduleOptions: undefined,
    }));
  }

  static async getPlaneNames(): Promise<string[]> {
    const res = await axios.get(`/AAZ/Specs/Planes`);
    return res.data.map((v: any) => v.name);
  }

  static async getModulesForPlane(planeName: string): Promise<string[]> {
    const res = await axios.get(`/Swagger/Specs/${planeName}`);
    return res.data.map((v: any) => v.url);
  }

  static async getResourceProviders(moduleUrl: string): Promise<string[]> {
    const res = await axios.get(`${moduleUrl}/ResourceProviders`);
    return res.data.map((v: any) => v.url);
  }

  static async getResources(resourceProviderUrl: string): Promise<Resource[]> {
    const res = await axios.get(`${resourceProviderUrl}/Resources`);
    return res.data;
  }

  static async getSwaggerModules(plane: string): Promise<string[]> {
    const res = await axios.get(`/Swagger/Specs/${plane}`);
    return res.data.map((v: any) => v.url);
  }

  static async getResourceProvidersWithType(moduleUrl: string, type?: string): Promise<string[]> {
    let url = `${moduleUrl}/ResourceProviders`;
    if (type) {
      url += `?type=${type}`;
    }
    const res = await axios.get(url);
    return res.data.map((v: any) => v.url);
  }

  static async getProviderResources(resourceProviderUrl: string): Promise<any> {
    const res = await axios.get(`${resourceProviderUrl}/Resources`);
    return res.data;
  }

  static async filterResourcesByPlane(plane: string, resourceIds: string[]): Promise<any> {
    const filterBody = { resources: resourceIds };
    const res = await axios.post(`/AAZ/Specs/Resources/${plane}/Filter`, filterBody);
    return res.data;
  }
}

export class SpecsHelper {
  static removeCommonPrefix(options: string[], prefix: string): string[] {
    return options.map((option) => option.replace(prefix, ""));
  }

  static async isClientConfigurablePlane(planeName: string): Promise<boolean> {
    const planeNames = await SpecsApiService.getPlaneNames();
    return !planeNames.includes(planeName);
  }

  static buildResourceProviderUrl(plane: string, modNames: string[], rpName: string, source: string): string {
    const basePath = `/Swagger/Specs/${plane}/${modNames.join("/")}`;
    const resourceProviderPath = `/ResourceProviders/${rpName}`;
    const suffix = source.toLowerCase() === "typespec" ? "/TypeSpec" : "";
    return `${basePath}${resourceProviderPath}${suffix}`;
  }
}
