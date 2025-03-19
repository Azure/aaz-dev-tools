import { Type } from "@typespec/compiler";
import { CMDVariantField } from "./fields.js"
import { CMDArrayFormat, CMDFloatFormat, CMDIntegerFormat, CMDObjectFormat, CMDResourceIdFormat, CMDStringFormat } from "./format.js";
import { Visibility } from "@typespec/http";


export interface PendingSchema {
  /** The TYPESPEC type for the schema */
  type: Type;
  /** The visibility to apply when computing the schema */
  visibility: Visibility;

  /**
   * The JSON reference to use to point to this schema.
   *
   * Note that its value will not be computed until all schemas have been
   * computed as we will add a suffix to the name if more than one schema
   * must be emitted for the type for different visibilities.
   */
  ref: Ref;

  schema?: CMDObjectSchemaBase | CMDArraySchemaBase;

  /** The reference count for this schema */
  count: number;
}

export class Ref {
  value?: string;
  toJSON() {
    return this.value;
  }
}

export class ClsType {
  pendingSchema: PendingSchema;
  
  constructor(pendingSchema: PendingSchema) {
    this.pendingSchema = pendingSchema;
  }
  
  toJSON() {
    return "@" + this.pendingSchema.ref.toJSON()!;
  }
}

export class ArrayType {
  itemType: string | ClsType | ArrayType;
  
  constructor(itemType: string | ClsType | ArrayType) {
    this.itemType = itemType;
  }
  
  toJSON() {
    return `array<${JSON.parse(JSON.stringify(this.itemType))}>`;
  }
}

export type CMDSchemaDefault<T> = {
  value: T | null;
}

export type CMDSchemaEnumItem<T> = {
  value: T;
  arg?: CMDVariantField;
}

export type CMDSchemaEnum<T> = {
  items: CMDSchemaEnumItem<T>[];
}

export interface CMDSchemaBase {
  type: string | ClsType | ArrayType;

  readOnly?: boolean;
  frozen?: boolean;   // python set?
  const?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  default?: CMDSchemaDefault<any>;
  nullable?: boolean;
}

export interface CMDSchemaBaseT<T> extends CMDSchemaBase {
  default?: CMDSchemaDefault<T>;
}

export interface CMDSchema extends CMDSchemaBase {
  name: string;
  arg?: CMDVariantField;
  required?: boolean;
  description?: string;
  skipUrlEncoding?: boolean;
  secret?: boolean;
}

export interface CMDSchemaT<T> extends CMDSchema {
  default?: CMDSchemaDefault<T>;
}

export interface CMDClsSchemaBase extends CMDSchemaBase {
  type: ClsType;
}

export interface CMDClsSchema extends CMDClsSchemaBase, CMDSchema {
  type: ClsType;
  clientFlatten?: boolean;
}


export type CMDStringSchemaTypeValues = "string" | "byte" | "binary" | "duration" | "date" | "date-time" | "time" | "uuid" | "password" | "ResourceLocation" | "ResourceId";

export interface CMDStringSchemaBase extends CMDSchemaBaseT<string> {
  type: CMDStringSchemaTypeValues;
  format?: CMDStringFormat;
  enum?: CMDSchemaEnum<string>;
}

export interface CMDStringSchema extends CMDStringSchemaBase, CMDSchemaT<string> {
  type: CMDStringSchemaTypeValues;
}

// type: byte
export interface CMDByteSchemaBase extends CMDStringSchemaBase {
  type: "byte";
}

export interface CMDByteSchema extends CMDByteSchemaBase, CMDStringSchema {
  type: "byte";
}

// type: binary
export interface CMDBinarySchemaBase extends CMDStringSchemaBase {
  type: "binary";
}

export interface CMDBinarySchema extends CMDBinarySchemaBase, CMDStringSchema {
  type: "binary";
}

// type: duration
export interface CMDDurationSchemaBase extends CMDStringSchemaBase {
  type: "duration";
}

export interface CMDDurationSchema extends CMDDurationSchemaBase, CMDStringSchema {
  type: "duration";
}

// type: date  As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
export interface CMDDateSchemaBase extends CMDStringSchemaBase {
  type: "date";
}

export interface CMDDateSchema extends CMDDateSchemaBase, CMDStringSchema {
  type: "date";
}

// type: date-time  As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
export interface CMDDateTimeSchemaBase extends CMDStringSchemaBase {
  type: "date-time";
}

export interface CMDDateTimeSchema extends CMDDateTimeSchemaBase, CMDStringSchema {
  type: "date-time";
}

// type: time
export interface CMDTimeSchemaBase extends CMDStringSchemaBase {
  type: "time";
}

export interface CMDTimeSchema extends CMDTimeSchemaBase, CMDStringSchema {
  type: "time";
}

// type: uuid 
export interface CMDUuidSchemaBase extends CMDStringSchemaBase {
  type: "uuid";
}

export interface CMDUuidSchema extends CMDUuidSchemaBase, CMDStringSchema {
  type: "uuid";
}

// type: password
export interface CMDPasswordSchemaBase extends CMDStringSchemaBase {
  type: "password";
}

export interface CMDPasswordSchema extends CMDPasswordSchemaBase, CMDStringSchema {
  type: "password";
}

// type: ResourceLocation
export interface CMDResourceLocationSchemaBase extends CMDStringSchemaBase {
  type: "ResourceLocation";
}

export interface CMDResourceLocationSchema extends CMDResourceLocationSchemaBase, CMDStringSchema {
  type: "ResourceLocation";
}

// type: ResourceId
export interface CMDResourceIdSchemaBase extends CMDSchemaBaseT<string> {
  type: "ResourceId";
  format?: CMDResourceIdFormat;
  enum?: CMDSchemaEnum<string>;
}

export interface CMDResourceIdSchema extends CMDResourceIdSchemaBase, CMDSchemaT<string> {
  type: "ResourceId";
}

type CMDIntegerSchemaTypeValues = "integer" | "integer32" | "integer64";

// type: integer
export interface CMDIntegerSchemaBase extends CMDSchemaBaseT<number> {
  type: CMDIntegerSchemaTypeValues;
  format?: CMDIntegerFormat;
  enum?: CMDSchemaEnum<number>;
}

export interface CMDIntegerSchema extends CMDIntegerSchemaBase, CMDSchemaT<number> {
  type: CMDIntegerSchemaTypeValues;
}

// type: integer32
export interface CMDInteger32SchemaBase extends CMDIntegerSchemaBase {
  type: "integer32";
}

export interface CMDInteger32Schema extends CMDInteger32SchemaBase, CMDIntegerSchema {
  type: "integer32";
}

// type: integer64
export interface CMDInteger64SchemaBase extends CMDIntegerSchemaBase {
  type: "integer64";
}

export interface CMDInteger64Schema extends CMDInteger64SchemaBase, CMDIntegerSchema {
  type: "integer64";
}

// type: boolean
export interface CMDBooleanSchemaBase extends CMDSchemaBaseT<boolean> {
  type: "boolean";
}

export interface CMDBooleanSchema extends CMDBooleanSchemaBase, CMDSchemaT<boolean> {
  type: "boolean";
}


type CMDFloatSchemaTypeValues = "float" | "float32" | "float64";


// type: float
export interface CMDFloatSchemaBase extends CMDSchemaBaseT<number> {
  type: CMDFloatSchemaTypeValues;
  format?: CMDFloatFormat;
  enum?: CMDSchemaEnum<number>;
}

export interface CMDFloatSchema extends CMDFloatSchemaBase, CMDSchemaT<number> {
  type: CMDFloatSchemaTypeValues;
}

// type: float32
export interface CMDFloat32SchemaBase extends CMDFloatSchemaBase {
  type: "float32";
}

export interface CMDFloat32Schema extends CMDFloat32SchemaBase, CMDFloatSchema {
  type: "float32";
}

// type: float64
export interface CMDFloat64SchemaBase extends CMDFloatSchemaBase {
  type: "float64";
}

export interface CMDFloat64Schema extends CMDFloat64SchemaBase, CMDFloatSchema {
  type: "float64";
}

// type: any
export interface CMDAnyTypeSchemaBase extends CMDSchemaBase {
  type: "any"
}

export interface CMDAnyTypeSchema extends CMDAnyTypeSchemaBase, CMDSchema {
  type: "any"
}

// object

// discriminator

export type CMDObjectSchemaDiscriminator = {
  property: string,
  value: string,
  frozen?: boolean,

  props?: CMDSchema[],
  discriminators?: CMDObjectSchemaDiscriminator[],
};

// additionalProperties

export type CMDObjectSchemaAdditionalProperties = {
  readOnly?: boolean,
  frozen?: boolean,

  item?: CMDSchemaBase,
  anyType?: boolean,
}

type CMDObjectSchemaTypeValues = "object" | "IdentityObject";

export interface CMDObjectSchemaBase extends CMDSchemaBase {
  type: CMDObjectSchemaTypeValues;
  format?: CMDObjectFormat;
  props?: CMDSchema[];
  discriminators?: CMDObjectSchemaDiscriminator[];
  additionalProps?: CMDObjectSchemaAdditionalProperties;
  cls?: Ref;
}

export interface CMDObjectSchema extends CMDObjectSchemaBase, CMDSchema {
  type: CMDObjectSchemaTypeValues;
  clientFlatten?: boolean;
}


// type: IdentityObject
export interface CMDIdentityObjectSchemaBase extends CMDObjectSchemaBase {
  type: "IdentityObject";
}

export interface CMDIdentityObjectSchema extends CMDIdentityObjectSchemaBase, CMDObjectSchema {
  type: "IdentityObject";
}

// type: array
export interface CMDArraySchemaBase extends CMDSchemaBase {
  type: ArrayType;
  format?: CMDArrayFormat;
  item?: CMDSchemaBase;

  identifiers?: string[];

  cls?: Ref;
}

export interface CMDArraySchema extends CMDArraySchemaBase, CMDSchema {
  type: ArrayType;
}
