import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  TextField,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { commandApi, errorHandlerApi } from "../../services";
import WSECArgumentSimilarPicker, { ArgSimilarTree, BuildArgSimilarTree } from "./argument/WSECArgumentSimilarPicker";

interface FlattenDialogProps {
  commandUrl: string;
  arg: CMDArg;
  clsArgDefineMap: ClsArgDefinitionMap;
  open: boolean;
  onClose: (flattened: boolean) => Promise<void>;
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

interface CMDArgPromptInput {
  msg: string;
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

type ClsArgDefinitionMap = {
  [clsName: string]: CMDArgBase;
};

const FlattenDialog: React.FC<FlattenDialogProps> = (props) => {
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
};

export default FlattenDialog;
export type { CMDArg, ClsArgDefinitionMap };
