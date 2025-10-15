import type { Output } from "../commandContent/OutputDialog";
import type { CMDArg, ClsArgDefinitionMap } from "../commandArgumentsContent";

export interface Plane {
  name: string;
  displayName: string;
  moduleOptions?: string[];
}

export interface Example {
  name: string;
  commands: string[];
}

export interface Resource {
  id: string;
  version: string;
  subresource?: string;
  swagger: string;
}

export interface Command {
  id: string;
  names: string[];
  help?: {
    short: string;
    lines?: string[];
  };
  stage: "Stable" | "Preview" | "Experimental";
  version: string;
  examples?: Example[];
  outputs?: Output[];
  resources: Resource[];

  confirmation?: string;
  args?: CMDArg[];
  clsArgDefineMap?: ClsArgDefinitionMap;
}

export interface ResponseCommand {
  names: string[];
  help?: {
    short: string;
    lines?: string[];
  };
  stage?: "Stable" | "Preview" | "Experimental";
  version: string;
  examples?: Example[];
  resources: Resource[];
  outputs?: Output[];
  confirmation?: string;
  argGroups?: any[];
}

export interface ResponseCommands {
  [name: string]: ResponseCommand;
}
