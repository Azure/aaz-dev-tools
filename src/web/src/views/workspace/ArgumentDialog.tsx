import {
  Alert,
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  InputLabel,
  LinearProgress,
  Radio,
  RadioGroup,
  Switch,
  TextField,
} from "@mui/material";

import { commandApi, errorHandlerApi } from "../../services";
import React, { useEffect, useState } from "react";
import WSECArgumentSimilarPicker, { ArgSimilarTree, BuildArgSimilarTree } from "./argument/WSECArgumentSimilarPicker";

interface CMDClsArg {
  var: string;
  type: string;
  clsName: string;
  options: string[];
  singularOptions?: string[];
  required: boolean;
  stage: "Stable" | "Preview" | "Experimental";
  hide: boolean;
  group: string;
  help?: {
    short: string;
    lines?: string[];
  };
  default?: {
    value: any;
  };
  prompt?: {
    msg: string;
    confirm?: boolean;
  };
  configurationKey?: string;
  supportEnumExtension?: boolean;
  hasEnum?: boolean;
}

interface CMDArrayArg {
  var: string;
  type: string;
  options: string[];
  singularOptions?: string[];
  required: boolean;
  stage: "Stable" | "Preview" | "Experimental";
  hide: boolean;
  group: string;
  help?: {
    short: string;
    lines?: string[];
  };
  default?: {
    value: any;
  };
  prompt?: {
    msg: string;
  };
  configurationKey?: string;
  supportEnumExtension?: boolean;
  hasEnum?: boolean;
}

interface CMDPasswordArg {
  var: string;
  type: string;
  options: string[];
  required: boolean;
  stage: "Stable" | "Preview" | "Experimental";
  hide: boolean;
  group: string;
  help?: {
    short: string;
    lines?: string[];
  };
  default?: {
    value: any;
  };
  prompt?: {
    msg: string;
    confirm?: boolean;
  };
  configurationKey?: string;
  supportEnumExtension?: boolean;
  hasEnum?: boolean;
}

interface CMDArg {
  var: string;
  type: string;
  options: string[];
  required: boolean;
  stage: "Stable" | "Preview" | "Experimental";
  hide: boolean;
  group: string;
  help?: {
    short: string;
    lines?: string[];
  };
  default?: {
    value: any;
  };
  prompt?: {
    msg: string;
  };
  configurationKey?: string;
  supportEnumExtension?: boolean;
  hasEnum?: boolean;
}

type ClsArgDefinitionMap = {
  [clsName: string]: any;
};

interface ArgumentDialogProps {
  commandUrl: string;
  arg: CMDArg;
  clsArgDefineMap: ClsArgDefinitionMap;
  open: boolean;
  onClose: (updated: boolean) => Promise<void>;
}

function convertArgDefaultText(defaultText: string, argType: string): any {
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
      if (Number.isNaN(parseInt(defaultText.trim()))) {
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
      if (Number.isInteger(parseInt(trimmed))) {
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

const ArgumentDialog: React.FC<ArgumentDialogProps> = (props) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [stage, setStage] = useState<string>("");
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [options, setOptions] = useState<string>("");
  const [singularOptions, setSingularOptions] = useState<string | undefined>(undefined);
  const [group, setGroup] = useState<string>("");
  const [hide, setHide] = useState<boolean>(false);
  const [supportEnumExtension, setSupportEnumExtension] = useState<boolean>(false);
  const [shortHelp, setShortHelp] = useState<string>("");
  const [longHelp, setLongHelp] = useState<string>("");
  const [argSimilarTree, setArgSimilarTree] = useState<ArgSimilarTree | undefined>(undefined);
  const [argSimilarTreeExpandedIds, setArgSimilarTreeExpandedIds] = useState<string[]>([]);
  const [argSimilarTreeArgIdsUpdated, setArgSimilarTreeArgIdsUpdated] = useState<string[]>([]);
  const [hasDefault, setHasDefault] = useState<boolean | undefined>(false);
  const [defaultValue, setDefaultValue] = useState<any | undefined>(undefined);
  const [defaultValueInJson, setDefaultValueInJson] = useState<boolean>(false);
  const [hasPrompt, setHasPrompt] = useState<boolean | undefined>(false);
  const [promptMsg, setPromptMsg] = useState<string | undefined>(undefined);
  const [promptConfirm, setPromptConfirm] = useState<boolean | undefined>(undefined);
  const [configurationKey, setConfigurationKey] = useState<string>("");
  const [isClientArg, setIsClientArg] = useState<boolean>(false);

  const handleClose = () => {
    setInvalidText(undefined);
    props.onClose(false);
  };

  const verifyModification = () => {
    setInvalidText(undefined);
    const name = options.trim();
    const sName = singularOptions?.trim() ?? undefined;
    const sHelp = shortHelp.trim();
    const lHelp = longHelp.trim();
    const gName = group.trim();
    const cfgKey = configurationKey.trim();

    const names = name.split(" ").filter((n) => n.length > 0);
    const sNames = sName?.split(" ").filter((n) => n.length > 0) ?? undefined;

    if (names.length < 1) {
      setInvalidText(`Argument 'Option names' is required.`);
      return undefined;
    }

    for (const idx in names) {
      const piece = names[idx];
      if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
        setInvalidText(`Invalid 'Option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `);
        return undefined;
      }
    }

    if (sNames) {
      for (const idx in sNames) {
        const piece = sNames[idx];
        if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
          setInvalidText(
            `Invalid 'Singular option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `,
          );
          return undefined;
        }
      }
    }

    if (
      sHelp.length < 1 &&
      names.find((n) => {
        return n === "subscription" || n === "resource-group";
      }) === undefined
    ) {
      setInvalidText(`Field 'Short Summary' is required.`);
      return undefined;
    }

    let lines: string[] | null = null;
    if (lHelp.length > 1) {
      lines = lHelp.split("\n").filter((l) => l.length > 0);
    }

    let argCfgKey: string | null = null;
    if (cfgKey.length > 0) {
      argCfgKey = cfgKey;
    }

    let argDefault = undefined;
    if (hasDefault === false) {
      if (props.arg.default !== undefined) {
        argDefault = null;
      }
    } else if (hasDefault === true) {
      if (defaultValue === undefined) {
        setInvalidText(`Field 'Default Value' is undefined.`);
        return undefined;
      } else {
        try {
          let argType = props.arg.type;
          if (argType.startsWith("@")) {
            argType = props.clsArgDefineMap[(props.arg as CMDClsArg).clsName].type;
          }
          argDefault = {
            value: convertArgDefaultText(defaultValue!, argType),
          };
        } catch (err: any) {
          setInvalidText(`Field 'Default Value' is invalid: ${err.message}.`);
          return undefined;
        }
        if (props.arg.default !== undefined && props.arg.default.value === argDefault.value) {
          argDefault = undefined;
        }
      }
    }

    let argPrompt = undefined;
    if (hasPrompt === false) {
      if (props.arg.prompt !== undefined) {
        argPrompt = null;
      }
    } else if (hasPrompt === true) {
      if (promptMsg === undefined) {
        setInvalidText(`Field 'Prompt Message' is undefined.`);
        return undefined;
      } else {
        const msg = promptMsg.trim();
        if (msg.length < 1) {
          setInvalidText(`Field 'Prompt Message' is empty.`);
          return undefined;
        }
        if (!msg.endsWith(":")) {
          setInvalidText(`Field 'Prompt Message' must end with a colon.`);
          return undefined;
        }
        argPrompt = {
          msg: msg,
          confirm: promptConfirm,
        };
      }
    }

    return {
      options: names,
      singularOptions: sNames,
      stage: stage,
      group: gName,
      hide: hide,
      help: {
        short: sHelp,
        lines: lines,
      },
      default: argDefault,
      prompt: argPrompt,
      configurationKey: argCfgKey,
      supportEnumExtension: supportEnumExtension,
    };
  };

  const handleModify = async () => {
    const data = verifyModification();
    if (data === undefined) {
      return;
    }

    setUpdating(true);

    const argumentUrl = `${props.commandUrl}/Arguments/${props.arg.var}`;

    try {
      await commandApi.updateCommandArgument(argumentUrl, data);
      setUpdating(false);
      await props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleDisplaySimilar = async () => {
    if (verifyModification() === undefined) {
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

  const handleModifySimilar = async () => {
    const data = verifyModification();
    if (data === undefined) {
      return;
    }

    setUpdating(true);
    let invalidText = "";
    const updatedIds: string[] = [...argSimilarTreeArgIdsUpdated];
    for (const idx in argSimilarTree!.selectedArgIds) {
      const argId = argSimilarTree!.selectedArgIds[idx];
      if (updatedIds.indexOf(argId) === -1) {
        try {
          await commandApi.updateArgumentById(argId, data);
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

  useEffect(() => {
    const { arg, clsArgDefineMap } = props;
    setIsClientArg(arg.var.startsWith("$Client."));

    setOptions(arg.options.join(" "));
    if (arg.type.startsWith("array")) {
      setSingularOptions((arg as CMDArrayArg).singularOptions?.join(" ") ?? "");
    } else if (arg.type.startsWith("@") && clsArgDefineMap[(arg as CMDClsArg).clsName].type.startsWith("array")) {
      setSingularOptions((arg as CMDClsArg).singularOptions?.join(" ") ?? "");
    } else {
      setSingularOptions(undefined);
    }

    if (
      arg.type === "object" ||
      arg.type.startsWith("dict<") ||
      arg.type.startsWith("array<") ||
      arg.type.startsWith("@")
    ) {
      setHasPrompt(undefined);
    } else {
      setHasPrompt(arg.prompt !== undefined);
      if (arg.prompt !== undefined) {
        setPromptMsg(arg.prompt.msg);
        setPromptConfirm(undefined);
      }
    }
    if (arg.type === "password") {
      setPromptConfirm((arg as CMDPasswordArg).prompt?.confirm ?? false);
    }
    setStage(props.arg.stage);
    setGroup(props.arg.group);
    setHide(props.arg.hide);
    setSupportEnumExtension(props.arg.supportEnumExtension || false);
    setShortHelp(props.arg.help?.short ?? "");
    setLongHelp(props.arg.help?.lines?.join("\n") ?? "");
    setConfigurationKey(props.arg.configurationKey ?? "");
    setUpdating(false);
    setArgSimilarTree(undefined);
    setArgSimilarTreeExpandedIds([]);

    if (
      arg.type === "object" ||
      arg.type.startsWith("dict<") ||
      arg.type.startsWith("array<") ||
      arg.type.startsWith("@")
    ) {
      setDefaultValueInJson(true);
      if (props.arg.default !== undefined && props.arg.default !== null) {
        setHasDefault(true);
        setDefaultValue(JSON.stringify(props.arg.default.value));
      } else {
        setHasDefault(false);
        setDefaultValue(undefined);
      }
    } else {
      setDefaultValueInJson(false);
      if (props.arg.default !== undefined && props.arg.default !== null) {
        setHasDefault(true);
        setDefaultValue(props.arg.default.value.toString());
      } else {
        setHasDefault(false);
        setDefaultValue(undefined);
      }
    }
  }, [props.arg]);

  return (
    <Dialog disableEscapeKeyDown open={props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      {!argSimilarTree && (
        <>
          <DialogTitle>{isClientArg ? "Modify Client Argument" : "Modify Argument"}</DialogTitle>
          <DialogContent dividers={true}>
            {invalidText && (
              <Alert variant="filled" severity="error">
                {" "}
                {invalidText}{" "}
              </Alert>
            )}
            <TextField
              id="options"
              label="Option names"
              helperText="You can input multiple names separated by a space character"
              type="text"
              fullWidth
              variant="standard"
              value={options}
              onChange={(event: any) => {
                setOptions(event.target.value);
              }}
              margin="normal"
              required
            />
            {singularOptions !== undefined && (
              <TextField
                id="singularOptions"
                label="Singular option names"
                type="text"
                fullWidth
                variant="standard"
                value={singularOptions}
                onChange={(event: any) => {
                  setSingularOptions(event.target.value);
                }}
                margin="normal"
              />
            )}
            {!isClientArg && (
              <>
                <TextField
                  id="group"
                  label="Argument Group"
                  type="text"
                  fullWidth
                  variant="standard"
                  value={group}
                  onChange={(event: any) => {
                    setGroup(event.target.value);
                  }}
                  margin="normal"
                />
                <InputLabel required shrink sx={{ font: "inherit" }}>
                  Stage
                </InputLabel>
                <RadioGroup
                  row
                  value={stage}
                  name="stage"
                  onChange={(event: any) => {
                    setStage(event.target.value);
                  }}
                >
                  <FormControlLabel value="Stable" control={<Radio />} label="Stable" sx={{ ml: 4 }} />
                  <FormControlLabel value="Preview" control={<Radio />} label="Preview" sx={{ ml: 4 }} />
                  <FormControlLabel value="Experimental" control={<Radio />} label="Experimental" sx={{ ml: 4 }} />
                </RadioGroup>

                {!props.arg.required && (
                  <>
                    <InputLabel shrink sx={{ font: "inherit" }}>
                      Hide Argument
                    </InputLabel>
                    <Switch
                      sx={{ ml: 4 }}
                      checked={hide}
                      onChange={() => {
                        setHide(!hide);
                      }}
                    />
                  </>
                )}

                {props.arg.hasEnum && (
                  <>
                    <InputLabel shrink sx={{ font: "inherit" }}>
                      Support Enum Extension
                    </InputLabel>
                    <Switch
                      sx={{ ml: 4 }}
                      checked={supportEnumExtension}
                      onChange={() => {
                        setSupportEnumExtension(!supportEnumExtension);
                      }}
                    />
                  </>
                )}
              </>
            )}
            {hasDefault !== undefined && (
              <>
                <InputLabel shrink sx={{ font: "inherit" }}>
                  Default Value
                </InputLabel>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    justifyContent: "flex-start",
                    ml: 4,
                  }}
                >
                  <Switch
                    checked={hasDefault}
                    onChange={() => {
                      setHasDefault(!hasDefault);
                      setDefaultValue(undefined);
                    }}
                  />
                  <TextField
                    id="defaultValue"
                    label="default Value"
                    hiddenLabel
                    type="text"
                    hidden={!hasDefault}
                    fullWidth
                    size="small"
                    value={defaultValue !== undefined ? defaultValue : ""}
                    onChange={(event: any) => {
                      setDefaultValue(event.target.value);
                    }}
                    placeholder={defaultValueInJson ? "Default Value in json format" : "Default Value"}
                    margin="normal"
                    aria-controls=""
                    required
                  />
                </Box>
              </>
            )}

            {hasPrompt !== undefined && (
              <>
                <InputLabel shrink sx={{ font: "inherit" }}>
                  Prompt Input
                </InputLabel>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    justifyContent: "flex-start",
                    ml: 4,
                  }}
                >
                  <Switch
                    checked={hasPrompt}
                    onChange={() => {
                      setHasPrompt(!hasPrompt);
                      setPromptMsg(undefined);
                    }}
                  />
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "stretch",
                      justifyContent: "flex-start",
                      flexGrow: 1,
                    }}
                  >
                    <TextField
                      id="SetPromptMsg"
                      label="Prompt Message"
                      hiddenLabel
                      type="text"
                      hidden={!hasPrompt}
                      fullWidth
                      size="small"
                      value={promptMsg !== undefined ? promptMsg : ""}
                      onChange={(event: any) => {
                        setPromptMsg(event.target.value);
                      }}
                      placeholder="Please input the prompt hint end with a colon."
                      margin="normal"
                      aria-controls=""
                      required
                    />
                    {promptConfirm !== undefined && (
                      <>
                        <FormControlLabel
                          control={
                            <Checkbox
                              size="small"
                              checked={promptConfirm}
                              onChange={() => {
                                setPromptConfirm(!promptConfirm);
                              }}
                            />
                          }
                          label="Confirm input"
                        />
                      </>
                    )}
                  </Box>
                </Box>
              </>
            )}
            {!isClientArg && (
              <TextField
                id="configurationKey"
                label="Configuration Key"
                helperText="The key to retrieve the default value from cli Configuration"
                type="text"
                fullWidth
                variant="standard"
                value={configurationKey}
                onChange={(event: any) => {
                  setConfigurationKey(event.target.value);
                }}
                margin="normal"
              />
            )}

            <TextField
              id="shortSummary"
              label="Short Summary"
              type="text"
              fullWidth
              variant="standard"
              value={shortHelp}
              onChange={(event: any) => {
                setShortHelp(event.target.value);
              }}
              margin="normal"
              required
            />
            <TextField
              id="longSummary"
              label="Long Summary"
              helperText="Please add long summary in lines."
              type="text"
              fullWidth
              multiline
              rows={4}
              variant="standard"
              value={longHelp}
              onChange={(event: any) => {
                setLongHelp(event.target.value);
              }}
              margin="normal"
            />
          </DialogContent>
        </>
      )}

      {argSimilarTree && (
        <>
          <DialogTitle>Modify Similar Arguments</DialogTitle>
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
            {!props.arg.var.startsWith("@") && (
              <Button onClick={handleModify}>{isClientArg ? "Update Global" : "Update"}</Button>
            )}
            {!isClientArg && <Button onClick={handleDisplaySimilar}>Update Similar</Button>}
          </>
        )}
        {!updating && argSimilarTree && (
          <>
            <Button onClick={handleDisableSimilar}>Back</Button>
            <Button onClick={handleModifySimilar} disabled={argSimilarTree.selectedArgIds.length === 0}>
              Update
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ArgumentDialog;
