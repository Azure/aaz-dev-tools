import { Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, LinearProgress } from "@mui/material";
import { cliApi, errorHandlerApi } from "../../../services";
import { useAsyncOperation } from "../../../services/hooks";
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
  const updateAllOperation = useAsyncOperation(cliApi.updateCliModule);
  const updateModifiedOperation = useAsyncOperation(cliApi.patchCliModule);

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

    try {
      await updateAllOperation.execute(props.repoName, props.moduleName, data);
      props.onClose(true);
    } catch (error) {
      console.error("Generate all failed:", error);
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

    try {
      await updateModifiedOperation.execute(props.repoName, props.moduleName, data);
      props.onClose(true);
    } catch (error) {
      console.error("Generate modified failed:", error);
    }
  };

  const isLoading = updateAllOperation.loading || updateModifiedOperation.loading;
  const error = updateAllOperation.error || updateModifiedOperation.error;

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Generate CLI commands to {props.moduleName}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert variant="filled" severity="error">
            {" "}
            {errorHandlerApi.getErrorMessage(error)}{" "}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        {isLoading && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!isLoading && (
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
