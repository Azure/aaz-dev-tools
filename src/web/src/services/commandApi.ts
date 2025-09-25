import axios from "axios";

/**
 * Service for command-related API operations
 */
export class CommandApiService {
  /**
   * Get command details
   */
  static async getCommand(leafUrl: string): Promise<any> {
    const res = await axios.get(leafUrl);
    return res.data;
  }

  /**
   * Get commands for a resource URL
   */
  static async getCommandsForResource(resourceUrl: string): Promise<any[]> {
    const res = await axios.get(`${resourceUrl}/Commands`);
    return res.data;
  }

  /**
   * Delete resource
   */
  static async deleteResource(resourceUrl: string): Promise<void> {
    await axios.delete(resourceUrl);
  }

  /**
   * Update command properties
   */
  static async updateCommand(leafUrl: string, data: any): Promise<any> {
    const res = await axios.patch(leafUrl, data);
    return res.data;
  }

  /**
   * Rename command
   */
  static async renameCommand(leafUrl: string, newName: string): Promise<any> {
    const res = await axios.post(`${leafUrl}/Rename`, { name: newName });
    return res.data;
  }

  /**
   * Update command examples
   */
  static async updateCommandExamples(leafUrl: string, examples: any[]): Promise<any> {
    const res = await axios.patch(leafUrl, { examples });
    return res.data;
  }

  /**
   * Generate examples from swagger
   */
  static async generateSwaggerExamples(leafUrl: string): Promise<any[]> {
    const res = await axios.post(`${leafUrl}/GenerateExamples`, { source: "swagger" });
    return res.data.map((v: any) => ({
      name: v.name,
      commands: v.commands,
    }));
  }

  /**
   * Add subcommands
   */
  static async addSubcommands(resourceUrl: string, data: any): Promise<void> {
    await axios.post(resourceUrl, data);
  }

  /**
   * Update command outputs
   */
  static async updateCommandOutputs(leafUrl: string, outputs: any[]): Promise<any> {
    const res = await axios.patch(leafUrl, { outputs });
    return res.data;
  }

  /**
   * Update command argument
   */
  static async updateCommandArgument(argumentUrl: string, data: any): Promise<void> {
    await axios.patch(argumentUrl, data);
  }

  /**
   * Update argument by ID
   */
  static async updateArgumentById(argId: string, data: any): Promise<void> {
    await axios.patch(argId, data);
  }

  /**
   * Flatten argument structure
   */
  static async flattenArgument(flattenUrl: string, data?: any): Promise<void> {
    if (data) {
      await axios.post(flattenUrl, data);
    } else {
      await axios.post(flattenUrl);
    }
  }

  /**
   * Unwrap class argument
   */
  static async unwrapClassArgument(flattenUrl: string): Promise<void> {
    await axios.post(flattenUrl);
  }

  /**
   * Create a subresource for a command resource
   */
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

/**
 * Error handling utilities for API operations
 */
export class ApiErrorHandler {
  /**
   * Extract error message from axios error response
   */
  static getErrorMessage(err: any): string {
    if (err.response?.data?.message) {
      const data = err.response.data;
      const details = data.details ? `: ${JSON.stringify(data.details)}` : "";
      return `ResponseError: ${data.message}${details}`;
    }
    return "An unexpected error occurred";
  }

  /**
   * Check if error is a specific HTTP status code
   */
  static isHttpError(err: any, statusCode: number): boolean {
    return err.response?.status === statusCode;
  }

  /**
   * Handle common API error scenarios
   */
  static handleApiError(err: any, context: string = ""): never {
    console.error(context, err);
    const message = this.getErrorMessage(err);
    throw new Error(message);
  }
}
