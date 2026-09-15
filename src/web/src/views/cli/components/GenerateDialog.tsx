import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material";
import { cliApi, errorHandlerApi } from "../../../services";
import { useAsyncOperation } from "../../../services/hooks";
import { AsyncOperationBanner } from "../../../components";
import {
  collectMissingVersionsInAaz,
  exportModViewProfile,
  type ProfileCommandTree,
} from "../utils/commandTreeInitialization";
import { type CLIModViewProfiles } from "../interfaces";

interface ProfileCommandTrees {
  [name: string]: ProfileCommandTree;
}

const preview = (names: string[]) => names.slice(0, 3).join(", ") + (names.length > 3 ? ", ..." : "");

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
  const trees = Object.values(props.profileCommandTrees);
  const missingInAaz = trees.flatMap((tree) => tree.missingInAaz ?? []);
  const missingVersionsInAaz = trees.flatMap(collectMissingVersionsInAaz);

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>{!isLoading && `Generate CLI commands for ${props.moduleName} module?`}</DialogTitle>
      <DialogContent>
        <AsyncOperationBanner operation={updateAllOperation} />
        <AsyncOperationBanner operation={updateModifiedOperation} />
        {!isLoading && (missingInAaz.length > 0 || missingVersionsInAaz.length > 0) && (
          <Alert variant="outlined" severity="warning" sx={{ whiteSpace: "pre-line" }}>
            {[
              missingInAaz.length > 0 &&
                `${missingInAaz.length} generated command(s)/group(s) have no command model in the local aaz repo, ` +
                  `'Generate All' deletes their code: ${preview(missingInAaz)}`,
              missingVersionsInAaz.length > 0 &&
                `${missingVersionsInAaz.length} generated command(s) have no model of their version in the local aaz ` +
                  `repo, 'Generate All' regenerates them with another version: ${preview(missingVersionsInAaz)}`,
              "'Generate Edited Only' keeps them untouched.",
              "See: https://azure.github.io/aaz-dev-tools/pages/usage/cli-generator/#miss-command-models.",
            ]
              .filter(Boolean)
              .join("\n")}
          </Alert>
        )}
        {error && (
          <Alert variant="filled" severity="error">
            {" "}
            {errorHandlerApi.getErrorMessage(error)}{" "}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button onClick={handleGenerateAll} disabled={isLoading}>
          Generate All
        </Button>
        <Button onClick={handleGenerateModified} disabled={isLoading}>
          Generate Edited Only
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default GenerateDialog;
export type { ProfileCommandTrees };
