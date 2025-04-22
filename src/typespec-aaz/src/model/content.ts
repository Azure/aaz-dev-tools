import { CMDSchema, CMDSchemaBase } from "./schema.js";
import { CMDVariantField } from "./fields.js";

export type CMDRequestJson = {
  ref?: CMDVariantField;
  schema?: CMDSchema;
};

export type CMDResponseJson = {
  var?: CMDVariantField;
  schema: CMDSchemaBase;
};
