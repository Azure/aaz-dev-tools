import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  styled,
  Typography,
  TypographyProps,
} from "@mui/material";

import { commandApi, errorHandlerApi } from "../../services";
import React, { useState } from "react";

const ArgTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 700,
}));

interface CMDArrayArg {
  var: string;
  type: string;
  item?: {
    type: string;
  };
}

interface CMDDictArg {
  var: string;
  type: string;
  item?: {
    type: string;
  };
}

interface CMDArg {
  var: string;
  type: string;
}

interface UnwrapClsDialogProps {
  commandUrl: string;
  arg: CMDArg;
  open: boolean;
  onClose: (unwrapped: boolean) => Promise<void>;
}

const UnwrapClsDialog: React.FC<UnwrapClsDialogProps> = (props) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);

  const handleClose = () => {
    setInvalidText(undefined);
    props.onClose(false);
  };

  const handleUnwrap = async () => {
    setUpdating(true);

    let argVar = props.arg.var;
    if (props.arg.type.startsWith("array")) {
      if ((props.arg as CMDArrayArg).item?.type.startsWith("@")) {
        argVar += "[]";
      }
    } else if (props.arg.type.startsWith("dict")) {
      if ((props.arg as CMDDictArg).item?.type.startsWith("@")) {
        argVar += "{}";
      }
    }

    const flattenUrl = `${props.commandUrl}/Arguments/${argVar}/UnwrapClass`;

    try {
      await commandApi.unwrapClassArgument(flattenUrl);
      setUpdating(false);
      await props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      <DialogTitle>Unwrap Class Type </DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <ArgTypeTypography>{props.arg.type}</ArgTypeTypography>
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
          <>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleUnwrap}>Unwrap Class</Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default UnwrapClsDialog;
