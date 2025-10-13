import {
  Box,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Button,
  InputLabel,
  Alert,
} from "@mui/material";
import * as React from "react";
import { SwaggerItemSelector } from "./WSEditorSwaggerPicker";
import styled from "@emotion/styled";
import { Plane } from "./WSEditorCommandContent";
import { workspaceApi, specsApi, errorHandlerApi } from "../../services";

interface WorkspaceCreateDialogProps {
  openDialog: boolean;
  name: string;
  onClose: (value: any | null) => void;
}

interface WorkspaceCreateDialogState {
  loading: boolean;

  invalidText?: string;
  workspaceName: string;

  planes: Plane[];
  planeOptions: string[];
  selectedPlane: string | null;

  moduleOptions: string[];
  moduleOptionsCommonPrefix: string;
  selectedModule: string | null;

  resourceProviderOptions: string[];
  resourceProviderOptionsCommonPrefix: string;
  selectedResourceProvider: string | null;
}

class WorkspaceCreateDialog extends React.Component<WorkspaceCreateDialogProps, WorkspaceCreateDialogState> {
  constructor(props: WorkspaceCreateDialogProps) {
    super(props);
    this.state = {
      loading: false,
      invalidText: undefined,
      workspaceName: props.name,

      planes: [],
      planeOptions: [],
      selectedPlane: null,

      moduleOptions: [],
      moduleOptionsCommonPrefix: "",
      selectedModule: null,

      resourceProviderOptions: [],
      resourceProviderOptionsCommonPrefix: "",
      selectedResourceProvider: null,
    };
  }

  componentDidMount(): void {
    this.loadPlanes().then(async () => {
      if (this.state.planes.length > 0) {
        await this.onPlaneSelectorUpdate(this.state.planes[0].name);
      }
    });
  }

  loadPlanes = async () => {
    try {
      this.setState({
        loading: true,
      });

      const planes = await specsApi.getPlanes();
      const planeOptions: string[] = planes.map((v) => v.displayName);
      this.setState({
        planes: planes,
        planeOptions: planeOptions,
        loading: false,
      });
      if (planeOptions.length > 0) {
        await this.onPlaneSelectorUpdate(planeOptions[0]);
      }
    } catch (err: any) {
      console.error(err);
      this.setState({
        loading: false,
        invalidText: errorHandlerApi.getErrorMessage(err),
      });
    }
  };

  onPlaneSelectorUpdate = async (planeDisplayName: string | null) => {
    const plane = this.state.planes.find((v) => v.displayName === planeDisplayName) ?? null;
    if (this.state.selectedPlane !== (plane?.displayName ?? null)) {
      if (!plane) {
        return;
      }
      this.setState({
        selectedPlane: plane?.displayName ?? null,
      });
      await this.loadSwaggerModules(plane);
    } else {
      this.setState({
        selectedPlane: plane?.displayName ?? null,
      });
    }
  };

  loadSwaggerModules = async (plane: Plane | null) => {
    if (plane !== null) {
      if (plane!.moduleOptions?.length) {
        this.setState({
          moduleOptions: plane!.moduleOptions!,
          moduleOptionsCommonPrefix: `/Swagger/Specs/${plane!.name}/`,
        });
        await this.onModuleSelectionUpdate(null);
      } else {
        try {
          this.setState({
            loading: true,
          });
          const options = await specsApi.getModulesForPlane(plane!.name);
          this.setState((preState) => {
            const planes = preState.planes;
            const index = planes.findIndex((v) => v.name === plane!.name);
            planes[index].moduleOptions = options;
            return {
              ...preState,
              loading: false,
              planes: planes,
              moduleOptions: options,
              moduleOptionsCommonPrefix: `/Swagger/Specs/${plane!.name}/`,
            };
          });
          await this.onModuleSelectionUpdate(null);
        } catch (err: any) {
          console.error(err);
          this.setState({
            loading: false,
            invalidText: errorHandlerApi.getErrorMessage(err),
          });
        }
      }
    } else {
      this.setState({
        moduleOptions: [],
        moduleOptionsCommonPrefix: "",
      });
      await this.onModuleSelectionUpdate(null);
    }
  };

  onModuleSelectionUpdate = async (moduleValueUrl: string | null) => {
    if (this.state.selectedModule !== moduleValueUrl) {
      this.setState({
        selectedModule: moduleValueUrl,
      });
      await this.loadResourceProviders(moduleValueUrl);
    } else {
      this.setState({
        selectedModule: moduleValueUrl,
      });
    }
  };

  loadResourceProviders = async (moduleUrl: string | null) => {
    if (moduleUrl !== null) {
      try {
        this.setState({
          loading: true,
        });
        const options = await specsApi.getResourceProviders(moduleUrl);
        const selectedResourceProvider = options.length === 1 ? options[0] : null;
        this.setState({
          loading: false,
          resourceProviderOptions: options,
          resourceProviderOptionsCommonPrefix: `${moduleUrl}/ResourceProviders/`,
        });
        this.onResourceProviderUpdate(selectedResourceProvider);
      } catch (err: any) {
        console.error(err);
        this.setState({
          loading: false,
          invalidText: errorHandlerApi.getErrorMessage(err),
        });
      }
    } else {
      this.setState({
        resourceProviderOptions: [],
        resourceProviderOptionsCommonPrefix: "",
      });
      this.onResourceProviderUpdate(null);
    }
  };

  onResourceProviderUpdate = (resourceProviderUrl: string | null) => {
    if (this.state.selectedResourceProvider !== resourceProviderUrl) {
      this.setState({
        selectedResourceProvider: resourceProviderUrl,
      });
    } else {
      this.setState({
        selectedResourceProvider: resourceProviderUrl,
      });
    }
  };

  verifyCreate = () => {
    this.setState({ invalidText: undefined });
    let { workspaceName, selectedModule, selectedResourceProvider } = this.state;
    const { selectedPlane, planes, moduleOptionsCommonPrefix, resourceProviderOptionsCommonPrefix } = this.state;
    workspaceName = workspaceName.trim();
    if (workspaceName.length < 1) {
      this.setState({ invalidText: `'Workspace Name' is required.` });
      return undefined;
    }

    const plane = planes.find((v) => v.displayName === selectedPlane)?.name ?? null;
    if (plane === null) {
      this.setState({ invalidText: `Please select 'Plane'.` });
      return undefined;
    }

    selectedModule = selectedModule ? selectedModule.replace(moduleOptionsCommonPrefix, "") : null;
    if (selectedModule === null) {
      this.setState({ invalidText: `Please select 'Module'.` });
      return undefined;
    }

    selectedResourceProvider = selectedResourceProvider
      ? selectedResourceProvider.replace(resourceProviderOptionsCommonPrefix, "")
      : null;
    if (selectedResourceProvider === null) {
      this.setState({ invalidText: `Please select 'Resource Provider'.` });
      return undefined;
    }
    let source = "OpenAPI";
    if (selectedResourceProvider.endsWith("/TypeSpec")) {
      selectedResourceProvider = selectedResourceProvider.replace("/TypeSpec", "");
      source = "TypeSpec";
    }
    return {
      name: workspaceName,
      plane: plane,
      modNames: selectedModule,
      resourceProvider: selectedResourceProvider,
      source: source,
    };
  };

  handleCreate = async () => {
    const data = this.verifyCreate();
    if (data === undefined) {
      return;
    }
    this.setState({ loading: true });
    try {
      const workspace = await workspaceApi.createWorkspace(data);
      this.setState({ loading: false });
      this.props.onClose(workspace);
    } catch (err: any) {
      console.error(err);
      this.setState({
        loading: false,
        invalidText: errorHandlerApi.getErrorMessage(err),
      });
    }
  };

  handleClose = () => {
    this.props.onClose(null);
  };

  render(): React.ReactNode {
    const { invalidText, loading, selectedPlane, selectedModule, selectedResourceProvider, workspaceName } = this.state;

    return (
      <Dialog open={this.props.openDialog} fullWidth={true} onClose={this.handleClose}>
        <DialogTitle>Create a new workspace</DialogTitle>
        <DialogContent>
          {invalidText && (
            <Alert variant="filled" severity="error">
              {" "}
              {invalidText}{" "}
            </Alert>
          )}
          <InputLabel shrink> API Specs</InputLabel>
          <Box
            sx={{
              mt: 1,
              mb: 1,
              marginLeft: 4,
              flexDirection: "column",
              display: "flex",
              alignItems: "stretch",
              justifyContent: "flex-start",
            }}
          >
            <SwaggerItemSelector
              name="Plane"
              commonPrefix=""
              options={this.state.planeOptions}
              value={selectedPlane}
              onValueUpdate={this.onPlaneSelectorUpdate}
            />
            <MiddlePadding />
            <SwaggerItemSelector
              name="Module"
              commonPrefix={this.state.moduleOptionsCommonPrefix}
              options={this.state.moduleOptions}
              value={selectedModule}
              onValueUpdate={this.onModuleSelectionUpdate}
            />
            <MiddlePadding />
            <SwaggerItemSelector
              name="Resource Provider"
              commonPrefix={this.state.resourceProviderOptionsCommonPrefix}
              options={this.state.resourceProviderOptions}
              value={selectedResourceProvider}
              onValueUpdate={this.onResourceProviderUpdate}
            />
          </Box>
          <TextField
            fullWidth={true}
            margin="normal"
            id="name"
            required
            value={workspaceName}
            onChange={(event: any) => {
              this.setState({
                workspaceName: event.target.value,
              });
            }}
            label="Workspace Name"
            type="text"
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Box>
            <Button onClick={this.handleClose}>Cancel</Button>
            <Button
              disabled={loading || !selectedPlane || !selectedModule || !selectedResourceProvider || !workspaceName}
              onClick={this.handleCreate}
              color="success"
            >
              Create
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    );
  }
}

const MiddlePadding = styled(Box)(() => ({
  height: "1.5vh",
}));

export default WorkspaceCreateDialog;
