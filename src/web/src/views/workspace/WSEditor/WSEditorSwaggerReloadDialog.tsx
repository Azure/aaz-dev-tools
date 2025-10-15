import * as React from "react";
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
import type { Resource } from "../interfaces";
import { getTypespecRPResourcesOperations } from "../../../typespec";
import { workspaceApi, errorHandlerApi } from "../../../services";

interface WSEditorSwaggerReloadDialogProps {
  workspaceName: string;
  workspaceUrl: string;
  open: boolean;
  source: string;
  onClose: (exported: boolean) => void;
}

interface WSEditorSwaggerReloadDialogState {
  updating: boolean;
  invalidText?: string;
  resourceOptions: Resource[];
  selectedResources: Set<string>;
}

class WSEditorSwaggerReloadDialog extends React.Component<
  WSEditorSwaggerReloadDialogProps,
  WSEditorSwaggerReloadDialogState
> {
  constructor(props: WSEditorSwaggerReloadDialogProps) {
    super(props);
    this.state = {
      updating: false,
      invalidText: undefined,
      resourceOptions: [],
      selectedResources: new Set(),
    };
  }

  componentDidMount() {
    this.loadResourceOptions();
  }

  loadResourceOptions = async () => {
    this.setState({
      invalidText: undefined,
      updating: true,
    });
    try {
      const resources: Resource[] = await workspaceApi.getWorkspaceResources(this.props.workspaceUrl);
      this.setState({
        updating: false,
        resourceOptions: resources,
        selectedResources: new Set(resources.map((resource) => resource.id)),
      });
    } catch (err: any) {
      console.error(err);
      this.setState({
        invalidText: errorHandlerApi.getErrorMessage(err),
        updating: false,
      });
    }
  };

  handleClose = () => {
    this.props.onClose(false);
  };

  handleReload = async () => {
    const { selectedResources, resourceOptions } = this.state;
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
      this.props.onClose(false);
      return;
    }

    this.setState({
      invalidText: undefined,
      updating: true,
    });

    try {
      if (this.props.source.toLowerCase() === "typespec") {
        const swaggerDefault = await workspaceApi.getWorkspaceSwaggerDefault(this.props.workspaceName);
        const { modNames, rpName, source } = swaggerDefault;
        if (!modNames || modNames.length === 0 || !rpName || !source || source.toLowerCase() !== "typespec") {
          this.setState({
            invalidText: "Invalid workspace info",
            updating: false,
          });
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
        console.log("request emitter data: ", requestBody);
        const emitterOptionRes = await getTypespecRPResourcesOperations(requestBody);
        console.log("emitterResourceOptionRes: ", emitterOptionRes);
        if (emitterOptionRes.length === 0) {
          this.setState({
            invalidText: "Invalid resource operation emitter info",
            updating: false,
          });
          return;
        }
        data.resources = emitterOptionRes;
        await workspaceApi.reloadTypespecResources(this.props.workspaceUrl, data);
      } else {
        await workspaceApi.reloadSwaggerResources(this.props.workspaceUrl, data);
      }

      this.setState({
        updating: false,
      });
      this.props.onClose(true);
    } catch (err: any) {
      console.error(err);
      this.setState({
        invalidText: errorHandlerApi.getErrorMessage(err),
        updating: false,
      });
    }
  };

  onSelectedAllClick = () => {
    this.setState((preState) => {
      return {
        ...preState,
        selectedResources:
          preState.selectedResources.size > 0 ? new Set() : new Set(preState.resourceOptions.map((op) => op.id)),
      };
    });
  };

  onResourceItemClick = (resourceId: string) => {
    return () => {
      this.setState((preState) => {
        const selectedResources = new Set(preState.selectedResources);
        if (selectedResources.has(resourceId)) {
          selectedResources.delete(resourceId);
        } else {
          selectedResources.add(resourceId);
        }
        return {
          ...preState,
          selectedResources: selectedResources,
        };
      });
    };
  };

  render() {
    const { invalidText, selectedResources, updating, resourceOptions } = this.state;

    return (
      <Dialog disableEscapeKeyDown open={this.props.open} fullWidth={true} maxWidth="xl">
        <DialogTitle>
          Reload {this.props.source.toLowerCase() === "typespec" ? "TypeSpec" : "Swagger"} Resources
        </DialogTitle>
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
                  {/* <Typography component='h6'>Resource Url</Typography> */}

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
                    <ListItemButton dense onClick={this.onSelectedAllClick} disabled={resourceOptions.length === 0}>
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
                      <ListItemButton dense onClick={this.onResourceItemClick(option.id)}>
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
            <React.Fragment>
              <Button onClick={this.handleClose}>Cancel</Button>
              <Button onClick={this.handleReload}>Reload</Button>
            </React.Fragment>
          )}
        </DialogActions>
      </Dialog>
    );
  }
}

export default WSEditorSwaggerReloadDialog;
