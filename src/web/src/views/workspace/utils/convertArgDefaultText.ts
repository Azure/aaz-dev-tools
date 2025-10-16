export type SupportedArgType =
  | "byte"
  | "binary"
  | "duration"
  | "date"
  | "dateTime"
  | "time"
  | "uuid"
  | "password"
  | "SubscriptionId"
  | "ResourceGroupName"
  | "ResourceId"
  | "ResourceLocation"
  | "string"
  | "integer32"
  | "integer64"
  | "integer"
  | "float32"
  | "float64"
  | "float"
  | "boolean"
  | "any"
  | "object"
  | `array<${string}>`
  | `dict<${string}>`;

export type ConvertedValue = string | number | boolean | null | object | any[];

export interface ConvertArgDefaultTextParams {
  defaultText: string;
  argType: SupportedArgType | string;
}

export function convertArgDefaultText(defaultText: string, argType: string): ConvertedValue {
  switch (argType) {
    case "byte":
    case "binary":
    case "duration":
    case "date":
    case "dateTime":
    case "time":
    case "uuid":
    case "password":
    case "SubscriptionId":
    case "ResourceGroupName":
    case "ResourceId":
    case "ResourceLocation":
    case "string":
      if (defaultText.trim().length === 0) {
        throw Error(`Not supported empty value: '${defaultText}'`);
      }
      return defaultText.trim();
    case "integer32":
    case "integer64":
    case "integer":
      if (Number.isNaN(parseInt(defaultText.trim())) || defaultText.trim().includes(".")) {
        throw Error(`Not supported default value for integer type: '${defaultText}'`);
      }
      return parseInt(defaultText.trim());
    case "float32":
    case "float64":
    case "float":
      if (Number.isNaN(parseFloat(defaultText.trim()))) {
        throw Error(`Not supported default value for float type: '${defaultText}'`);
      }
      return parseFloat(defaultText.trim());
    case "boolean":
      switch (defaultText.trim().toLowerCase()) {
        case "true":
        case "yes":
          return true;
        case "false":
        case "no":
          return false;
        default:
          throw Error(`Not supported default value for boolean type: '${defaultText}'`);
      }
    case "any":
      let trimmed = defaultText.trim().toLowerCase();
      if (!trimmed.includes(".") && Number.isInteger(parseInt(trimmed))) {
        return parseInt(trimmed);
      }
      if (!Number.isNaN(parseFloat(trimmed))) {
        return parseFloat(trimmed);
      }
      switch (trimmed) {
        case "null":
          return null;
        case "true":
        case "yes":
          return true;
        case "false":
        case "no":
          return false;
        default:
          return defaultText.trim();
      }
    case "object": {
      const de = JSON.parse(defaultText.trim());
      return de;
    }
    default:
      if (argType.startsWith("array")) {
        const de = JSON.parse(defaultText.trim());
        return de;
      } else if (argType.startsWith("dict")) {
        const de = JSON.parse(defaultText.trim());
        return de;
      }
      throw Error(`Not supported type: ${argType}`);
  }
}
