import React from "react";
import { Box, Button, Card, CardContent, Typography, ButtonBase, styled, TypographyProps } from "@mui/material";
import DataObjectIcon from "@mui/icons-material/DataObject";
import EditIcon from "@mui/icons-material/Edit";
import { SubtitleTypography, CardTitleTypography } from "./WSEditorTheme";

interface Example {
  name: string;
  commands: string[];
}

interface ObjectOutput {
  type: "object";
  ref: string;
  clientFlatten: boolean;
}

interface ArrayOutput {
  type: "array";
  ref: string;
  clientFlatten: boolean;
  nextLink: string;
}

interface StringOutput {
  type: "string";
  ref: string;
  value: string;
}

type Output = ObjectOutput | ArrayOutput | StringOutput;

interface Resource {
  id: string;
  version: string;
  subresource?: string;
  swagger: string;
}

interface Command {
  id: string;
  names: string[];
  help?: {
    short: string;
    lines?: string[];
  };
  stage: "Stable" | "Preview" | "Experimental";
  version: string;
  examples?: Example[];
  outputs?: Output[];
  resources: Resource[];
  confirmation?: string;
  args?: any[];
  clsArgDefineMap?: any;
}

interface OutputCardProps {
  command: Command;
  onOutputDialogDisplay: (idx: number) => void;
}

const OutputTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const OutputRefTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 700,
}));

const OutputFlagTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#8888C3",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const OutputEditTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#5d64cf",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

function OutputCard(props: OutputCardProps) {
  const outputs = props.command.outputs!;

  const buildBaseOutputView = (
    idx: number,
    refName: string,
    type: string,
    flags: string[],
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    return (
      <Box sx={{ my: 1 }}>
        <Box
          sx={{
            p: 2,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          <DataObjectIcon fontSize="small" />
          <SubtitleTypography sx={{ ml: 1 }}>JSON</SubtitleTypography>
          <Button
            sx={{ flexShrink: 0, ml: 3 }}
            startIcon={<EditIcon color="secondary" fontSize="small" />}
            onClick={onClick}
          >
            <OutputEditTypography>Edit</OutputEditTypography>
          </Button>
        </Box>
        <Box
          key={`output-${idx}-${refName}`}
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "stretch",
            justifyContent: "flex-start",
            mb: 2,
            ml: 6,
          }}
        >
          <Box>
            <ButtonBase onClick={onClick}>
              <OutputRefTypography>{refName}</OutputRefTypography>
            </ButtonBase>
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
              <OutputTypeTypography
                sx={{
                  flexShrink: 0,
                }}
              >{`/${type}/`}</OutputTypeTypography>
              <Box sx={{ flexGrow: 1 }} />
              {flags.map((flag, idx) => {
                return <OutputFlagTypography key={`output-flag-${idx}`}>{`[${flag}]`}</OutputFlagTypography>;
              })}
            </Box>
          </Box>
        </Box>
      </Box>
    );
  };

  const buildObjectOutputView = (
    output: ObjectOutput,
    idx: number,
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    return buildBaseOutputView(
      idx,
      output.ref,
      output.type,
      output.clientFlatten ? ["Flattened"] : ["Unflattened"],
      onClick,
    );
  };

  const buildArrayOutputView = (
    output: ArrayOutput,
    idx: number,
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    return buildBaseOutputView(
      idx,
      output.ref,
      output.type,
      output.clientFlatten ? ["Flattened"] : ["Unflattened"],
      onClick,
    );
  };

  const buildStringOutputView = (
    output: StringOutput,
    idx: number,
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    const title = output.ref ? output.ref : output.value;
    return buildBaseOutputView(idx, title, output.type, [], onClick);
  };

  const buildOutputView = (output: Output, idx: number) => {
    const onClick = () => {
      props.onOutputDialogDisplay(idx);
    };
    switch (output.type) {
      case "object":
        return buildObjectOutputView(output, idx, onClick);
      case "array":
        return buildArrayOutputView(output, idx, onClick);
      case "string":
        return buildStringOutputView(output, idx, onClick);
    }
  };

  return (
    <Card
      elevation={3}
      sx={{
        flexGrow: 1,
        display: "flex",
        flexDirection: "column",
        mt: 1,
        p: 2,
      }}
    >
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
          <CardTitleTypography sx={{ flexShrink: 0 }}>[ OUTPUT ]</CardTitleTypography>
        </Box>
        {outputs.length > 0 &&
          outputs.map((output, idx) => <div key={`output-${idx}`}>{buildOutputView(output, idx)}</div>)}
      </CardContent>
    </Card>
  );
}

export default OutputCard;
export type { OutputCardProps, Command, Output, ObjectOutput, ArrayOutput, StringOutput, Example, Resource };
