import { CMDSchema } from "./schema.js";
import { CMDHttpRequestBody } from "./http_request_body.js";
import { CMDHttpResponseBody } from "./http_response_body.js";
import { CMDVariantField } from "./fields.js";
import { HttpMethod } from "../types.js";

export type CMDHttpAction = {
  path: string;
  request?: CMDHttpRequest;
  responses?: CMDHttpResponse[];
};

export type CMDHttpRequest = {
  method: HttpMethod;
  path?: CMDHttpRequestPath;
  query?: CMDHttpRequestQuery;
  header?: CMDHttpRequestHeader;
  body?: CMDHttpRequestBody;
};

export type CMDHttpResponse = {
  statusCode?: number[];
  isError?: boolean;
  description?: string;
  header?: CMDHttpResponseHeader;
  body?: CMDHttpResponseBody;
};

type CMDHttpRequestArgs = {
  params?: CMDSchema[];
  consts?: CMDSchema[];
};

export type CMDHttpRequestPath = CMDHttpRequestArgs;

export type CMDHttpRequestQuery = CMDHttpRequestArgs;

export type CMDHttpRequestHeader = CMDHttpRequestArgs & {
  clientRequestId?: string;
};

export type CMDHttpResponseHeader = {
  items: CMDHttpResponseHeaderItem[];
};

export type CMDHttpResponseHeaderItem = {
  name: string;
  var?: CMDVariantField;
};
