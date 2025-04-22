import { CMDResponseJson } from "./content.js";

export interface CMDHttpResponseBody {}
export interface CMDHttpResponseJsonBody extends CMDHttpResponseBody {
  json?: CMDResponseJson;
}
