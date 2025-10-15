import React, { useEffect, useState } from "react";
import { Box } from "@mui/material";
import { ExperimentalTypography, PreviewTypography, StableTypography } from "../WSEditor/WSEditorTheme";
import ArgumentPropsReviewer from "./ArgumentPropsReviewer";
import ArgNavBar, { type ArgIdx } from "./ArgNavBar";
import ArgumentReviewer from "./ArgumentReviewer";
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

interface ArgumentNavigationProps {
  commandUrl: string;
  args: CMDArg[];
  clsArgDefineMap: ClsArgDefinitionMap;
  onEdit: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
  onFlatten: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
  onUnwrap: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
  onAddSubcommand: (arg: CMDArg, argIdxStack: ArgIdx[]) => void;
}

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
export type { ArgumentNavigationProps };
