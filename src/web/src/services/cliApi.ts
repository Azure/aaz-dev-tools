import axios from "axios";

/**
 * Service for CLI-related API operations
 */
export class CliApiService {
  /**
   * Get CLI profiles
   */
  static async getCliProfiles(): Promise<string[]> {
    const res = await axios.get(`/CLI/Az/Profiles`);
    return res.data;
  }

  /**
   * Get CLI module view
   */
  static async getCliModule(repoName: string, moduleName: string): Promise<any> {
    const res = await axios.get(`/CLI/Az/${repoName}/Modules/${moduleName}`);
    return res.data;
  }

  /**
   * Get specs command by path
   */
  static async getSpecsCommand(names: string[]): Promise<any> {
    const res = await axios.get(
      `/AAZ/Specs/CommandTree/Nodes/aaz/${names.slice(0, -1).join("/")}/Leaves/${names[names.length - 1]}`,
    );
    return res.data;
  }

  /**
   * Retrieve multiple commands by names list
   */
  static async retrieveCommands(namesList: string[][]): Promise<any[]> {
    const namesListData = namesList.map((names) => ["aaz", ...names]);
    const res = await axios.post(`/AAZ/Specs/CommandTree/Nodes/Leaves`, namesListData);
    return res.data;
  }

  /**
   * Get simple command tree
   */
  static async getSimpleCommandTree(): Promise<any> {
    const res = await axios.get(`/AAZ/Specs/CommandTree/Simple`);
    return res.data;
  }

  /**
   * Update CLI module (generate all)
   */
  static async updateCliModule(repoName: string, moduleName: string, data: any): Promise<void> {
    await axios.put(`/CLI/Az/${repoName}/Modules/${moduleName}`, data);
  }

  /**
   * Patch CLI module (generate modified only)
   */
  static async patchCliModule(repoName: string, moduleName: string, data: any): Promise<void> {
    await axios.patch(`/CLI/Az/${repoName}/Modules/${moduleName}`, data);
  }
}
