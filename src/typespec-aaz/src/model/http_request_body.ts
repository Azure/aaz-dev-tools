import { CMDRequestJson } from "./content.js";

export interface CMDHttpRequestBody {}

export interface CMDHttpRequestJsonBody extends CMDHttpRequestBody {
  json?: CMDRequestJson;
}
