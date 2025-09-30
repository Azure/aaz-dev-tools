import axios from "axios";

export const cliApi = {
  getCliProfiles: async (): Promise<string[]> => {
    const res = await axios.get(`/CLI/Az/Profiles`);
    return res.data;
  },

  getCliModules: async (repoName: string): Promise<any[]> => {
    const res = await axios.get(`/CLI/Az/${repoName}/Modules`);
    return res.data;
  },

  createCliModule: async (repoName: string, moduleName: string): Promise<any> => {
    const res = await axios.post(`/CLI/Az/${repoName}/Modules`, { name: moduleName });
    return res.data;
  },

  getCliModule: async (repoName: string, moduleName: string): Promise<any> => {
    const res = await axios.get(`/CLI/Az/${repoName}/Modules/${moduleName}`);
    return res.data;
  },

  getSpecsCommand: async (names: string[]): Promise<any> => {
    const res = await axios.get(
      `/AAZ/Specs/CommandTree/Nodes/aaz/${names.slice(0, -1).join("/")}/Leaves/${names[names.length - 1]}`,
    );
    return res.data;
  },

  retrieveCommands: async (namesList: string[][]): Promise<any[]> => {
    const namesListData = namesList.map((names) => ["aaz", ...names]);
    const res = await axios.post(`/AAZ/Specs/CommandTree/Nodes/Leaves`, namesListData);
    return res.data;
  },

  getSimpleCommandTree: async (): Promise<any> => {
    const res = await axios.get(`/AAZ/Specs/CommandTree/Simple`);
    return res.data;
  },

  updateCliModule: async (repoName: string, moduleName: string, data: any): Promise<void> => {
    await axios.put(`/CLI/Az/${repoName}/Modules/${moduleName}`, data);
  },

  patchCliModule: async (repoName: string, moduleName: string, data: any): Promise<void> => {
    await axios.patch(`/CLI/Az/${repoName}/Modules/${moduleName}`, data);
  },
} as const;
