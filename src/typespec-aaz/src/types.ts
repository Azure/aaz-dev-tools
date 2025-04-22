import { Program } from "@typespec/compiler";
import { TypeSpecPathItem } from "./model/path_item.js";

export interface AAZListResourcesContext {
  program: Program;
}

export interface AAZRetrieveOperationContext {
  program: Program;
}

export type HttpMethod = "get" | "put" | "post" | "delete" | "head" | "patch" | "options";

export interface AAZResourceSchema {
  /** The available paths and operations for typespec resource */
  pathItem?: TypeSpecPathItem;
  id: string;
  path: string;
  version?: string;
}
