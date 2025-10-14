import React from "react";
import { Box, Button, ButtonBase, styled, Typography, TypographyProps } from "@mui/material";
import { ChevronRight } from "@mui/icons-material";
import AddIcon from "@mui/icons-material/Add";
import CallSplitSharpIcon from "@mui/icons-material/CallSplitSharp";
import { SmallExperimentalTypography, SmallPreviewTypography, SubtitleTypography } from "./WSEditorTheme";
import type { CMDArg } from "./WSEditorCommandArgumentsContent";

interface CMDArrayArg extends CMDArg {
  singularOptions?: string[];
}

interface CMDClsArg extends CMDArg {
  singularOptions?: string[];
}

interface ArgGroup {
  name: string;
  args: CMDArg[];
}

interface ArgumentPropsReviewerProps {
  title: string;
  args: CMDArg[];
  onFlatten?: () => void;
  onAddSubcommand?: () => void;
  selectedArg?: CMDArg;
  depth: number;
  onSelectSubArg: (subArgVar: string) => void;
}

const PropArgTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const PropRequiredTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#dba339",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const PropHiddenTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#8888C3",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const ArgGroupTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 18,
  fontWeight: 200,
}));

const PropArgOptionTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 700,
}));

const PropHiddenArgOptionTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#8888C3",
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 700,
}));

const PropArgShortSummaryTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 14,
  fontStyle: "italic",
  fontWeight: 400,
}));

const ArgEditTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#5d64cf",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
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

const ArgumentPropsReviewer: React.FC<ArgumentPropsReviewerProps> = (props) => {
  const groupArgs: { [name: string]: CMDArg[] } = {};
  if (props.args !== undefined) {
    props.args.forEach((arg) => {
      const groupName: string = arg.group.length > 0 ? arg.group : "";
      if (!(groupName in groupArgs)) {
        groupArgs[groupName] = [];
      }
      groupArgs[groupName].push(arg);
    });
  }

  const groups: ArgGroup[] = [];

  for (const groupName in groupArgs) {
    groupArgs[groupName].sort((a, b) => {
      if (a.required && !b.required) {
        return -1;
      } else if (!a.required && b.required) {
        return 1;
      }
      return a.options[0].localeCompare(b.options[0]);
    });
    groups.push({
      name: groupName,
      args: groupArgs[groupName],
    });
  }
  groups.sort((a, b) => a.name.localeCompare(b.name));

  const checkCanAddSubcommand = () => {
    if (props.selectedArg && props.args.length > 0) {
      return true;
    }
    return false;
  };

  const buildArg = (arg: CMDArg, idx: number) => {
    const argOptionsString = spliceArgOptionsString(arg, props.depth);
    return (
      <Box
        key={`group-arg-${idx}`}
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          justifyContent: "flex-start",
          mb: 2,
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "flex-end",
            justifyContent: "flex-start",
          }}
        >
          <ButtonBase
            onClick={() => {
              props.onSelectSubArg(arg.var);
            }}
          >
            {!arg.hide && <PropArgOptionTypography sx={{ flexShrink: 0 }}>{argOptionsString}</PropArgOptionTypography>}
            {arg.hide && (
              <PropHiddenArgOptionTypography sx={{ flexShrink: 0 }}>{argOptionsString}</PropHiddenArgOptionTypography>
            )}
            <ChevronRight />
          </ButtonBase>
          <Box sx={{ flexGrow: 1 }} />
          {arg.stage === "Preview" && (
            <SmallPreviewTypography sx={{ flexShrink: 0 }}>{arg.stage}</SmallPreviewTypography>
          )}
          {arg.stage === "Experimental" && (
            <SmallExperimentalTypography sx={{ flexShrink: 0 }}>{arg.stage}</SmallExperimentalTypography>
          )}
        </Box>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "flex-start",
            justifyContent: "flex-start",
          }}
        >
          <Box
            sx={{
              width: 300,
              flexShrink: 0,
              flexDirection: "row",
              display: "flex",
              alignItems: "center",
            }}
          >
            <PropArgTypeTypography
              sx={{
                flexShrink: 0,
              }}
            >{`/${arg.type}/`}</PropArgTypeTypography>
            <Box sx={{ flexGrow: 1 }} />
            {arg.required && <PropRequiredTypography>[Required]</PropRequiredTypography>}
            {arg.hide && <PropHiddenTypography>[Hidden]</PropHiddenTypography>}
          </Box>
          {arg.help && (
            <Box
              sx={{
                ml: 4,
              }}
            >
              <PropArgShortSummaryTypography>{arg.help.short}</PropArgShortSummaryTypography>
            </Box>
          )}
        </Box>
      </Box>
    );
  };

  const buildArgGroup = (group: ArgGroup, idx: number) => {
    return (
      <Box
        key={`group-${idx}`}
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          justifyContent: "flex-start",
          ml: 2,
          mr: 2,
          mb: 1,
        }}
      >
        <Box sx={{ flexShrink: 0, ml: 2, p: 1 }}>
          <ArgGroupTypography id={`argGroup-${idx}-header`}>
            {group.name.length > 0 ? `${group.name} Group` : "Default Group"}
          </ArgGroupTypography>
        </Box>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "stretch",
            justifyContent: "flex-start",
            ml: 3,
            mr: 3,
          }}
        >
          {group.args.map(buildArg)}
        </Box>
      </Box>
    );
  };

  if (groups.length === 0) {
    return <></>;
  }

  return (
    <React.Fragment>
      <Box
        sx={{
          p: 2,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
        }}
      >
        <SubtitleTypography>{props.title}</SubtitleTypography>
        {props.onFlatten !== undefined && (
          <Button
            sx={{ flexShrink: 0, ml: 3 }}
            startIcon={<CallSplitSharpIcon color="secondary" fontSize="small" />}
            onClick={props.onFlatten}
          >
            <ArgEditTypography>Flatten</ArgEditTypography>
          </Button>
        )}

        {props.onAddSubcommand !== undefined && checkCanAddSubcommand() && (
          <Button
            sx={{ flexShrink: 0, ml: 3 }}
            startIcon={<AddIcon color="secondary" fontSize="small" />}
            onClick={props.onAddSubcommand}
          >
            <ArgEditTypography>Subcommands</ArgEditTypography>
          </Button>
        )}
      </Box>
      {groups.map(buildArgGroup)}
    </React.Fragment>
  );
};

export default ArgumentPropsReviewer;
export type { ArgumentPropsReviewerProps, ArgGroup };
