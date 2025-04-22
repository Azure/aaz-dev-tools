export interface CMDFormat {}

export interface CMDStringFormat extends CMDFormat {
  pattern?: string;
  maxLength?: number;
  minLength?: number;
}

export interface CMDResourceIdFormat extends CMDFormat {
  template: string;
}

export interface CMDIntegerFormat extends CMDFormat {
  maximum?: number;
  minimum?: number;
  multipleOf?: number;
}

export interface CMDFloatFormat extends CMDFormat {
  maximum?: number;
  minimum?: number;
  exclusiveMaximum?: boolean;
  exclusiveMinimum?: boolean;
  multipleOf?: number;
}

export interface CMDObjectFormat extends CMDFormat {
  maxProperties?: number;
  minProperties?: number;
}

export interface CMDArrayFormat extends CMDFormat {
  maxLength?: number;
  minLength?: number;
  unique?: boolean;
  strFormat?: "csv" | "ssv" | "tsv" | "pipes" | "multi" | "simple" | "form";
}
