import { Box, CardContent } from "@mui/material";

import pluralize from "pluralize";
import React, { useState } from "react";

import ArgumentNavigation from "./ArgumentNavigation";
import ArgumentDialog from "./ArgumentDialog";
import UnwrapClsDialog from "./UnwrapClsDialog";
import FlattenDialog from "./FlattenDialog";

import { CardTitleTypography } from "../WSEditor/WSEditorTheme";
import {
  type ClsArgDefinitionMap,
  type CMDArg,
  type CMDArgBase,
  type CMDObjectArg,
  type CMDClsArg,
  type CMDDictArgBase,
  type CMDArrayArgBase,
  type CMDObjectArgBase,
} from "../../utils/decodeArgs";

interface WSEditorCommandArgumentsContentProps {
  commandUrl: string;
  args: CMDArg[];
  clsArgDefineMap: ClsArgDefinitionMap;
  onReloadArgs: () => Promise<void>;
  onAddSubCommand: (argVar: string, subArgOptions: { var: string; options: string }[], argStackNames: string[]) => void;
}

interface ArgIdx {
  var: string;
  displayKey: string;
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

export default WSEditorCommandArgumentsContent;
