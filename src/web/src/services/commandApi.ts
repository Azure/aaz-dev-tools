import axios from "axios";

export class CommandApiService {
  static async getCommand(leafUrl: string): Promise<any> {
    const res = await axios.get(leafUrl);
    return res.data;
  }

  static async getCommandsForResource(resourceUrl: string): Promise<any[]> {
    const res = await axios.get(`${resourceUrl}/Commands`);
    return res.data;
  }

  static async deleteResource(resourceUrl: string): Promise<void> {
    await axios.delete(resourceUrl);
  }

  static async updateCommand(leafUrl: string, data: any): Promise<any> {
    const res = await axios.patch(leafUrl, data);
    return res.data;
  }

  static async renameCommand(leafUrl: string, newName: string): Promise<any> {
    const res = await axios.post(`${leafUrl}/Rename`, { name: newName });
    return res.data;
  }

  static async updateCommandExamples(leafUrl: string, examples: any[]): Promise<any> {
    const res = await axios.patch(leafUrl, { examples });
    return res.data;
  }

  static async generateSwaggerExamples(leafUrl: string): Promise<any[]> {
    const res = await axios.post(`${leafUrl}/GenerateExamples`, { source: "swagger" });
    return res.data.map((v: any) => ({
      name: v.name,
      commands: v.commands,
    }));
  }

  static async addSubcommands(resourceUrl: string, data: any): Promise<void> {
    await axios.post(resourceUrl, data);
  }

  static async updateCommandOutputs(leafUrl: string, outputs: any[]): Promise<any> {
    const res = await axios.patch(leafUrl, { outputs });
    return res.data;
  }

  static async updateCommandArgument(argumentUrl: string, data: any): Promise<void> {
    await axios.patch(argumentUrl, data);
  }

  static async updateArgumentById(argId: string, data: any): Promise<void> {
    await axios.patch(argId, data);
  }

  static async flattenArgument(flattenUrl: string, data?: any): Promise<void> {
    if (data) {
      await axios.post(flattenUrl, data);
    } else {
      await axios.post(flattenUrl);
    }
  }

  static async unwrapClassArgument(flattenUrl: string): Promise<void> {
    await axios.post(flattenUrl);
  }

  static async deleteCommandGroup(nodeUrl: string): Promise<void> {
    await axios.delete(nodeUrl);
  }

  static async updateCommandGroup(
    nodeUrl: string,
    data: { help: { short: string; lines: string[] }; stage: string },
  ): Promise<any> {
    const res = await axios.patch(nodeUrl, data);
    return res.data;
  }

  static async renameCommandGroup(nodeUrl: string, name: string): Promise<any> {
    const res = await axios.post(`${nodeUrl}/Rename`, { name });
    return res.data;
  }

  static async findSimilarArguments(commandUrl: string, argVar: string): Promise<any> {
    const similarUrl = `${commandUrl}/Arguments/${argVar}/FindSimilar`;
    const res = await axios.post(similarUrl);
    return res.data;
  }

  static async createSubresource(
    subresourceUrl: string,
    data: {
      commandGroupName: string;
      refArgsOptions: { [argVar: string]: string[] };
      arg: string;
    },
  ): Promise<any> {
    try {
      const response = await axios.post(subresourceUrl, data);
      return response.data;
    } catch (err: any) {
      ApiErrorHandler.handleApiError(err, "Failed to create subresource");
    }
  }
}

export class ApiErrorHandler {
  static getErrorMessage(err: any): string {
    if (err.response?.data?.message) {
      const data = err.response.data;
      const details = data.details ? `: ${JSON.stringify(data.details)}` : "";
      return `ResponseError: ${data.message}${details}`;
    }
    return "An unexpected error occurred";
  }

  static isHttpError(err: any, statusCode: number): boolean {
    return err.response?.status === statusCode;
  }

  static handleApiError(err: any, context: string = ""): never {
    console.error(context, err);
    const message = this.getErrorMessage(err);
    throw new Error(message);
  }
}
