import axios from "axios";

export class CliApiService {
  static async getCliProfiles(): Promise<string[]> {
    const res = await axios.get(`/CLI/Az/Profiles`);
    return res.data;
  }

  static async getCliModules(repoName: string): Promise<any[]> {
    const res = await axios.get(`/CLI/Az/${repoName}/Modules`);
    return res.data;
  }

  static async createCliModule(repoName: string, moduleName: string): Promise<any> {
    const res = await axios.post(`/CLI/Az/${repoName}/Modules`, { name: moduleName });
    return res.data;
  }

  static async getCliModule(repoName: string, moduleName: string): Promise<any> {
    const res = await axios.get(`/CLI/Az/${repoName}/Modules/${moduleName}`);
    return res.data;
  }

  static async getSpecsCommand(names: string[]): Promise<any> {
    const res = await axios.get(
      `/AAZ/Specs/CommandTree/Nodes/aaz/${names.slice(0, -1).join("/")}/Leaves/${names[names.length - 1]}`,
    );
    return res.data;
  }

  static async retrieveCommands(namesList: string[][]): Promise<any[]> {
    const namesListData = namesList.map((names) => ["aaz", ...names]);
    const res = await axios.post(`/AAZ/Specs/CommandTree/Nodes/Leaves`, namesListData);
    return res.data;
  }

  static async getSimpleCommandTree(): Promise<any> {
    const res = await axios.get(`/AAZ/Specs/CommandTree/Simple`);
    return res.data;
  }

  static async updateCliModule(repoName: string, moduleName: string, data: any): Promise<void> {
    await axios.put(`/CLI/Az/${repoName}/Modules/${moduleName}`, data);
  }

  static async patchCliModule(repoName: string, moduleName: string, data: any): Promise<void> {
    await axios.patch(`/CLI/Az/${repoName}/Modules/${moduleName}`, data);
  }
}
