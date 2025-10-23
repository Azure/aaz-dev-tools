import type { ResponseCommands } from "./commands";

export interface CommandGroup {
  id: string;
  names: string[];
  stage: "Stable" | "Preview" | "Experimental";
  help?: {
    short: string;
    lines?: string[];
  };
  canDelete: boolean;
}

export interface ResponseCommandGroup {
  names: string[];
  stage?: "Stable" | "Preview" | "Experimental";
  help?: {
    short: string;
    lines?: string[];
  };
  commands?: ResponseCommands;
  commandGroups?: ResponseCommandGroups;
}

export interface ResponseCommandGroups {
  [name: string]: ResponseCommandGroup;
}
