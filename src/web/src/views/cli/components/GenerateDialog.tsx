import { useState } from "react";
import { Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, LinearProgress } from "@mui/material";
import { cliApi, errorHandlerApi } from "../../../services";
import { exportModViewProfile, type ProfileCommandTree } from "../utils/commandTreeInitialization";
import { type CLIModViewProfiles } from "../interfaces";

interface ProfileCommandTrees {
  [name: string]: ProfileCommandTree;
}

interface GenerateDialogProps {
  repoName: string;
  moduleName: string;
  profileCommandTrees: ProfileCommandTrees;
  open: boolean;
  onClose: (generated: boolean) => void;
}

const GenerateDialog = (props: GenerateDialogProps) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);

  const handleClose = () => {
    props.onClose(false);
  };

  const handleGenerateAll = async () => {
    const profiles: CLIModViewProfiles = {};
    Object.values(props.profileCommandTrees).forEach((tree) => {
      profiles[tree.name] = exportModViewProfile(tree);
    });
    const data = {
      name: props.moduleName,
      profiles: profiles,
    };

    setUpdating(true);
    try {
      await cliApi.updateCliModule(props.repoName, props.moduleName, data);
      setUpdating(false);
      props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleGenerateModified = async () => {
    const profiles: CLIModViewProfiles = {};
    Object.values(props.profileCommandTrees).forEach((tree) => {
      profiles[tree.name] = exportModViewProfile(tree);
    });
    const data = {
      name: props.moduleName,
      profiles: profiles,
    };

    setUpdating(true);
    try {
      await cliApi.patchCliModule(props.repoName, props.moduleName, data);
      setUpdating(false);
      props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Generate CLI commands to {props.moduleName}</DialogTitle>
      <DialogContent>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
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
            <Button onClick={handleGenerateAll}>Generate All</Button>
            <Button onClick={handleGenerateModified}>Generate Edited Only</Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default GenerateDialog;
export type { ProfileCommandTrees };
