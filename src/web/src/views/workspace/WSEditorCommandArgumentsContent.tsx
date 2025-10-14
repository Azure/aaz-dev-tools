import {
  Alert,
  Box,
  Button,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  TextField,
} from "@mui/material";

import { commandApi, errorHandlerApi } from "../../services";
import pluralize from "pluralize";
import React, { useEffect, useState } from "react";
import WSECArgumentSimilarPicker, { ArgSimilarTree, BuildArgSimilarTree } from "./argument/WSECArgumentSimilarPicker";

import ArgumentNavigation from "./ArgumentNavigation";
import ArgumentDialog from "./ArgumentDialog";
import UnwrapClsDialog from "./UnwrapClsDialog";

import { CardTitleTypography } from "./WSEditorTheme";

interface WSEditorCommandArgumentsContentProps {
  commandUrl: string;
  args: CMDArg[];
  clsArgDefineMap: ClsArgDefinitionMap;
  onReloadArgs: () => Promise<void>;
  onAddSubCommand: (argVar: string, subArgOptions: { var: string; options: string }[], argStackNames: string[]) => void;
}

const WSEditorCommandArgumentsContent: React.FC<WSEditorCommandArgumentsContentProps> = ({
  commandUrl,
  args,
  clsArgDefineMap,
  onReloadArgs,
  onAddSubCommand,
}) => {
  const [displayArgumentDialog, setDisplayArgumentDialog] = useState<boolean>(false);
  const [editArg, setEditArg] = useState<CMDArg | undefined>(undefined);
  const [, setEditArgIdxStack] = useState<ArgIdx[] | undefined>(undefined);
  const [displayFlattenDialog, setDisplayFlattenDialog] = useState<boolean>(false);
  const [displayUnwrapClsDialog, setDisplayUnwrapClsDialog] = useState<boolean>(false);

  const handleArgumentDialogClose = async (updated: boolean) => {
    if (updated) {
      onReloadArgs();
    }
    setDisplayArgumentDialog(false);
    setEditArg(undefined);
    setEditArgIdxStack(undefined);
  };

  const handleEditArgument = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
    setEditArg(arg);
    setEditArgIdxStack(argIdxStack);
    setDisplayArgumentDialog(true);
  };

  const handleFlattenDialogClose = async (flattened: boolean) => {
    if (flattened) {
      onReloadArgs();
    }
    setDisplayFlattenDialog(false);
    setEditArg(undefined);
    setEditArgIdxStack(undefined);
  };

  const handleArgumentFlatten = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
    setEditArg(arg);
    setEditArgIdxStack(argIdxStack);
    setDisplayFlattenDialog(true);
  };

  const handleUnwrapClsDialogClose = async (unwrapped: boolean) => {
    if (unwrapped) {
      onReloadArgs();
    }
    setDisplayUnwrapClsDialog(false);
    setEditArg(undefined);
    setEditArgIdxStack(undefined);
  };

  const handleUnwrapClsArgument = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
    setEditArg(arg);
    setEditArgIdxStack(argIdxStack);
    setDisplayUnwrapClsDialog(true);
  };

  const handleAddSubcommand = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
    const argVar = arg.var;
    const argStackNames = argIdxStack.map((argIdx) => {
      let name = argIdx.displayKey;
      while (name.startsWith("-")) {
        name = name.slice(1);
      }
      if (name.endsWith("[]") || name.endsWith("{}")) {
        name = name.slice(0, name.length - 2);
        name = pluralize.singular(name);
      }
      return name;
    });
    let a: CMDArgBase | undefined = arg;
    if (a.type.startsWith("@")) {
      const clsName = (a as CMDClsArg).clsName;
      a = clsArgDefineMap[clsName];
    }
    if (a.type.startsWith("dict<")) {
      a = (a as CMDDictArgBase).item;
    } else if (a.type.startsWith("array<")) {
      a = (a as CMDArrayArgBase).item;
    }
    let subArgOptions: { var: string; options: string }[] = [];
    if (a !== undefined) {
      let subArgs;
      if (a.type.startsWith("@")) {
        const clsName = (a as CMDClsArg).clsName;
        subArgs = (clsArgDefineMap[clsName] as CMDObjectArgBase).args;
      } else {
        subArgs = (a as CMDObjectArg).args;
      }
      subArgOptions = subArgs.map((value) => {
        return {
          var: value.var,
          options: value.options.join(" "),
        };
      });
    }

    onAddSubCommand(argVar, subArgOptions, argStackNames);
  };

  return (
    <React.Fragment>
      <CardContent
        sx={{
          flex: "1 0 auto",
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
        }}
      >
        <Box
          sx={{
            mb: 2,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          <CardTitleTypography sx={{ flexShrink: 0 }}>[ ARGUMENT ]</CardTitleTypography>
        </Box>
        <ArgumentNavigation
          commandUrl={commandUrl}
          args={args}
          clsArgDefineMap={clsArgDefineMap}
          onEdit={handleEditArgument}
          onFlatten={handleArgumentFlatten}
          onUnwrap={handleUnwrapClsArgument}
          onAddSubcommand={handleAddSubcommand}
        />
      </CardContent>

      {displayArgumentDialog && (
        <ArgumentDialog
          commandUrl={commandUrl}
          arg={editArg!}
          clsArgDefineMap={clsArgDefineMap}
          open={displayArgumentDialog}
          onClose={handleArgumentDialogClose}
        />
      )}
      {displayFlattenDialog && (
        <FlattenDialog
          commandUrl={commandUrl}
          arg={editArg!}
          clsArgDefineMap={clsArgDefineMap}
          open={displayFlattenDialog}
          onClose={handleFlattenDialogClose}
        />
      )}
      {displayUnwrapClsDialog && (
        <UnwrapClsDialog
          commandUrl={commandUrl}
          arg={editArg!}
          open={displayUnwrapClsDialog}
          onClose={handleUnwrapClsDialogClose}
        />
      )}
    </React.Fragment>
  );
};

interface ArgIdx {
  var: string;
  displayKey: string;
}

function FlattenDialog(props: {
  commandUrl: string;
  arg: CMDArg;
  clsArgDefineMap: ClsArgDefinitionMap;
  open: boolean;
  onClose: (flattened: boolean) => Promise<void>;
}) {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [subArgOptions, setSubArgOptions] = useState<{ var: string; options: string }[]>([]);
  const [argSimilarTree, setArgSimilarTree] = useState<ArgSimilarTree | undefined>(undefined);
  const [argSimilarTreeExpandedIds, setArgSimilarTreeExpandedIds] = useState<string[]>([]);
  const [argSimilarTreeArgIdsUpdated, setArgSimilarTreeArgIdsUpdated] = useState<string[]>([]);

  useEffect(() => {
    const { arg, clsArgDefineMap } = props;
    let subArgs;
    if (arg.type.startsWith("@")) {
      const clsName = (arg as CMDClsArg).clsName;
      subArgs = (clsArgDefineMap[clsName] as CMDObjectArgBase).args;
    } else {
      subArgs = (arg as CMDObjectArg).args;
    }
    const subArgOptions = subArgs.map((value) => {
      return {
        var: value.var,
        options: value.options.join(" "),
      };
    });

    setSubArgOptions(subArgOptions);
    setArgSimilarTree(undefined);
    setArgSimilarTreeExpandedIds([]);
  }, [props.arg]);

  const handleClose = () => {
    setInvalidText(undefined);
    props.onClose(false);
  };

  const verifyFlatten = () => {
    setInvalidText(undefined);
    const argOptions: { [argVar: string]: string[] } = {};
    let invalidText: string | undefined = undefined;

    subArgOptions.forEach((arg, idx) => {
      const names = arg.options.split(" ").filter((n) => n.length > 0);
      if (names.length < 1) {
        invalidText = `Prop ${idx + 1} option name is required.`;
        return undefined;
      }

      for (const idx in names) {
        const piece = names[idx];
        if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
          invalidText = `Invalid 'Prop ${idx + 1} option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `;
          return undefined;
        }
      }
      argOptions[arg.var] = names;
    });
    if (invalidText !== undefined) {
      setInvalidText(invalidText);
      return undefined;
    }

    return {
      subArgsOptions: argOptions,
    };
  };

  const handleFlatten = async () => {
    const data = verifyFlatten();
    if (data === undefined) {
      return;
    }

    setUpdating(true);

    const flattenUrl = `${props.commandUrl}/Arguments/${props.arg.var}/Flatten`;

    try {
      await commandApi.flattenArgument(flattenUrl, data);
      setUpdating(false);
      await props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleDisplaySimilar = async () => {
    if (verifyFlatten() === undefined) {
      return;
    }

    setUpdating(true);

    try {
      const res = await commandApi.findSimilarArguments(props.commandUrl, props.arg.var);
      setUpdating(false);
      const { tree, expandedIds } = BuildArgSimilarTree(res);
      setArgSimilarTree(tree);
      setArgSimilarTreeExpandedIds(expandedIds);
      setArgSimilarTreeArgIdsUpdated([]);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleDisableSimilar = () => {
    setArgSimilarTree(undefined);
    setArgSimilarTreeExpandedIds([]);
  };

  const onSimilarTreeUpdated = (newTree: ArgSimilarTree) => {
    setArgSimilarTree(newTree);
  };

  const onSimilarTreeExpandedIdsUpdated = (expandedIds: string[]) => {
    setArgSimilarTreeExpandedIds(expandedIds);
  };

  const handleFlattenSimilar = async () => {
    const data = verifyFlatten();
    if (data === undefined) {
      return;
    }
    setUpdating(true);
    let invalidText = "";
    const updatedIds: string[] = [...argSimilarTreeArgIdsUpdated];
    for (const idx in argSimilarTree!.selectedArgIds) {
      const argId = argSimilarTree!.selectedArgIds[idx];
      if (updatedIds.indexOf(argId) === -1) {
        const flattenUrl = `${argId}/Flatten`;
        try {
          await commandApi.flattenArgument(flattenUrl, data);
          updatedIds.push(argId);
          setArgSimilarTreeArgIdsUpdated([...updatedIds]);
        } catch (err: any) {
          console.error(err);
          invalidText += errorHandlerApi.getErrorMessage(err);
        }
      }
    }

    if (invalidText.length > 0) {
      setInvalidText(invalidText);
      setUpdating(false);
    } else {
      setUpdating(false);
      await props.onClose(true);
    }
  };

  const buildSubArgText = (arg: { var: string; options: string }, idx: number) => {
    return (
      <TextField
        id={`subArg-${arg.var}`}
        key={arg.var}
        label={`Prop ${idx + 1}`}
        helperText={idx === 0 ? "You can input multiple names separated by a space character" : undefined}
        type="text"
        fullWidth
        variant="standard"
        value={arg.options}
        onChange={(event: any) => {
          const options = subArgOptions.map((value) => {
            if (value.var === arg.var) {
              return {
                ...value,
                options: event.target.value,
              };
            } else {
              return value;
            }
          });
          setSubArgOptions(options);
        }}
        margin="normal"
        required
      />
    );
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      {!argSimilarTree && (
        <>
          <DialogTitle>Flatten Props</DialogTitle>
          <DialogContent dividers={true}>
            {invalidText && (
              <Alert variant="filled" severity="error">
                {" "}
                {invalidText}{" "}
              </Alert>
            )}
            {subArgOptions.map(buildSubArgText)}
          </DialogContent>
        </>
      )}

      {argSimilarTree && (
        <>
          <DialogTitle>Flatten Similar Argument Props</DialogTitle>
          <DialogContent dividers={true}>
            {invalidText && (
              <Alert variant="filled" severity="error">
                {" "}
                {invalidText}{" "}
              </Alert>
            )}
            <WSECArgumentSimilarPicker
              tree={argSimilarTree}
              expandedIds={argSimilarTreeExpandedIds}
              updatedIds={argSimilarTreeArgIdsUpdated}
              onTreeUpdated={onSimilarTreeUpdated}
              onToggle={onSimilarTreeExpandedIdsUpdated}
            />
          </DialogContent>
        </>
      )}
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && !argSimilarTree && (
          <>
            <Button onClick={handleClose}>Cancel</Button>
            {!props.arg.type.startsWith("@") && <Button onClick={handleFlatten}>Flatten</Button>}
            {props.arg.type.startsWith("@") && <Button onClick={handleFlatten}>Unwrap & Flatten</Button>}
            <Button onClick={handleDisplaySimilar}>Flatten Similar</Button>
          </>
        )}
        {!updating && argSimilarTree && (
          <>
            <Button onClick={handleDisableSimilar}>Back</Button>
            <Button onClick={handleFlattenSimilar} disabled={argSimilarTree.selectedArgIds.length === 0}>
              Update
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}

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

export default WSEditorCommandArgumentsContent;
export { DecodeArgs };
export type { ClsArgDefinitionMap, CMDArg };
