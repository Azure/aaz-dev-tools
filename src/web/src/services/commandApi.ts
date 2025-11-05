import axios from "axios";

export const commandApi = {
  getCommand: async (leafUrl: string): Promise<any> => {
    const res = await axios.get(leafUrl);
    return res.data;
  },

  getCommandsForResource: async (resourceUrl: string): Promise<any[]> => {
    const res = await axios.get(`${resourceUrl}/Commands`);
    return res.data;
  },

  deleteResource: {
    loadingMessage: "Deleting commands...",
    fn: async (resourceUrl: string): Promise<void> => {
      await axios.delete(resourceUrl);
    },
  },

  updateCommand: {
    loadingMessage: "Updating command...",
    fn: async (leafUrl: string, data: any): Promise<any> => {
      const res = await axios.patch(leafUrl, data);
      return res.data;
    },
  },

  renameCommand: {
    loadingMessage: "Renaming command...",
    fn: async (leafUrl: string, newName: string): Promise<any> => {
      const res = await axios.post(`${leafUrl}/Rename`, { name: newName });
      return res.data;
    },
  },

  updateCommandExamples: {
    loadingMessage: "Updating command examples...",
    fn: async (leafUrl: string, examples: any[]): Promise<any> => {
      const res = await axios.patch(leafUrl, { examples });
      return res.data;
    },
  },

  generateSwaggerExamples: {
    loadingMessage: "Generating examples from OpenAPI...",
    fn: async (leafUrl: string): Promise<any[]> => {
      const res = await axios.post(`${leafUrl}/GenerateExamples`, { source: "swagger" });
      return res.data.map((v: any) => ({
        name: v.name,
        commands: v.commands,
      }));
    },
  },

  addSubcommands: async (resourceUrl: string, data: any): Promise<void> => {
    await axios.post(resourceUrl, data);
  },

  updateCommandOutputs: {
    loadingMessage: "Updating command outputs...",
    fn: async (leafUrl: string, outputs: any[]): Promise<any> => {
      const res = await axios.patch(leafUrl, { outputs });
      return res.data;
    },
  },

  updateCommandArgument: {
    loadingMessage: "Updating command argument...",
    fn: async (argumentUrl: string, data: any): Promise<void> => {
      await axios.patch(argumentUrl, data);
    },
  },

  updateArgumentById: {
    loadingMessage: "Updating argument...",
    fn: async (argId: string, data: any): Promise<void> => {
      await axios.patch(argId, data);
    },
  },

  flattenArgument: async (flattenUrl: string, data?: any): Promise<void> => {
    if (data) {
      await axios.post(flattenUrl, data);
    } else {
      await axios.post(flattenUrl);
    }
  },

  unwrapClassArgument: async (flattenUrl: string): Promise<void> => {
    await axios.post(flattenUrl);
  },

  deleteCommandGroup: {
    loadingMessage: "Deleting command group...",
    fn: async (nodeUrl: string): Promise<void> => {
      await axios.delete(nodeUrl);
    },
  },

  updateCommandGroup: {
    loadingMessage: "Updating command group...",
    fn: async (nodeUrl: string, data: { help: { short: string; lines: string[] }; stage: string }): Promise<any> => {
      const res = await axios.patch(nodeUrl, data);
      return res.data;
    },
  },

  renameCommandGroup: {
    loadingMessage: "Renaming command group...",
    fn: async (nodeUrl: string, name: string): Promise<any> => {
      const res = await axios.post(`${nodeUrl}/Rename`, { name });
      return res.data;
    },
  },

  findSimilarArguments: async (commandUrl: string, argVar: string): Promise<any> => {
    const similarUrl = `${commandUrl}/Arguments/${argVar}/FindSimilar`;
    const res = await axios.post(similarUrl);
    return res.data;
  },

  findSimilarArgumentsOperation: {
    loadingMessage: "Finding similar arguments...",
    fn: async (commandUrl: string, argVar: string): Promise<any> => {
      const similarUrl = `${commandUrl}/Arguments/${argVar}/FindSimilar`;
      const res = await axios.post(similarUrl);
      return res.data;
    },
  },

  createSubresource: {
    loadingMessage: "Creating subcommands...",
    fn: async (
      subresourceUrl: string,
      data: {
        commandGroupName: string;
        refArgsOptions: { [argVar: string]: string[] };
        arg: string;
      },
    ): Promise<any> => {
      const response = await axios.post(subresourceUrl, data);
      return response.data;
    },
  },
} as const;
