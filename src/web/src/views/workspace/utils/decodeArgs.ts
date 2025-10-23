type CMDArgHelp = {
  short: string;
  lines?: string[];
  refCommands?: string[];
};

type CMDArgDefault<T> = {
  value: T | null;
};

type CMDArgBlank<T> = {
  value: T | null;
};

type CMDArgEnumItem<T> = {
  name: string;
  hide: boolean;
  value: T;
};

type CMDArgEnum<T> = {
  items: CMDArgEnumItem<T>[];
};

interface CMDArgPromptInput {
  msg: string;
}

interface CMDPasswordArgPromptInput extends CMDArgPromptInput {
  confirm: boolean;
}

interface CMDArgBase {
  type: string;
  nullable: boolean;
  blank?: CMDArgBlank<any>;
}

interface CMDArg extends CMDArgBase {
  var: string;
  options: string[];

  required: boolean;
  stage: "Stable" | "Preview" | "Experimental";
  hide: boolean;
  group: string;
  help?: CMDArgHelp;

  default?: CMDArgDefault<any>;
  idPart?: string;
  prompt?: CMDArgPromptInput;
  configurationKey?: string;
  supportEnumExtension?: boolean;
  hasEnum?: boolean;
}

interface CMDClsArgBase extends CMDArgBase {
  clsName: string;
}

interface CMDClsArg extends CMDClsArgBase, CMDArg {
  singularOptions?: string[];
}

interface CMDObjectArgBase extends CMDArgBase {
  args: CMDArg[];
}

interface CMDObjectArg extends CMDObjectArgBase, CMDArg {}

interface CMDDictArgBase extends CMDArgBase {
  item?: CMDArgBase;
  anyType: boolean;
}
interface CMDArrayArgBase extends CMDArgBase {
  item: CMDArgBase;
}

type ClsArgDefinitionMap = {
  [clsName: string]: CMDArgBase;
};

function decodeArgEnumItem<T>(response: any): CMDArgEnumItem<T> {
  return {
    name: response.name,
    hide: response.hide ?? false,
    value: response.value as T,
  };
}

function decodeArgEnum<T>(response: any): CMDArgEnum<T> {
  const argEnum: CMDArgEnum<T> = {
    items: response.items.map((item: any) => decodeArgEnumItem<T>(item)),
  };
  return argEnum;
}

function decodeArgBlank<T>(response: any | undefined): CMDArgBlank<T> | undefined {
  if (response === undefined || response === null) {
    return undefined;
  }

  return {
    value: response.value as T | null,
  };
}

function decodeArgDefault<T>(response: any | undefined): CMDArgDefault<T> | undefined {
  if (response === undefined || response === null) {
    return undefined;
  }

  return {
    value: response.value as T | null,
  };
}

function decodeArgPromptInput(response: any): CMDArgPromptInput | undefined {
  if (response === undefined || response === null) {
    return undefined;
  }

  return {
    msg: response.msg as string,
  };
}

function decodePasswordArgPromptInput(response: any): CMDPasswordArgPromptInput | undefined {
  if (response === undefined || response === null) {
    return undefined;
  }

  return {
    msg: response.msg as string,
    confirm: (response.confirm ?? false) as boolean,
  };
}

function decodeArgBase(response: any): {
  argBase: CMDArgBase;
  clsDefineMap: ClsArgDefinitionMap;
} {
  let argBase: any = {
    type: response.type,
    nullable: (response.nullable ?? false) as boolean,
  };

  let clsDefineMap: ClsArgDefinitionMap = {};

  switch (response.type) {
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
      if (response.enum) {
        argBase = {
          ...argBase,
          enum: decodeArgEnum<string>(response.enum),
        };
      }
      if (response.blank) {
        argBase = {
          ...argBase,
          blank: decodeArgBlank<string>(response.blank),
        };
      }
      break;
    case "integer32":
    case "integer64":
    case "integer":
      if (response.enum) {
        argBase = {
          ...argBase,
          enum: decodeArgEnum<number>(response.enum),
        };
      }
      if (response.blank) {
        argBase = {
          ...argBase,
          blank: decodeArgBlank<number>(response.blank),
        };
      }
      break;
    case "float32":
    case "float64":
    case "float":
      if (response.enum) {
        argBase = {
          ...argBase,
          enum: decodeArgEnum<number>(response.enum),
        };
      }
      if (response.blank) {
        argBase = {
          ...argBase,
          blank: decodeArgBlank<number>(response.blank),
        };
      }
      break;
    case "boolean":
      if (response.blank) {
        argBase = {
          ...argBase,
          blank: decodeArgBlank<boolean>(response.blank),
        };
      }
      break;
    case "any":
      if (response.blank) {
        argBase = {
          ...argBase,
          blank: decodeArgBlank<boolean>(response.blank),
        };
      }
      break;
    case "object":
      if (response.args && Array.isArray(response.args) && response.args.length > 0) {
        const args: CMDArg[] = response.args.map((resSubArg: any) => {
          const subArgParse = decodeArg(resSubArg);
          clsDefineMap = {
            ...clsDefineMap,
            ...subArgParse.clsDefineMap,
          };
          return subArgParse.arg;
        });
        argBase = {
          ...argBase,
          args: args,
        };
      } else if (response.additionalProps && response.additionalProps.item) {
        const itemArgBaseParse = decodeArgBase(response.additionalProps.item);
        clsDefineMap = {
          ...clsDefineMap,
          ...itemArgBaseParse.clsDefineMap,
        };
        const argBaseType = `dict<string, ${itemArgBaseParse.argBase.type}>`;
        argBase = {
          ...argBase,
          type: argBaseType,
          item: itemArgBaseParse.argBase,
          anyType: false,
        };
      } else if (response.additionalProps && response.additionalProps.anyType) {
        const argBaseType = `dict<string, Any>`;
        argBase = {
          ...argBase,
          type: argBaseType,
          anyType: true,
        };
      }

      if (response.cls) {
        const clsName = response.cls;
        clsDefineMap[clsName] = argBase;
        argBase = {
          type: `@${response.cls}`,
          clsName: clsName,
        };
      }
      break;
    default:
      if (response.type.startsWith("array<")) {
        if (response.item) {
          const itemArgBaseParse = decodeArgBase(response.item);
          clsDefineMap = {
            ...clsDefineMap,
            ...itemArgBaseParse.clsDefineMap,
          };
          const argBaseType = `array<${itemArgBaseParse.argBase.type}>`;
          argBase = {
            ...argBase,
            type: argBaseType,
            item: itemArgBaseParse.argBase,
          };
        } else {
          throw Error("Invalid array object. Item is not defined");
        }

        if (response.cls) {
          const clsName = response.cls;
          clsDefineMap[clsName] = argBase;
          argBase = {
            type: `@${response.cls}`,
            clsName: clsName,
          };
        }
      } else if (response.type.startsWith("@")) {
        argBase["clsName"] = response.type.slice(1);
      } else {
        console.error(`Unknown type '${response.type}'`);
        throw Error(`Unknown type '${response.type}'`);
      }
  }

  return {
    argBase: argBase,
    clsDefineMap: clsDefineMap,
  };
}

function decodeArgHelp(response: any): CMDArgHelp {
  return {
    short: response.short,
    lines: response.lines,
    refCommands: response.refCommands,
  };
}

function decodeArg(response: any): {
  arg: CMDArg;
  clsDefineMap: ClsArgDefinitionMap;
} {
  const { argBase, clsDefineMap } = decodeArgBase(response);
  const options = (response.options as string[]).sort((a, b) => a.length - b.length).reverse();
  const help = response.help ? decodeArgHelp(response.help) : undefined;
  const prompt = response.prompt ? decodeArgPromptInput(response.prompt) : undefined;

  let arg: any = {
    ...argBase,
    var: response.var as string,
    options: options,
    required: (response.required ?? false) as boolean,
    stage: (response.stage ?? "Stable") as "Stable" | "Preview" | "Experimental",
    hide: (response.hide ?? false) as boolean,
    group: (response.group ?? "") as string,
    help: help,
    idPart: response.idPart,
    prompt: prompt,
    configurationKey: response.configurationKey,
    supportEnumExtension: response.enum?.supportExtension || response.item?.enum?.supportExtension || false,
    hasEnum: response.enum?.items?.length > 0 || response.item?.enum?.items?.length > 0 || false,
  };

  switch (argBase.type) {
    case "byte":
    case "binary":
    case "duration":
    case "date":
    case "dateTime":
    case "time":
    case "uuid":
    case "SubscriptionId":
    case "ResourceGroupName":
    case "ResourceId":
    case "ResourceLocation":
    case "string":
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<string>(response.default),
        };
      }
      break;
    case "password":
      if (response.prompt) {
        arg = {
          ...arg,
          prompt: decodePasswordArgPromptInput(response.prompt),
        };
      }
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<string>(response.default),
        };
      }
      break;
    case "integer32":
    case "integer64":
    case "integer":
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<number>(response.default),
        };
      }
      break;
    case "float32":
    case "float64":
    case "float":
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<number>(response.default),
        };
      }
      break;
    case "boolean":
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<boolean>(response.default),
        };
      }
      break;
    case "any":
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<any>(response.default),
        };
      }
      break;
    case "object":
      if (response.default) {
        arg = {
          ...arg,
          default: decodeArgDefault<object>(response.default),
        };
      }
      break;
    default:
      if (argBase.type.startsWith("dict<")) {
        if (response.default) {
          arg = {
            ...arg,
            default: decodeArgDefault<object>(response.default),
          };
        }
      } else if (argBase.type.startsWith("array<")) {
        if (response.singularOptions) {
          arg = {
            ...arg,
            singularOptions: response.singularOptions as string[],
          };
        }
        if (response.default) {
          arg = {
            ...arg,
            default: decodeArgDefault<Array<any>>(response.default),
          };
        }
      } else if (argBase.type.startsWith("@")) {
        if (response.singularOptions) {
          arg = {
            ...arg,
            singularOptions: response.singularOptions as string[],
          };
        }
        if (response.default) {
          arg = {
            ...arg,
            default: decodeArgDefault<any>(response.default),
          };
        }
      } else {
        console.error(`Unknown type '${argBase.type}'`);
        throw Error(`Unknown type '${argBase.type}'`);
      }
  }

  return {
    arg: arg,
    clsDefineMap: clsDefineMap,
  };
}

const DecodeArgs = (argGroups: any[]): { args: CMDArg[]; clsArgDefineMap: ClsArgDefinitionMap } => {
  let clsDefineMap: ClsArgDefinitionMap = {};
  const args: CMDArg[] = [];
  argGroups.forEach((argGroup: any) => {
    args.push(
      ...argGroup.args.map((resArg: any) => {
        const argDecode = decodeArg(resArg);
        clsDefineMap = {
          ...clsDefineMap,
          ...argDecode.clsDefineMap,
        };
        return argDecode.arg;
      }),
    );
  });
  return {
    args: args,
    clsArgDefineMap: clsDefineMap,
  };
};

export { DecodeArgs };
export type {
  ClsArgDefinitionMap,
  CMDArg,
  CMDArgBase,
  CMDObjectArg,
  CMDClsArg,
  CMDDictArgBase,
  CMDArrayArgBase,
  CMDObjectArgBase,
  CMDArgHelp,
  CMDArgDefault,
  CMDArgBlank,
  CMDArgEnumItem,
  CMDArgEnum,
  CMDArgPromptInput,
  CMDPasswordArgPromptInput,
};
