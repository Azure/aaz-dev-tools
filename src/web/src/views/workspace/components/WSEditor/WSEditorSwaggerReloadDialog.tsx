import React, { useState, useEffect, Fragment } from "react";
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Button,
  List,
  ListSubheader,
  Paper,
  ListItemButton,
  ListItemIcon,
  Checkbox,
  ListItemText,
  ListItem,
  Alert,
} from "@mui/material";
import type { Resource } from "../../interfaces";
import { getTypespecRPResourcesOperations } from "../../../../typespec";
import { workspaceApi, errorHandlerApi } from "../../../../services";

interface WSEditorSwaggerReloadDialogProps {
  workspaceName: string;
  workspaceUrl: string;
  open: boolean;
  source: string;
  onClose: (exported: boolean) => void;
}

const WSEditorSwaggerReloadDialog: React.FC<WSEditorSwaggerReloadDialogProps> = ({
  workspaceName,
  workspaceUrl,
  open,
  source,
  onClose,
}) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [resourceOptions, setResourceOptions] = useState<Resource[]>([]);
  const [selectedResources, setSelectedResources] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadResourceOptions();
  }, []);

  const loadResourceOptions = async () => {
    setInvalidText(undefined);
    setUpdating(true);
    try {
      const resources: Resource[] = await workspaceApi.getWorkspaceResources(workspaceUrl);
      setUpdating(false);
      setResourceOptions(resources);
      setSelectedResources(new Set(resources.map((resource) => resource.id)));
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleClose = () => {
    onClose(false);
  };

  const handleReload = async () => {
    const data = {
      resources: resourceOptions
        .filter((option) => selectedResources.has(option.id))
        .map((option) => {
          return {
            id: option.id,
            version: option.version,
          };
        }),
    };

    if (data.resources.length === 0) {
      onClose(false);
      return;
    }

    setInvalidText(undefined);
    setUpdating(true);

    try {
      if (source.toLowerCase() === "typespec") {
        const swaggerDefault = await workspaceApi.getWorkspaceSwaggerDefault(workspaceName);
        const { modNames, rpName, source: swaggerSource } = swaggerDefault;
        if (
          !modNames ||
          modNames.length === 0 ||
          !rpName ||
          !swaggerSource ||
          swaggerSource.toLowerCase() !== "typespec"
        ) {
          setInvalidText("Invalid workspace info");
          setUpdating(false);
          return;
        }
        const resourceProviderUrl =
          "/Swagger/Specs/" +
          swaggerDefault.plane +
          "/" +
          swaggerDefault.modNames.join("/") +
          `/ResourceProviders/${swaggerDefault.rpName}/TypeSpec`;
        const requestBody = {
          version: resourceOptions[0].version,
          resources: data.resources,
          resourceProviderUrl: resourceProviderUrl,
        };
        const emitterOptionRes = await getTypespecRPResourcesOperations(requestBody);
        if (emitterOptionRes.length === 0) {
          setInvalidText("Invalid resource operation emitter info");
          setUpdating(false);
          return;
        }
        data.resources = emitterOptionRes;
        await workspaceApi.reloadTypespecResources(workspaceUrl, data);
      } else {
        await workspaceApi.reloadSwaggerResources(workspaceUrl, data);
      }

      setUpdating(false);
      onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const onSelectedAllClick = () => {
    setSelectedResources(selectedResources.size > 0 ? new Set() : new Set(resourceOptions.map((op) => op.id)));
  };

  const onResourceItemClick = (resourceId: string) => {
    return () => {
      setSelectedResources((prev) => {
        const newSelectedResources = new Set(prev);
        if (newSelectedResources.has(resourceId)) {
          newSelectedResources.delete(resourceId);
        } else {
          newSelectedResources.add(resourceId);
        }
        return newSelectedResources;
      });
    };
  };

  return (
    <Dialog disableEscapeKeyDown open={open} fullWidth={true} maxWidth="xl">
      <DialogTitle>Reload {source.toLowerCase() === "typespec" ? "TypeSpec" : "Swagger"} Resources</DialogTitle>
      <DialogContent>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <List
          sx={{ flexGrow: 1 }}
          subheader={
            <ListSubheader>
              <Box
                sx={{
                  mt: 1,
                  mb: 1,
                  flexDirection: "column",
                  display: "flex",
                  alignItems: "stretch",
                  justifyContent: "flex-start",
                }}
                color="inherit"
              >
                <Paper
                  sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    mt: 1,
                  }}
                  variant="outlined"
                  square
                >
                  <ListItemButton dense onClick={onSelectedAllClick} disabled={resourceOptions.length === 0}>
                    <ListItemIcon>
                      <Checkbox
                        edge="start"
                        checked={selectedResources.size > 0 && selectedResources.size === resourceOptions.length}
                        indeterminate={selectedResources.size > 0 && selectedResources.size < resourceOptions.length}
                        tabIndex={-1}
                        disableRipple
                        inputProps={{ "aria-labelledby": "SelectAll" }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      id="SelectAll"
                      primary={`All (${resourceOptions.length})`}
                      primaryTypographyProps={{
                        variant: "h6",
                      }}
                    />
                  </ListItemButton>
                </Paper>
              </Box>
            </ListSubheader>
          }
        >
          {resourceOptions.length > 0 && (
            <Paper sx={{ ml: 2, mr: 2 }} variant="outlined" square>
              {resourceOptions.map((option) => {
                const labelId = `resource-${option.id}`;
                const selected = selectedResources.has(option.id);
                return (
                  <ListItem
                    key={option.id}
                    sx={{
                      display: "flex",
                      flexDirection: "row",
                      alignItems: "center",
                    }}
                    disablePadding
                  >
                    <ListItemButton dense onClick={onResourceItemClick(option.id)}>
                      <ListItemIcon>
                        <Checkbox
                          edge="start"
                          checked={selected}
                          tabIndex={-1}
                          disableRipple
                          inputProps={{ "aria-labelledby": labelId }}
                        />
                      </ListItemIcon>
                      <ListItemText
                        id={labelId}
                        primary={`${option.version} ${option.id}`}
                        primaryTypographyProps={{
                          variant: "h6",
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </Paper>
          )}
        </List>
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
          <Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleReload}>Reload</Button>
          </Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default WSEditorSwaggerReloadDialog;
