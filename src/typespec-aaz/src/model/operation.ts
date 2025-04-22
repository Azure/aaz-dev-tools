import { FinalStateValue } from "@azure-tools/typespec-azure-core";
import { CMDVariantField } from "./fields.js";
import { CMDHttpAction } from "./http.js";
import { XmsPageable } from "./x_ms_pageable.js";

export type TypeSpecOperation = {
  operationId?: string;
  pageable?: XmsPageable;
  read?: CMDHttpOperation;
  create?: CMDHttpOperation;
  update?: CMDHttpOperation;
};

export interface CMDHttpOperation {
  when?: CMDVariantField[];

  longRunning?: CMDHttpOperationLongRunning;
  // required
  operationId: string;
  description?: string;
  // required
  http: CMDHttpAction;
}

export type CMDHttpOperationLongRunning = {
  // "azure-async-operation" | "location" | "original-uri"
  finalStateVia?: FinalStateValue;
};
