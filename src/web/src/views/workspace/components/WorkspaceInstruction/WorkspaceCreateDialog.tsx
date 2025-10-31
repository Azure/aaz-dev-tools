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
import React, { useState, useEffect, useCallback } from "react";
import SwaggerItemSelector from "../../common/SwaggerItemSelector";
import styled from "@emotion/styled";
import { workspaceApi, specsApi, errorHandlerApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import AsyncOperationBanner from "../../../../components/AsyncOperationBanner";
import type { Plane } from "../../interfaces";

interface WorkspaceCreateDialogProps {
  openDialog: boolean;
  name: string;
  onClose: (value: any | null) => void;
}

const WorkspaceCreateDialog: React.FC<WorkspaceCreateDialogProps> = ({ openDialog, name, onClose }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [workspaceName, setWorkspaceName] = useState<string>(name);

  const modulesLoader = useAsyncOperation(specsApi.getModulesForPlane);

  const [planes, setPlanes] = useState<Plane[]>([]);
  const [planeOptions, setPlaneOptions] = useState<string[]>([]);
  const [selectedPlane, setSelectedPlane] = useState<string | null>(null);

  const [moduleOptions, setModuleOptions] = useState<string[]>([]);
  const [moduleOptionsCommonPrefix, setModuleOptionsCommonPrefix] = useState<string>("");
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  const [resourceProviderOptions, setResourceProviderOptions] = useState<string[]>([]);
  const [resourceProviderOptionsCommonPrefix, setResourceProviderOptionsCommonPrefix] = useState<string>("");
  const [selectedResourceProvider, setSelectedResourceProvider] = useState<string | null>(null);

  useEffect(() => {
    loadPlanes();
  }, []);

  const loadPlanes = useCallback(async () => {
    try {
      setLoading(true);

      const planesData = await specsApi.getPlanes();
      const planeOptionsData: string[] = planesData.map((v) => v.displayName);
      setPlanes(planesData);
      setPlaneOptions(planeOptionsData);
      setLoading(false);
      if (planeOptionsData.length > 0) {
        await onPlaneSelectorUpdateWithData(planeOptionsData[0], planesData);
      }
    } catch (err: any) {
      console.error(err);
      setLoading(false);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
    }
  }, []);

  const onPlaneSelectorUpdateWithData = useCallback(
    async (planeDisplayName: string | null, freshPlanesData: Plane[]) => {
      const plane = freshPlanesData.find((v: Plane) => v.displayName === planeDisplayName) ?? null;

      if (selectedPlane !== (plane?.displayName ?? null)) {
        if (!plane) {
          return;
        }
        setSelectedPlane(plane?.displayName ?? null);
        await loadSwaggerModules(plane);
      } else {
        setSelectedPlane(plane?.displayName ?? null);
      }
    },
    [selectedPlane],
  );

  const onPlaneSelectorUpdate = useCallback(
    async (planeDisplayName: string | null) => {
      const plane = planes.find((v: Plane) => v.displayName === planeDisplayName) ?? null;

      if (selectedPlane !== (plane?.displayName ?? null)) {
        if (!plane) {
          return;
        }
        setSelectedPlane(plane?.displayName ?? null);
        await loadSwaggerModules(plane);
      } else {
        setSelectedPlane(plane?.displayName ?? null);
      }
    },
    [planes, selectedPlane],
  );

  const loadSwaggerModules = useCallback(async (plane: Plane | null) => {
    if (plane !== null) {
      if (plane.moduleOptions?.length) {
        setModuleOptions(plane.moduleOptions);
        setModuleOptionsCommonPrefix(`/Swagger/Specs/${plane.name}/`);
        await onModuleSelectionUpdate(null);
      } else {
        try {
          const options = await modulesLoader.execute(plane.name);
          setPlanes((prevPlanes) => {
            const updatedPlanes = [...prevPlanes];
            const index = updatedPlanes.findIndex((v: Plane) => v.name === plane.name);
            updatedPlanes[index].moduleOptions = options || [];
            return updatedPlanes;
          });
          setModuleOptions(options || []);
          setModuleOptionsCommonPrefix(`/Swagger/Specs/${plane.name}/`);
          await onModuleSelectionUpdate(null);
        } catch (err: any) {
          console.error(err);
          setInvalidText(errorHandlerApi.getErrorMessage(err));
        }
      }
    } else {
      setModuleOptions([]);
      setModuleOptionsCommonPrefix("");
      await onModuleSelectionUpdate(null);
    }
  }, []);

  const onModuleSelectionUpdate = useCallback(
    async (moduleValueUrl: string | null) => {
      if (selectedModule !== moduleValueUrl) {
        setSelectedModule(moduleValueUrl);
        await loadResourceProviders(moduleValueUrl);
      } else {
        setSelectedModule(moduleValueUrl);
      }
    },
    [selectedModule],
  );

  const loadResourceProviders = useCallback(async (moduleUrl: string | null) => {
    if (moduleUrl !== null) {
      try {
        setLoading(true);
        const options = await specsApi.getResourceProviders(moduleUrl);
        const selectedResourceProviderData = options.length === 1 ? options[0] : null;
        setLoading(false);
        setResourceProviderOptions(options);
        setResourceProviderOptionsCommonPrefix(`${moduleUrl}/ResourceProviders/`);
        onResourceProviderUpdate(selectedResourceProviderData);
      } catch (err: any) {
        console.error(err);
        setLoading(false);
        setInvalidText(errorHandlerApi.getErrorMessage(err));
      }
    } else {
      setResourceProviderOptions([]);
      setResourceProviderOptionsCommonPrefix("");
      onResourceProviderUpdate(null);
    }
  }, []);

  const onResourceProviderUpdate = useCallback(
    (resourceProviderUrl: string | null) => {
      if (selectedResourceProvider !== resourceProviderUrl) {
        setSelectedResourceProvider(resourceProviderUrl);
      } else {
        setSelectedResourceProvider(resourceProviderUrl);
      }
    },
    [selectedResourceProvider],
  );

  const verifyCreate = useCallback(() => {
    setInvalidText(undefined);
    let wsName = workspaceName.trim();
    let selModule = selectedModule;
    let selResourceProvider = selectedResourceProvider;

    if (wsName.length < 1) {
      setInvalidText(`'Workspace Name' is required.`);
      return undefined;
    }

    const plane = planes.find((v: Plane) => v.displayName === selectedPlane)?.name ?? null;
    if (plane === null) {
      setInvalidText(`Please select 'Plane'.`);
      return undefined;
    }

    selModule = selModule ? selModule.replace(moduleOptionsCommonPrefix, "") : null;
    if (selModule === null) {
      setInvalidText(`Please select 'Module'.`);
      return undefined;
    }

    selResourceProvider = selResourceProvider
      ? selResourceProvider.replace(resourceProviderOptionsCommonPrefix, "")
      : null;
    if (selResourceProvider === null) {
      setInvalidText(`Please select 'Resource Provider'.`);
      return undefined;
    }
    let source = "OpenAPI";
    if (selResourceProvider.endsWith("/TypeSpec")) {
      selResourceProvider = selResourceProvider.replace("/TypeSpec", "");
      source = "TypeSpec";
    }
    return {
      name: wsName,
      plane: plane,
      modNames: selModule,
      resourceProvider: selResourceProvider,
      source: source,
    };
  }, [
    workspaceName,
    selectedModule,
    selectedResourceProvider,
    planes,
    selectedPlane,
    moduleOptionsCommonPrefix,
    resourceProviderOptionsCommonPrefix,
  ]);

  const handleCreate = useCallback(async () => {
    const data = verifyCreate();
    if (data === undefined) {
      return;
    }
    setLoading(true);
    try {
      const workspace = await workspaceApi.createWorkspace(data);
      setLoading(false);
      onClose(workspace);
    } catch (err: any) {
      console.error(err);
      setLoading(false);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
    }
  }, [verifyCreate, onClose]);

  const handleClose = useCallback(() => {
    onClose(null);
  }, [onClose]);

  return (
    <Dialog open={openDialog} fullWidth={true} onClose={handleClose}>
      <DialogTitle>Create a new workspace</DialogTitle>
      <DialogContent>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <AsyncOperationBanner operation={modulesLoader} />
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
            options={planeOptions}
            value={selectedPlane}
            onValueUpdate={onPlaneSelectorUpdate}
          />
          <MiddlePadding />
          <SwaggerItemSelector
            name="Module"
            commonPrefix={moduleOptionsCommonPrefix}
            options={moduleOptions}
            value={selectedModule}
            onValueUpdate={onModuleSelectionUpdate}
          />
          <MiddlePadding />
          <SwaggerItemSelector
            name="Resource Provider"
            commonPrefix={resourceProviderOptionsCommonPrefix}
            options={resourceProviderOptions}
            value={selectedResourceProvider}
            onValueUpdate={onResourceProviderUpdate}
          />
        </Box>
        <TextField
          fullWidth={true}
          margin="normal"
          id="name"
          required
          value={workspaceName}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
            setWorkspaceName(event.target.value);
          }}
          label="Workspace Name"
          type="text"
          variant="standard"
        />
      </DialogContent>
      <DialogActions>
        <Box>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            disabled={
              loading ||
              modulesLoader.loading ||
              !selectedPlane ||
              !selectedModule ||
              !selectedResourceProvider ||
              !workspaceName
            }
            onClick={handleCreate}
            color="success"
          >
            Create
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

const MiddlePadding = styled(Box)(() => ({
  height: "1.5vh",
}));

export default WorkspaceCreateDialog;
