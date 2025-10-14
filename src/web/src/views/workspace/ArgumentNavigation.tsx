import React, { useEffect, useState } from "react";
import { Box, Button, ButtonBase, styled, Typography, TypographyProps } from "@mui/material";
import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";
import EditIcon from "@mui/icons-material/Edit";
import ImportExportIcon from "@mui/icons-material/ImportExport";
import {
  ExperimentalTypography,
  LongHelpTypography,
  PreviewTypography,
  ShortHelpPlaceHolderTypography,
  ShortHelpTypography,
  StableTypography,
} from "./WSEditorTheme";
import ArgumentPropsReviewer from "./ArgumentPropsReviewer";
import type { CMDArg, ClsArgDefinitionMap } from "./WSEditorCommandArgumentsContent";

interface CMDArgBase {
  type: string;
  nullable: boolean;
  blank?: any;
}

interface CMDClsArg extends CMDArg {
  clsName: string;
  singularOptions?: string[];
}

interface CMDObjectArg extends CMDArg {
  args: CMDArg[];
}

interface CMDDictArg extends CMDArg {
  item?: any;
  anyType: boolean;
}

interface CMDArrayArg extends CMDArg {
  item: any;
  singularOptions?: string[];
}

interface CMDStringArg extends CMDArg {
  enum?: {
    items: { name: string; hide: boolean; value: string }[];
  };
}

interface CMDNumberArg extends CMDArg {
  enum?: {
    items: { name: string; hide: boolean; value: number }[];
  };
}

interface ArgIdx {
  var: string;
  displayKey: string;
}

interface ArgumentNavigationProps {
  commandUrl: string;
  args: CMDArg[];
  clsArgDefineMap: ClsArgDefinitionMap;
  onEdit: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
  onFlatten: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
  onUnwrap: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
  onAddSubcommand: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
}

interface ArgNavBarProps {
  argIdxStack: ArgIdx[];
  onChangeArgIdStack: (end: number) => void;
}

interface ArgumentReviewerProps {
  arg: CMDArg;
  depth: number;
  onEdit: () => void;
  onUnwrap: () => void;
}

const NavBarItemTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const NavBarItemHightLightedTypography = styled(NavBarItemTypography)<TypographyProps>(() => ({
  color: "#5d64cf",
}));

const ArgNameTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 26,
  fontWeight: 700,
}));

const ArgTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 700,
}));

const ArgRequiredTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#fad105",
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 200,
}));

const ArgEditTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#5d64cf",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const ArgChoicesTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 14,
  fontWeight: 700,
}));

const spliceArgOptionsString = (arg: CMDArg, depth: number) => {
  let optionsString = arg.options
    .map((option) => {
      if (depth === 0) {
        if (option.length === 1) {
          return "-" + option;
        } else {
          return "--" + option;
        }
      } else {
        return "." + option;
      }
    })
    .join(" ");

  if ((arg as CMDArrayArg).singularOptions) {
    const singularOptionString = (arg as CMDArrayArg)
      .singularOptions!.map((option: string) => {
        if (depth === 0) {
          if (option.length === 1) {
            return "-" + option;
          } else {
            return "--" + option;
          }
        } else {
          return "." + option;
        }
      })
      .join(" ");
    optionsString += ` (${singularOptionString})`;
  } else if ((arg as CMDClsArg).singularOptions) {
    const singularOptionString = (arg as CMDClsArg)
      .singularOptions!.map((option: string) => {
        if (depth === 0) {
          if (option.length === 1) {
            return "-" + option;
          } else {
            return "--" + option;
          }
        } else {
          return "." + option;
        }
      })
      .join(" ");
    optionsString += ` (${singularOptionString})`;
  }

  return optionsString;
};

const ArgNavBar: React.FC<ArgNavBarProps> = ({ argIdxStack, onChangeArgIdStack }) => {
  return (
    <React.Fragment>
      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "flex-start",
          mt: 1,
          mb: 0.5,
          mr: 2,
        }}
      >
        <ButtonBase
          key="Back"
          onClick={() => {
            onChangeArgIdStack(0);
          }}
        >
          <ArrowBackIosIcon sx={{ fontSize: 14 }} />
        </ButtonBase>
        {argIdxStack.slice(0, -1).map((argIdx: ArgIdx, index: number) => (
          <ButtonBase
            key={`${index}`}
            onClick={() => {
              onChangeArgIdStack(index + 1);
            }}
          >
            <NavBarItemTypography sx={{ flexShrink: 0 }}>
              {index > 0 ? `.${argIdx.displayKey}` : argIdx.displayKey}
            </NavBarItemTypography>
          </ButtonBase>
        ))}
        <ButtonBase
          key={`${argIdxStack.length - 1}`}
          onClick={() => {
            onChangeArgIdStack(argIdxStack.length);
          }}
        >
          <NavBarItemHightLightedTypography sx={{ flexShrink: 0 }}>
            {argIdxStack.length > 1
              ? `.${argIdxStack[argIdxStack.length - 1].displayKey}`
              : argIdxStack[argIdxStack.length - 1].displayKey}
          </NavBarItemHightLightedTypography>
        </ButtonBase>
      </Box>
    </React.Fragment>
  );
};

const ArgumentReviewer: React.FC<ArgumentReviewerProps> = ({ arg, depth, onEdit, onUnwrap }) => {
  const [choices, setChoices] = useState<string[]>([]);

  const buildArgOptionsString = () => {
    const argOptionsString = spliceArgOptionsString(arg, depth - 1);
    return <ArgNameTypography>{argOptionsString}</ArgNameTypography>;
  };

  useEffect(() => {
    const newChoices: string[] = [];
    if ((arg as CMDStringArg).enum) {
      const items = (arg as CMDStringArg).enum!.items;
      for (const idx in items) {
        const enumItem = items[idx];
        newChoices.push(enumItem.name);
      }
    } else if ((arg as CMDNumberArg).enum) {
      const items = (arg as CMDNumberArg).enum!.items;
      for (const idx in items) {
        const enumItem = items[idx];
        newChoices.push(enumItem.name);
      }
    }
    setChoices(newChoices);
  }, [arg]);

  const getUnwrapKeywords = () => {
    if (arg.type.startsWith("@")) {
      return "Unwrap";
    } else if (arg.type.startsWith("array")) {
      if ((arg as CMDArrayArg).item?.type.startsWith("@")) {
        return "Unwrap Element";
      }
    } else if (arg.type.startsWith("dict")) {
      if ((arg as CMDDictArg).item?.type.startsWith("@")) {
        return "Unwrap Element";
      }
    }
    return null;
  };

  const getDefaultValueToString = () => {
    if (
      arg.type === "object" ||
      arg.type.startsWith("dict<") ||
      arg.type.startsWith("array<") ||
      arg.type.startsWith("@")
    ) {
      if (arg.default !== undefined && arg.default !== null) {
        return JSON.stringify(arg.default.value);
      }
    } else {
      if (arg.default !== undefined && arg.default !== null) {
        return arg.default.value.toString();
      }
    }
    return "";
  };

  return (
    <React.Fragment>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          justifyContent: "flex-start",
          mt: 1,
          mb: 2,
        }}
      >
        <Box
          sx={{
            flexGrow: 1,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          {buildArgOptionsString()}
          <Button
            sx={{ flexShrink: 0, ml: 3 }}
            startIcon={<EditIcon color="secondary" fontSize="small" />}
            onClick={() => {
              onEdit();
            }}
          >
            <ArgEditTypography>Edit</ArgEditTypography>
          </Button>
        </Box>

        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "flex-start",
            alignItems: "stretch",
            ml: 6,
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              justifyContent: "flex-start",
              alignItems: "center",
            }}
          >
            <ArgTypeTypography>{`/${arg.type}/`}</ArgTypeTypography>
          </Box>
          {getUnwrapKeywords() !== null && (
            <Button
              sx={{ flexShrink: 0, ml: 1 }}
              startIcon={<ImportExportIcon color="secondary" fontSize="small" />}
              onClick={() => {
                onUnwrap();
              }}
            >
              <ArgEditTypography>{getUnwrapKeywords()!}</ArgEditTypography>
            </Button>
          )}
          <Box sx={{ flexGrow: 1 }} />
          {arg.required && <ArgRequiredTypography>[Required]</ArgRequiredTypography>}
        </Box>
        {(arg.default !== undefined || choices.length > 0 || arg.configurationKey !== undefined) && (
          <Box
            sx={{
              ml: 5,
              mt: 0.5,
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
            }}
          >
            {choices.length > 0 && (
              <ArgChoicesTypography sx={{ ml: 1 }}>{`Choices: ` + choices.join(", ")}</ArgChoicesTypography>
            )}
            {arg.default !== undefined && (
              <ArgChoicesTypography sx={{ ml: 1 }}>{`Default: ${getDefaultValueToString()}`}</ArgChoicesTypography>
            )}
            {arg.configurationKey !== undefined && (
              <ArgChoicesTypography sx={{ ml: 1 }}>{`ConfigurationKey: ${arg.configurationKey}`}</ArgChoicesTypography>
            )}
          </Box>
        )}
        {arg.help?.short && <ShortHelpTypography sx={{ ml: 6, mt: 1.5 }}> {arg.help?.short} </ShortHelpTypography>}
        {!arg.help?.short && (
          <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>
            Please add argument short summary!
          </ShortHelpPlaceHolderTypography>
        )}
        {arg.help?.lines && (
          <Box sx={{ ml: 6, mt: 1, mb: 1 }}>
            {arg.help.lines.map((line, idx) => (
              <LongHelpTypography key={idx}>{line}</LongHelpTypography>
            ))}
          </Box>
        )}
      </Box>
    </React.Fragment>
  );
};

const ArgumentNavigation: React.FC<ArgumentNavigationProps> = ({
  commandUrl,
  args,
  clsArgDefineMap,
  onEdit,
  onFlatten,
  onUnwrap,
  onAddSubcommand,
}) => {
  const [argIdxStack, setArgIdxStack] = useState<ArgIdx[]>([]);

  const getArgProps = (
    selectedArgBase: CMDArgBase,
  ): { title: string; props: CMDArg[]; flattenArgVar: string | undefined } | undefined => {
    if (selectedArgBase.type.startsWith("@")) {
      const clsArgDefine = clsArgDefineMap[(selectedArgBase as CMDClsArg).clsName];
      const clsArgProps = getArgProps(clsArgDefine);
      if (clsArgProps !== undefined && clsArgDefine.type === "object") {
        clsArgProps!.flattenArgVar = (selectedArgBase as CMDClsArg).var;
      }
      return clsArgProps;
    }
    if (selectedArgBase.type === "object") {
      return {
        title: "Props",
        props: (selectedArgBase as CMDObjectArg).args,
        flattenArgVar: (selectedArgBase as CMDObjectArg).var,
      };
    } else if (selectedArgBase.type.startsWith("dict<")) {
      const item = (selectedArgBase as CMDDictArg).item;
      const itemProps = item ? getArgProps(item) : undefined;
      if (!itemProps) {
        return undefined;
      }
      return {
        title: "Dict Element Props",
        props: itemProps.props,
        flattenArgVar: undefined,
      };
    } else if (selectedArgBase.type.startsWith("array<")) {
      const itemProps = getArgProps((selectedArgBase as CMDArrayArg).item);
      if (!itemProps) {
        return undefined;
      }
      return {
        title: "Array Element Props",
        props: itemProps.props,
        flattenArgVar: undefined,
      };
    } else {
      return undefined;
    }
  };

  const getSelectedArg = (stack: ArgIdx[]): CMDArg | undefined => {
    if (stack.length === 0) {
      return undefined;
    } else {
      let argsArray: CMDArg[] = [...args];
      let selectedArg: CMDArg | undefined = undefined;
      for (const i in stack) {
        const argVar = stack[i].var;
        selectedArg = argsArray.find((arg) => arg.var === argVar);
        if (!selectedArg) {
          break;
        }
        argsArray = getArgProps(selectedArg)?.props ?? [];
      }
      return selectedArg;
    }
  };

  useEffect(() => {
    setArgIdxStack([]);
  }, [commandUrl]);

  useEffect(() => {
    const stack = [...argIdxStack];
    while (stack.length > 0 && !getSelectedArg(stack)) {
      stack.pop();
    }
    if (stack.length !== argIdxStack.length) {
      setArgIdxStack(stack);
    }
  }, [args, clsArgDefineMap]);

  const handleSelectSubArg = (subArgVar: string) => {
    let subArg;
    if (argIdxStack.length > 0) {
      const arg = getSelectedArg(argIdxStack);
      if (!arg) {
        return;
      }
      subArg = getArgProps(arg)?.props.find((a) => a.var === subArgVar);
    } else {
      subArg = args.find((a: CMDArg) => a.var === subArgVar);
    }

    if (!subArg) {
      return;
    }
    const argIdx: ArgIdx = {
      var: subArg.var,
      displayKey: subArg.options[0],
    };
    if (argIdxStack.length === 0) {
      if (argIdx.displayKey.length === 1) {
        argIdx.displayKey = `-${argIdx.displayKey}`;
      } else {
        argIdx.displayKey = `--${argIdx.displayKey}`;
      }
    }

    let argType = subArg.type;
    if (argType.startsWith("@")) {
      argType = clsArgDefineMap[(subArg as CMDClsArg).clsName].type;
    }
    if (argType.startsWith("dict<")) {
      argIdx.displayKey += "{}";
    } else if (argType.startsWith("array<")) {
      argIdx.displayKey += "[]";
    }

    setArgIdxStack([...argIdxStack, argIdx]);
  };

  const handleChangeArgIdStack = (end: number) => {
    setArgIdxStack(argIdxStack.slice(0, end));
  };

  const buildArgumentReviewer = () => {
    const selectedArg = getSelectedArg(argIdxStack);
    if (!selectedArg) {
      return <></>;
    }

    const stage = selectedArg.stage;

    return (
      <React.Fragment>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "flex-start",
            justifyContent: "flex-start",
          }}
        >
          <ArgNavBar argIdxStack={argIdxStack} onChangeArgIdStack={handleChangeArgIdStack} />
          {stage === "Stable" && <StableTypography sx={{ flexShrink: 0 }}>{stage}</StableTypography>}
          {stage === "Preview" && <PreviewTypography sx={{ flexShrink: 0 }}>{stage}</PreviewTypography>}
          {stage === "Experimental" && <ExperimentalTypography sx={{ flexShrink: 0 }}>{stage}</ExperimentalTypography>}
        </Box>
        <ArgumentReviewer
          arg={selectedArg}
          depth={argIdxStack.length}
          onEdit={() => {
            onEdit(selectedArg, argIdxStack);
          }}
          onUnwrap={() => {
            onUnwrap(selectedArg, argIdxStack);
          }}
        />
      </React.Fragment>
    );
  };

  const buildArgumentPropsReviewer = () => {
    if (argIdxStack.length === 0) {
      if (args.length === 0) {
        return <></>;
      }
      return (
        <ArgumentPropsReviewer
          title={"Argument Groups"}
          args={args}
          onFlatten={undefined}
          onAddSubcommand={undefined}
          depth={argIdxStack.length}
          onSelectSubArg={handleSelectSubArg}
        />
      );
    } else {
      const selectedArg = getSelectedArg(argIdxStack);
      if (!selectedArg) {
        return <></>;
      }
      const argProps = getArgProps(selectedArg);
      if (!argProps) {
        return <></>;
      }
      const canFlatten = argProps.flattenArgVar !== undefined;
      return (
        <ArgumentPropsReviewer
          title={argProps.title}
          args={argProps.props}
          depth={argIdxStack.length}
          selectedArg={selectedArg!}
          onFlatten={
            canFlatten
              ? () => {
                  onFlatten(selectedArg!, argIdxStack);
                }
              : undefined
          }
          onAddSubcommand={() => {
            onAddSubcommand(selectedArg!, argIdxStack);
          }}
          onSelectSubArg={handleSelectSubArg}
        />
      );
    }
  };

  return (
    <React.Fragment>
      {argIdxStack.length > 0 && <React.Fragment>{buildArgumentReviewer()}</React.Fragment>}
      <React.Fragment>{buildArgumentPropsReviewer()}</React.Fragment>
    </React.Fragment>
  );
};

export default ArgumentNavigation;
export type { ArgumentNavigationProps, ArgIdx, ArgumentReviewerProps, ArgNavBarProps };
