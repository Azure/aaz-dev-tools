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

  deleteResource: async (resourceUrl: string): Promise<void> => {
    await axios.delete(resourceUrl);
  },

  updateCommand: async (leafUrl: string, data: any): Promise<any> => {
    const res = await axios.patch(leafUrl, data);
    return res.data;
  },

  renameCommand: async (leafUrl: string, newName: string): Promise<any> => {
    const res = await axios.post(`${leafUrl}/Rename`, { name: newName });
    return res.data;
  },

  updateCommandExamples: async (leafUrl: string, examples: any[]): Promise<any> => {
    const res = await axios.patch(leafUrl, { examples });
    return res.data;
  },

  generateSwaggerExamples: async (leafUrl: string): Promise<any[]> => {
    const res = await axios.post(`${leafUrl}/GenerateExamples`, { source: "swagger" });
    return res.data.map((v: any) => ({
      name: v.name,
      commands: v.commands,
    }));
  },

  addSubcommands: async (resourceUrl: string, data: any): Promise<void> => {
    await axios.post(resourceUrl, data);
  },

  updateCommandOutputs: async (leafUrl: string, outputs: any[]): Promise<any> => {
    const res = await axios.patch(leafUrl, { outputs });
    return res.data;
  },

  updateCommandArgument: async (argumentUrl: string, data: any): Promise<void> => {
    await axios.patch(argumentUrl, data);
  },

  updateArgumentById: async (argId: string, data: any): Promise<void> => {
    await axios.patch(argId, data);
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

  deleteCommandGroup: async (nodeUrl: string): Promise<void> => {
    await axios.delete(nodeUrl);
  },

  updateCommandGroup: async (
    nodeUrl: string,
    data: { help: { short: string; lines: string[] }; stage: string },
  ): Promise<any> => {
    const res = await axios.patch(nodeUrl, data);
    return res.data;
  },

  renameCommandGroup: async (nodeUrl: string, name: string): Promise<any> => {
    const res = await axios.post(`${nodeUrl}/Rename`, { name });
    return res.data;
  },

  findSimilarArguments: async (commandUrl: string, argVar: string): Promise<any> => {
    const similarUrl = `${commandUrl}/Arguments/${argVar}/FindSimilar`;
    const res = await axios.post(similarUrl);
    return res.data;
  },

  createSubresource: async (
    subresourceUrl: string,
    data: {
      commandGroupName: string;
      refArgsOptions: { [argVar: string]: string[] };
      arg: string;
    },
  ): Promise<any> => {
    try {
      const response = await axios.post(subresourceUrl, data);
      return response.data;
    } catch (err: any) {
      apiErrorHandler.handleApiError(err, "Failed to create subresource");
    }
  },
} as const;

export const apiErrorHandler = {
  getErrorMessage: (err: any): string => {
    if (err.response?.data?.message) {
      const data = err.response.data;
      const details = data.details ? `: ${JSON.stringify(data.details)}` : "";
      return `ResponseError: ${data.message}${details}`;
    }
    return "An unexpected error occurred";
  },

  isHttpError: (err: any, statusCode: number): boolean => {
    return err.response?.status === statusCode;
  },

  handleApiError: (err: any, context: string = ""): never => {
    console.error(context, err);
    const message = apiErrorHandler.getErrorMessage(err);
    throw new Error(message);
  },
} as const;
