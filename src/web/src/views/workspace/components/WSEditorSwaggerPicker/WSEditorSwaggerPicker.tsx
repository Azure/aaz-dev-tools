import * as React from "react";
import { useState, useEffect, useCallback } from "react";
import {
  Typography,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Button,
  Backdrop,
  CircularProgress,
  List,
  ListSubheader,
  ListItem,
  ListItemButton,
  ListItemIcon,
  Checkbox,
  ListItemText,
  Alert,
  Paper,
  InputBase,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { workspaceApi, specsApi, errorHandlerApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import AsyncOperationBanner from "../../../../components/AsyncOperationBanner";
import EditorPageLayout from "../../../../components/EditorPageLayout";
import { styled } from "@mui/material/styles";
import { getTypespecRPResources, getTypespecRPResourcesOperations } from "../../../../typespec";
import SwaggerItemSelector from "../../common/SwaggerItemSelector";
import { useResourceFilter } from "../../hooks/useResourceFilter";

interface WSEditorSwaggerPickerProps {
  workspaceName: string;
  plane: string;
  onClose: (updated: boolean) => void;
}

type ResourceVersionOperations = {
  [Named: string]: string;
};

type ResourceVersion = {
  version: string;
  operations: ResourceVersionOperations;
  file: string;
  id: string;
  path: string;
};

type Resource = {
  id: string;
  versions: ResourceVersion[];
  aazVersions: string[] | null;
};

type AAZResource = {
  id: string;
  versions: string[] | null;
};

type VersionResourceIdMap = {
  [version: string]: Resource[];
};

type ResourceInheritanceAAZVersionMap = {
  [id: string]: string | null;
};

type ResourceMap = {
  [id: string]: Resource;
};

const MiddlePadding = styled(Box)(() => ({
  height: "2vh",
}));

const MiddlePadding2 = styled(Box)(() => ({
  height: "8vh",
}));

const UpdateOptions = ["Default", "Generic(Get&Put) First", "Patch First", "No update command"];

const WSEditorSwaggerPicker = ({ workspaceName, plane, onClose }: WSEditorSwaggerPickerProps) => {
  const { filterText, updateFilter, filterResources } = useResourceFilter();

  const modulesLoader = useAsyncOperation(specsApi.getModulesForPlane);

  const [loading, setLoading] = useState(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [_defaultModule, setDefaultModule] = useState<string | null>(null);
  const [defaultResourceProvider, setDefaultResourceProvider] = useState<string | null>(null);
  const [defaultSource, setDefaultSource] = useState<string | null>(null);
  const [existingResources, setExistingResources] = useState<Set<string>>(new Set());
  const [moduleOptionsCommonPrefix, setModuleOptionsCommonPrefix] = useState("");
  const [resourceProviderOptionsCommonPrefix, setResourceProviderOptionsCommonPrefix] = useState("");
  const [moduleOptions, setModuleOptions] = useState<string[]>([]);
  const [versionOptions, setVersionOptions] = useState<string[]>([]);
  const [resourceProviderOptions, setResourceProviderOptions] = useState<string[]>([]);
  const [selectedResources, setSelectedResources] = useState<Set<string>>(new Set());
  const [selectedResourceInheritanceAAZVersionMap, setSelectedResourceInheritanceAAZVersionMap] =
    useState<ResourceInheritanceAAZVersionMap>({});
  const [preferredAAZVersion, setPreferredAAZVersion] = useState<string | null>(null);
  const [resourceOptions, setResourceOptions] = useState<Resource[]>([]);
  const [versionResourceIdMap, setVersionResourceIdMap] = useState<VersionResourceIdMap>({});
  const [resourceMap, setResourceMap] = useState<ResourceMap>({});
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [selectedResourceProvider, setSelectedResourceProvider] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
  const [updateOptions] = useState(UpdateOptions);
  const [updateOption, setUpdateOption] = useState(UpdateOptions[0]);

  useEffect(() => {
    const initializeComponent = async () => {
      await loadWorkspaceResources();

      try {
        const allModules = await modulesLoader.execute(plane);
        setModuleOptions(allModules || []);
        setModuleOptionsCommonPrefix(`/Swagger/Specs/${plane}/`);

        const swaggerDefault = await workspaceApi.getSwaggerDefault(workspaceName);
        if (swaggerDefault.modNames === null || swaggerDefault.modNames.length == 0) {
          return;
        }

        const moduleValueUrl = `/Swagger/Specs/${plane}/` + swaggerDefault.modNames.join("/");
        if (!allModules || allModules.findIndex((v) => v === moduleValueUrl) == -1) {
          return;
        }

        let rpUrl = null;
        if (swaggerDefault.rpName !== null && swaggerDefault.rpName.length > 0) {
          rpUrl = `${moduleValueUrl}/ResourceProviders/${swaggerDefault.rpName}`;
          if (swaggerDefault.source === "TypeSpec") {
            rpUrl += `/TypeSpec`;
          }
        }

        setDefaultModule(moduleValueUrl);
        setDefaultSource(swaggerDefault.source);
        setSelectedModule(moduleValueUrl);
        setModuleOptions([moduleValueUrl]);
        await loadResourceProviders(moduleValueUrl, rpUrl, swaggerDefault.source);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
      }
    };

    initializeComponent();
  }, []);

  const handleClose = useCallback(() => {
    onClose(false);
  }, [onClose]);

  const loadResourceProviders = useCallback(
    async (moduleUrl: string | null, preferredRP: string | null, sourceOverride?: string) => {
      if (moduleUrl != null) {
        try {
          const typeParam = sourceOverride ?? defaultSource ?? undefined;
          let options = await specsApi.getResourceProvidersWithType(moduleUrl, typeParam);
          let selectedResourceProvider = options.length === 1 ? options[0] : null;
          let defaultResourceProviderVal = null;
          if (preferredRP !== null && options.findIndex((v) => v === preferredRP) >= 0) {
            selectedResourceProvider = preferredRP;
            defaultResourceProviderVal = preferredRP;
            options = [preferredRP];
          }
          setDefaultResourceProvider(defaultResourceProviderVal);
          setResourceProviderOptions(options);
          setResourceProviderOptionsCommonPrefix(`${moduleUrl}/ResourceProviders/`);
          setSelectedResourceProvider(selectedResourceProvider);
        } catch (err: any) {
          console.error(err);
          const message = errorHandlerApi.getErrorMessage(err);
          setInvalidText(`ResponseError: ${message}`);
        }
      } else {
        setResourceProviderOptions([]);
        setSelectedResourceProvider(null);
        setVersionOptions([]);
        setResourceOptions([]);
        setSelectedVersion(null);
      }
    },
    [defaultSource],
  );

  const loadWorkspaceResources = useCallback(async () => {
    try {
      const resources = await workspaceApi.getWorkspaceResourcesByName(workspaceName);
      const existingResourcesSet = new Set<string>();
      if (resources && Array.isArray(resources) && resources.length > 0) {
        resources.forEach((resource: any) => {
          existingResourcesSet.add(resource.id);
        });
      }
      setExistingResources(existingResourcesSet);
    } catch (err: any) {
      console.error(err);
      const message = errorHandlerApi.getErrorMessage(err);
      setInvalidText(`ResponseError: ${message}`);
    }
  }, [workspaceName]);

  const loadResources = useCallback(
    async (resourceProviderUrl: string | null) => {
      if (resourceProviderUrl != null) {
        setInvalidText(undefined);
        setLoading(true);
        let data;
        if (resourceProviderUrl.endsWith("/TypeSpec")) {
          try {
            data = await getTypespecRPResources(resourceProviderUrl);
          } catch (err: any) {
            console.error(err);
            const message = errorHandlerApi.getErrorMessage(err);
            setInvalidText(`ResponseError: ${message}`);
            setLoading(false);
            return;
          }
        } else {
          try {
            data = await specsApi.getProviderResources(resourceProviderUrl);
          } catch (err: any) {
            console.error(err);
            const message = errorHandlerApi.getErrorMessage(err);
            setInvalidText(`ResponseError: ${message}`);
            setLoading(false);
            return;
          }
        }
        try {
          if (!data || !Array.isArray(data)) {
            setInvalidText("No resources found or invalid data format");
            setLoading(false);
            return;
          }
          const versionResourceIdMapLocal: VersionResourceIdMap = {};
          const versionOptionsLocal: string[] = [];
          const resourceMapLocal: ResourceMap = {};
          const resourceIdList: string[] = [];
          data.forEach((resource: Resource) => {
            resourceIdList.push(resource.id);
            resourceMapLocal[resource.id] = resource;
            resourceMapLocal[resource.id].aazVersions = null;

            const resourceVersions = resource.versions.map((v) => v.version);
            resourceVersions.forEach((v) => {
              if (!(v in versionResourceIdMapLocal)) {
                versionResourceIdMapLocal[v] = [];
                versionOptionsLocal.push(v);
              }
              versionResourceIdMapLocal[v].push(resource);
            });
          });
          versionOptionsLocal.sort((a, b) => a.localeCompare(b)).reverse();
          let selectVersion = null;
          if (versionOptionsLocal.length > 0) {
            selectVersion = versionOptionsLocal[0];
          }

          const filterData = await specsApi.filterResourcesByPlane(plane, resourceIdList);
          filterData.resources.forEach((aazResource: AAZResource) => {
            if (aazResource.versions) {
              resourceMapLocal[aazResource.id].aazVersions = aazResource.versions;
            }
          });
          setLoading(false);
          setVersionResourceIdMap(versionResourceIdMapLocal);
          setResourceMap(resourceMapLocal);
          setVersionOptions(versionOptionsLocal);

          if (
            selectVersion != null &&
            versionResourceIdMapLocal[selectVersion] &&
            Array.isArray(versionResourceIdMapLocal[selectVersion])
          ) {
            const newResourceOptions = [...versionResourceIdMapLocal[selectVersion]]
              .sort((a, b) => a.id.localeCompare(b.id))
              .filter((r) => !existingResources.has(r.id));
            setResourceOptions(newResourceOptions);
            setSelectedVersion(selectVersion);
            setPreferredAAZVersion(selectVersion);
            setSelectedResources(new Set());
            setSelectedResourceInheritanceAAZVersionMap({});
          }
        } catch (err: any) {
          console.error(err);
          setInvalidText(errorHandlerApi.getErrorMessage(err));
          setLoading(false);
        }
      } else {
        setVersionOptions([]);
        onVersionUpdate(null);
      }
    },
    [plane, existingResources],
  );

  useEffect(() => {
    if (selectedResourceProvider) {
      loadResources(selectedResourceProvider);
    } else {
      setVersionOptions([]);
      setResourceOptions([]);
      setSelectedVersion(null);
    }
  }, [selectedResourceProvider, loadResources]);

  const addSwagger = useCallback(async () => {
    if (!selectedModule || !selectedVersion || selectedResources.size < 1) {
      console.warn("Cannot submit: missing required values", {
        selectedModule,
        selectedVersion,
        selectedResourcesSize: selectedResources.size,
      });
      return;
    }

    const resources: { id: string; options: { update_by?: string; aaz_version: string | null } }[] = [];
    const resourceOptionMap: { [key: string]: { update_by?: string; aaz_version: string | null } } = {};
    selectedResources.forEach((resourceId: string) => {
      const res: any = {
        id: resourceId,
        options: {
          aaz_version: selectedResourceInheritanceAAZVersionMap[resourceId],
        },
      };
      if (updateOption === UpdateOptions[1]) {
        const resource = resourceMap[resourceId];
        const operations = resource.versions.find((v: any) => v.version === selectedVersion)?.operations;
        if (operations) {
          let hasGet = false;
          let hasPut = false;
          for (const opName in operations) {
            if (operations[opName].toLowerCase() === "put") {
              hasPut = true;
            } else if (operations[opName].toLowerCase() === "get") {
              hasGet = true;
            }
          }
          if (hasGet && hasPut) {
            res.options.update_by = "GenericOnly";
          }
        }
      } else if (updateOption === UpdateOptions[2]) {
        const resource = resourceMap[resourceId];
        const operations = resource.versions.find((v: any) => v.version === selectedVersion)?.operations;
        if (operations) {
          for (const opName in operations) {
            if (operations[opName].toLowerCase() === "patch") {
              res.options.update_by = "PatchOnly";
              break;
            }
          }
        }
      } else if (updateOption === UpdateOptions[3]) {
        res.options.update_by = "None";
      }
      resourceOptionMap[resourceId] = res.options;
      resources.push(res);
    });

    const requestBody = {
      module: selectedModule.replace(moduleOptionsCommonPrefix, ""),
      version: selectedVersion,
      resources: resources,
    };

    setInvalidText(undefined);
    setLoading(true);

    if (defaultResourceProvider?.endsWith("TypeSpec")) {
      const requestEmitterObj = JSON.parse(JSON.stringify(requestBody));
      requestEmitterObj.resourceProviderUrl = defaultResourceProvider;
      console.log("requestEmitterObj: ", requestEmitterObj);
      try {
        const res = await getTypespecRPResourcesOperations(requestEmitterObj);
        console.log("emitter getTypespecRPResourceOperations res: ", res);
        console.log("resourceOptionMap: ", resourceOptionMap);
        const addTypespecData = {
          version: selectedVersion,
          resources: res.map((item: { id: string; [key: string]: any }) => {
            if (item.id in resourceOptionMap) {
              item.options = resourceOptionMap[item.id];
            }
            return item;
          }),
        };
        console.log("addTypespec data: ", addTypespecData);
        try {
          await workspaceApi.addTypespecResources(workspaceName, addTypespecData);
          setLoading(false);
          onClose(true);
        } catch (err: any) {
          console.error(err);
          setLoading(false);
          onClose(false);
          const message = errorHandlerApi.getErrorMessage(err);
          setInvalidText(`ResponseError: ${message}`);
        }
      } catch (err: any) {
        setLoading(false);
        onClose(true);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
      }
    } else {
      try {
        await workspaceApi.addSwaggerResources(workspaceName, requestBody);
        setLoading(false);
        onClose(true);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
      }
    }
  }, [
    selectedResources,
    selectedVersion,
    selectedModule,
    moduleOptionsCommonPrefix,
    updateOption,
    resourceMap,
    selectedResourceInheritanceAAZVersionMap,
    defaultResourceProvider,
    workspaceName,
    onClose,
  ]);

  const handleSubmit = useCallback(() => {
    addSwagger();
  }, [addSwagger]);

  const onModuleSelectorUpdate = useCallback(
    async (moduleValueUrl: string | null) => {
      if (selectedModule !== moduleValueUrl) {
        setSelectedModule(moduleValueUrl);
        await loadResourceProviders(moduleValueUrl, null);
      } else {
        setSelectedModule(moduleValueUrl);
      }
    },
    [selectedModule, loadResourceProviders],
  );

  const onResourceProviderUpdate = useCallback(
    async (resourceProviderUrl: string | null) => {
      if (selectedResourceProvider !== resourceProviderUrl) {
        setSelectedResourceProvider(resourceProviderUrl);
        await loadResources(resourceProviderUrl);
      } else {
        setSelectedResourceProvider(resourceProviderUrl);
      }
    },
    [selectedResourceProvider, loadResources],
  );

  const onVersionUpdate = useCallback(
    (version: string | null) => {
      let newSelectedResources = selectedResources;
      let newResourceOptions: Resource[] = [];
      let newSelectedResourceInheritanceAAZVersionMap = selectedResourceInheritanceAAZVersionMap;

      if (version != null && versionResourceIdMap[version] && Array.isArray(versionResourceIdMap[version])) {
        newSelectedResources = new Set();
        newSelectedResourceInheritanceAAZVersionMap = {};
        newResourceOptions = [...versionResourceIdMap[version]]
          .sort((a, b) => a.id.localeCompare(b.id))
          .filter((r) => !existingResources.has(r.id));
        newResourceOptions.forEach((r) => {
          if (selectedResources.has(r.id)) {
            newSelectedResources.add(r.id);
            if (r.aazVersions && r.aazVersions.findIndex((v: string) => v === version) >= 0) {
              newSelectedResourceInheritanceAAZVersionMap[r.id] = version;
            } else {
              newSelectedResourceInheritanceAAZVersionMap[r.id] = selectedResourceInheritanceAAZVersionMap[r.id];
            }
          }
        });
      }

      setResourceOptions(newResourceOptions);
      setSelectedVersion(version);
      setPreferredAAZVersion(version);
      setSelectedResources(newSelectedResources);
      setSelectedResourceInheritanceAAZVersionMap(newSelectedResourceInheritanceAAZVersionMap);
    },
    [selectedResources, selectedResourceInheritanceAAZVersionMap, versionResourceIdMap, existingResources],
  );

  const onUpdateOptionUpdate = useCallback((updateOption: string | null) => {
    setUpdateOption(updateOption ?? UpdateOptions[0]);
  }, []);

  const onResourceItemClick = useCallback(
    (resourceId: string) => {
      return () => {
        const newSelectedResources = new Set(selectedResources);
        const newSelectedResourceInheritanceAAZVersionMap = { ...selectedResourceInheritanceAAZVersionMap };

        if (newSelectedResources.has(resourceId)) {
          newSelectedResources.delete(resourceId);
          delete newSelectedResourceInheritanceAAZVersionMap[resourceId];
        } else if (!existingResources.has(resourceId)) {
          newSelectedResources.add(resourceId);
          const aazVersions = resourceMap[resourceId].aazVersions;
          let inheritanceAAZVersion = null;
          if (aazVersions) {
            if (aazVersions.findIndex((v: string) => v === preferredAAZVersion) >= 0) {
              inheritanceAAZVersion = preferredAAZVersion;
            } else {
              inheritanceAAZVersion = aazVersions[0];
            }
          }
          newSelectedResourceInheritanceAAZVersionMap[resourceId] = inheritanceAAZVersion;
        }

        setSelectedResources(newSelectedResources);
        setSelectedResourceInheritanceAAZVersionMap(newSelectedResourceInheritanceAAZVersionMap);
      };
    },
    [selectedResources, selectedResourceInheritanceAAZVersionMap, existingResources, resourceMap, preferredAAZVersion],
  );

  const onSelectedAllClick = useCallback(() => {
    const newSelectedResources = new Set(selectedResources);
    let newSelectedResourceInheritanceAAZVersionMap = { ...selectedResourceInheritanceAAZVersionMap };
    if (newSelectedResources.size === resourceOptions.length) {
      newSelectedResources.clear();
      newSelectedResourceInheritanceAAZVersionMap = {};
    } else {
      resourceOptions.forEach((r) => {
        newSelectedResources.add(r.id);
        const aazVersions = resourceMap[r.id].aazVersions;
        let inheritanceAAZVersion = null;
        if (aazVersions) {
          if (aazVersions.findIndex((v: string) => v === preferredAAZVersion) >= 0) {
            inheritanceAAZVersion = preferredAAZVersion;
          } else {
            inheritanceAAZVersion = aazVersions[0];
          }
        }
        newSelectedResourceInheritanceAAZVersionMap[r.id] = inheritanceAAZVersion;
      });
    }

    setSelectedResources(newSelectedResources);
    setSelectedResourceInheritanceAAZVersionMap(newSelectedResourceInheritanceAAZVersionMap);
  }, [selectedResources, selectedResourceInheritanceAAZVersionMap, resourceOptions, resourceMap, preferredAAZVersion]);

  const onResourceInheritanceAAZVersionUpdate = useCallback(
    (resourceId: string, aazVersion: string | null) => {
      const newSelectedResourceInheritanceAAZVersionMap = { ...selectedResourceInheritanceAAZVersionMap };
      newSelectedResourceInheritanceAAZVersionMap[resourceId] = aazVersion;
      let newPreferredAAZVersion = preferredAAZVersion;
      if (aazVersion !== null) {
        newPreferredAAZVersion = aazVersion;
      }

      setSelectedResourceInheritanceAAZVersionMap(newSelectedResourceInheritanceAAZVersionMap);
      setPreferredAAZVersion(newPreferredAAZVersion);
    },
    [selectedResourceInheritanceAAZVersionMap, preferredAAZVersion],
  );

  return (
    <React.Fragment>
      <AppBar sx={{ position: "fixed" }}>
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={handleClose} aria-label="close">
            <CloseIcon />
          </IconButton>
          <Typography
            sx={{
              ml: 2,
              flex: 1,
              flexDirection: "row",
              display: "flex",
              justifyContent: "center",
              alignContent: "center",
            }}
            variant="h5"
            component="div"
          >
            Add Resources
          </Typography>
        </Toolbar>
      </AppBar>
      <EditorPageLayout>
        <Box
          sx={{
            flexShrink: 0,
            width: 250,
            flexDirection: "column",
            display: "flex",
            alignItems: "stretch",
            justifyContent: "flex-start",
            marginRight: "3vh",
          }}
        >
          <ListSubheader> Swagger Filters</ListSubheader>
          <MiddlePadding />
          <AsyncOperationBanner operation={modulesLoader} />
          <SwaggerItemSelector
            name="Swagger Module"
            commonPrefix={moduleOptionsCommonPrefix}
            options={moduleOptions}
            value={selectedModule}
            onValueUpdate={onModuleSelectorUpdate}
          />
          <MiddlePadding />
          <SwaggerItemSelector
            name="Resource Provider"
            commonPrefix={resourceProviderOptionsCommonPrefix}
            options={resourceProviderOptions}
            value={selectedResourceProvider}
            onValueUpdate={onResourceProviderUpdate}
          />
          <MiddlePadding />
          <SwaggerItemSelector
            name="API Version"
            commonPrefix=""
            options={versionOptions}
            value={selectedVersion}
            onValueUpdate={onVersionUpdate}
          />
          <MiddlePadding2 />
          <SwaggerItemSelector
            name="Update Command Mode"
            commonPrefix=""
            options={updateOptions}
            value={updateOption}
            onValueUpdate={onUpdateOptionUpdate}
          />
          <MiddlePadding2 />

          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={selectedModule === null || selectedVersion === null || selectedResources.size < 1}
          >
            Submit
          </Button>
        </Box>
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
                <Typography component="h6">Resource Url</Typography>

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
                  <ListItemButton
                    sx={{ maxWidth: 180 }}
                    dense
                    onClick={onSelectedAllClick}
                    disabled={resourceOptions.length === 0}
                  >
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
                  <InputBase
                    sx={{ flex: 1 }}
                    placeholder="Filter by keywords"
                    inputProps={{ "aria-label": "Filter by keywords" }}
                    value={filterText}
                    onChange={(event: any) => {
                      updateFilter(event.target.value);
                    }}
                  />
                </Paper>
              </Box>
            </ListSubheader>
          }
        >
          {resourceOptions.length > 0 && (
            <Paper sx={{ ml: 2, mr: 2 }} variant="outlined" square>
              {filterResources(resourceOptions).map((option) => {
                const labelId = `resource-${option.id}`;
                const selected = selectedResources.has(option.id);
                const inheritanceOptions = resourceMap[option.id]?.aazVersions;
                let selectedInheritance = null;
                if (selectedResourceInheritanceAAZVersionMap !== null) {
                  selectedInheritance = selectedResourceInheritanceAAZVersionMap[option.id];
                }
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
                          checked={selected || existingResources.has(option.id)}
                          tabIndex={-1}
                          disableRipple
                          inputProps={{ "aria-labelledby": labelId }}
                        />
                      </ListItemIcon>
                      <ListItemText
                        id={labelId}
                        primary={option.id}
                        primaryTypographyProps={{
                          variant: "h6",
                        }}
                      />
                    </ListItemButton>
                    {selected && (
                      <FormControl sx={{ m: 1, minWidth: 120 }}>
                        <InputLabel id={`${labelId}-inheritance-select-label`}>Inheritance</InputLabel>
                        <Select
                          id={`${labelId}-inheritance-select`}
                          value={selectedInheritance === null ? "_NULL_" : selectedInheritance}
                          onChange={(event) => {
                            onResourceInheritanceAAZVersionUpdate(
                              option.id,
                              event.target.value === "_NULL_" ? null : event.target.value,
                            );
                          }}
                          size="small"
                        >
                          <MenuItem value="_NULL_" key={`${labelId}-inheritance-select-null`}>
                            None
                          </MenuItem>
                          {inheritanceOptions &&
                            inheritanceOptions.map((inheritanceOption: string) => {
                              return (
                                <MenuItem
                                  value={inheritanceOption}
                                  key={`${labelId}-inheritance-select-${inheritanceOption}`}
                                >
                                  {inheritanceOption}
                                </MenuItem>
                              );
                            })}
                        </Select>
                        <FormHelperText>Inherit modification from exported command models in aaz</FormHelperText>
                      </FormControl>
                    )}
                  </ListItem>
                );
              })}
            </Paper>
          )}
        </List>
      </EditorPageLayout>
      <Backdrop sx={{ color: "#fff", zIndex: (theme: any) => theme.zIndex.drawer + 1 }} open={loading}>
        {invalidText !== undefined && (
          <Alert
            sx={{
              maxWidth: "80%",
              display: "flex",
              flexDirection: "column",
              alignItems: "stretch",
              justifyContent: "flex-start",
            }}
            variant="filled"
            severity="error"
            onClose={() => {
              setInvalidText(undefined);
              setLoading(false);
            }}
          >
            {invalidText}
          </Alert>
        )}
        {invalidText === undefined && <CircularProgress color="inherit" />}
      </Backdrop>
    </React.Fragment>
  );
};

export default WSEditorSwaggerPicker;
