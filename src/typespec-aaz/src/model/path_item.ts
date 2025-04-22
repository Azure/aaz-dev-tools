import { HttpMethod } from "../types.js";
import { TypeSpecOperation } from "./operation.js";

export type TypeSpecPathItem = {
  [method in HttpMethod]?: TypeSpecOperation;
} & { traces?: string[] };
