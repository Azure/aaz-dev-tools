import axios from "axios";

// Types for specs/planes/modules operations
export interface Plane {
  name: string;
  displayName: string;
  moduleOptions?: string[];
}

export interface Resource {
  id: string;
  version: string;
}

/**
 * Service for API specifications, planes, modules, and resource providers
 */
export class SpecsApiService {
  /**
   * Get all available planes
   */
  static async getPlanes(): Promise<Plane[]> {
    const res = await axios.get(`/AAZ/Specs/Planes`);
    return res.data.map((v: any) => ({
      name: v.name,
      displayName: v.displayName,
      moduleOptions: undefined,
    }));
  }

  /**
   * Get plane names only (used for client configurable plane detection)
   */
  static async getPlaneNames(): Promise<string[]> {
    const res = await axios.get(`/AAZ/Specs/Planes`);
    return res.data.map((v: any) => v.name);
  }

  /**
   * Get modules for a specific plane
   */
  static async getModulesForPlane(planeName: string): Promise<string[]> {
    const res = await axios.get(`/Swagger/Specs/${planeName}`);
    return res.data.map((v: any) => v.url);
  }

  /**
   * Get resource providers for a specific module
   */
  static async getResourceProviders(moduleUrl: string): Promise<string[]> {
    const res = await axios.get(`${moduleUrl}/ResourceProviders`);
    return res.data.map((v: any) => v.url);
  }

  /**
   * Get resources for a specific resource provider
   */
  static async getResources(resourceProviderUrl: string): Promise<Resource[]> {
    const res = await axios.get(`${resourceProviderUrl}/Resources`);
    return res.data;
  }

  /**
   * Get swagger modules for a plane
   */
  static async getSwaggerModules(plane: string): Promise<string[]> {
    const res = await axios.get(`/Swagger/Specs/${plane}`);
    return res.data.map((v: any) => v.url);
  }

  /**
   * Get resource providers for a module (with optional type filter)
   */
  static async getResourceProvidersWithType(moduleUrl: string, type?: string): Promise<string[]> {
    let url = `${moduleUrl}/ResourceProviders`;
    if (type) {
      url += `?type=${type}`;
    }
    const res = await axios.get(url);
    return res.data.map((v: any) => v.url);
  }

  /**
   * Get resources for a resource provider (returns raw data)
   */
  static async getProviderResources(resourceProviderUrl: string): Promise<any> {
    const res = await axios.get(`${resourceProviderUrl}/Resources`);
    return res.data;
  }

  /**
   * Filter resources by plane
   */
  static async filterResourcesByPlane(plane: string, resourceIds: string[]): Promise<any> {
    const filterBody = { resources: resourceIds };
    const res = await axios.post(`/AAZ/Specs/Resources/${plane}/Filter`, filterBody);
    return res.data;
  }
}

/**
 * Helper functions for working with specs
 */
export class SpecsHelper {
  /**
   * Remove common prefix from option strings
   */
  static removeCommonPrefix(options: string[], prefix: string): string[] {
    return options.map((option) => option.replace(prefix, ""));
  }

  /**
   * Check if a plane is client configurable (not in built-in planes)
   */
  static async isClientConfigurablePlane(planeName: string): Promise<boolean> {
    const planeNames = await SpecsApiService.getPlaneNames();
    return !planeNames.includes(planeName);
  }

  /**
   * Build full resource provider URL
   */
  static buildResourceProviderUrl(plane: string, modNames: string[], rpName: string, source: string): string {
    const basePath = `/Swagger/Specs/${plane}/${modNames.join("/")}`;
    const resourceProviderPath = `/ResourceProviders/${rpName}`;
    const suffix = source.toLowerCase() === "typespec" ? "/TypeSpec" : "";
    return `${basePath}${resourceProviderPath}${suffix}`;
  }
}
