import React, { useEffect, useState } from "react";
import { Box, Button, styled, Typography, TypographyProps } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import ImportExportIcon from "@mui/icons-material/ImportExport";
import { LongHelpTypography, ShortHelpPlaceHolderTypography, ShortHelpTypography } from "../WSEditorTheme";
import type { CMDArg } from "../WSEditorCommandArgumentsContent";

interface CMDClsArg extends CMDArg {
  clsName: string;
  singularOptions?: string[];
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

interface ArgumentReviewerProps {
  arg: CMDArg;
  depth: number;
  onEdit: () => void;
  onUnwrap: () => void;
}

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

export default ArgumentReviewer;
export type { ArgumentReviewerProps };
