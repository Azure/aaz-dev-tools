import React, { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  FormLabel,
  Switch,
  Typography,
  TypographyProps,
  FormLabelProps,
} from "@mui/material";
import { styled } from "@mui/material";
import { commandApi, errorHandlerApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import { AsyncOperationBanner } from "../../../../components";
import { DecodeResponseCommand } from "../../utils/decodeResponseCommand";

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

function isObjectOutput(output: Output): output is ObjectOutput {
  return output.type === "object";
}

function isArrayOutput(output: Output): output is ArrayOutput {
  return output.type === "array";
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
  outputs?: Output[];
  resources: any[];
}

const OutputDialogLabel = styled(FormLabel)<FormLabelProps>(() => ({
  fontSize: 12,
}));

const OutputDialogMainTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 18,
  fontWeight: 400,
}));

interface OutputDialogProps {
  workspaceUrl: string;
  command: Command;
  idx?: number;
  open: boolean;
  onClose: (newCommand?: Command) => void;
}

const OutputDialog: React.FC<OutputDialogProps> = (props) => {
  const updateOutputsOperation = useAsyncOperation(commandApi.updateCommandOutputs);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const outputs = props.command.outputs ?? [];
  const output = outputs[props.idx!];
  const [flatten, setFlatten] = useState<boolean>(output.type !== "string" ? output.clientFlatten : false);
  const flattenLabelContent = flatten ? "Flattened" : "Unflattened";

  const handleClose = () => {
    setInvalidText(undefined);
    props.onClose();
  };

  const handleUpdateOutput = async () => {
    setInvalidText(undefined);

    if (isObjectOutput(output) || isArrayOutput(output)) {
      let commandNames = props.command.names;
      const leafUrl =
        `${props.workspaceUrl}/CommandTree/Nodes/aaz/` +
        commandNames.slice(0, -1).join("/") +
        "/Leaves/" +
        commandNames[commandNames.length - 1];

      output.clientFlatten = !output.clientFlatten;

      try {
        const responseData = await updateOutputsOperation.execute(leafUrl, outputs);
        const cmd = DecodeResponseCommand(responseData);
        props.onClose(cmd);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
      }
    } else {
      console.error(`Invalid output type for flatten switch: ${output.type}`);
      setInvalidText(`Invalid output type for flatten switch: ${output.type}`);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      <DialogTitle>JSON Format Output</DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        {(output.type !== "string" || output.ref !== undefined) && (
          <React.Fragment>
            <OutputDialogLabel>Output Reference</OutputDialogLabel>
            <OutputDialogMainTypography sx={{ my: 1 }}>{output.ref}</OutputDialogMainTypography>
          </React.Fragment>
        )}
        {output.type == "string" && output.ref == undefined && (
          <React.Fragment>
            <OutputDialogLabel>Output Value</OutputDialogLabel>
            <OutputDialogMainTypography sx={{ my: 1 }}>{output.value}</OutputDialogMainTypography>
          </React.Fragment>
        )}
        {output.type == "array" && output.nextLink !== undefined && (
          <React.Fragment>
            <OutputDialogLabel>Next Link Reference</OutputDialogLabel>
            <OutputDialogMainTypography sx={{ my: 1 }}>{output.nextLink}</OutputDialogMainTypography>
          </React.Fragment>
        )}
        {(output.type !== "string" || output.ref !== undefined) && (
          <React.Fragment>
            <OutputDialogLabel>Client Flatten</OutputDialogLabel>
            <Box sx={{ display: "flex" }}>
              <FormControlLabel
                sx={{ ml: 2 }}
                control={
                  <Switch
                    checked={flatten}
                    onChange={(event: any) => {
                      setFlatten(event.target.checked);
                    }}
                  />
                }
                label={<OutputDialogMainTypography sx={{ mx: 2 }}>{flattenLabelContent}</OutputDialogMainTypography>}
                labelPlacement="end"
              />
            </Box>
          </React.Fragment>
        )}
      </DialogContent>
      <DialogActions>
        <AsyncOperationBanner operation={updateOutputsOperation} />
        {!updateOutputsOperation.loading && <Button onClick={handleClose}>Cancel</Button>}
        <Button onClick={handleUpdateOutput} disabled={updateOutputsOperation.loading}>
          Update
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default OutputDialog;
export type { Output, ObjectOutput, ArrayOutput, StringOutput, OutputDialogProps };
