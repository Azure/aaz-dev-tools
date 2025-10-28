import * as React from "react";
import { useState, useEffect, useCallback } from "react";
import {
  styled,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Button,
  Paper,
  TextField,
  Alert,
  InputLabel,
  IconButton,
  Input,
  Typography,
  TypographyProps,
  Tabs,
  Tab,
} from "@mui/material";
import { workspaceApi, specsApi, errorHandlerApi } from "../../../../services";
import DoDisturbOnRoundedIcon from "@mui/icons-material/DoDisturbOnRounded";
import AddCircleRoundedIcon from "@mui/icons-material/AddCircleRounded";
import SwaggerItemSelector from "../../common/SwaggerItemSelector";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import type { Plane, Resource } from "../../interfaces";

interface WSEditorClientConfigDialogProps {
  workspaceUrl: string;
  open: boolean;
  onClose: (updated: boolean) => void;
}

interface SwaggerVersionResourceIdMap {
  [version: string]: string[];
}

interface ClientEndpointResource {
  plane: string;
  module: string;
  version: string;
  id: string;
  subresource: string;
}

const AuthTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 400,
}));

const TemplateSuffixTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 18,
  fontWeight: 500,
}));

const MiddlePadding = styled(Box)(() => ({
  height: "1.5vh",
}));

const WSEditorClientConfigDialog: React.FC<WSEditorClientConfigDialogProps> = ({ workspaceUrl, open, onClose }) => {
  const [updating, setUpdating] = useState(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [isAdd, setIsAdd] = useState(true);

  const [endpointType, setEndpointType] = useState<"template" | "http-operation">("template");

  const [templateAzureCloud, setTemplateAzureCloud] = useState("");
  const [templateAzureChinaCloud, setTemplateAzureChinaCloud] = useState("");
  const [templateAzureUSGovernment, setTemplateAzureUSGovernment] = useState("");
  const [templateAzureGermanCloud, setTemplateAzureGermanCloud] = useState("");
  const [cloudMetadataSelectorIndex, setCloudMetadataSelectorIndex] = useState("");
  const [cloudMetadataPrefixTemplate, setCloudMetadataPrefixTemplate] = useState("");

  const [aadAuthScopes, setAadAuthScopes] = useState<string[]>([""]);

  const [selectedPlane, setSelectedPlane] = useState<string | null>(null);

  const [moduleOptions, setModuleOptions] = useState<string[]>([]);
  const [moduleOptionsCommonPrefix, setModuleOptionsCommonPrefix] = useState("");
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  const [resourceProviderOptions, setResourceProviderOptions] = useState<string[]>([]);
  const [resourceProviderOptionsCommonPrefix, setResourceProviderOptionsCommonPrefix] = useState("");
  const [selectedResourceProvider, setSelectedResourceProvider] = useState<string | null>(null);

  const [versionOptions, setVersionOptions] = useState<string[]>([]);
  const [versionResourceIdMap, setVersionResourceIdMap] = useState<SwaggerVersionResourceIdMap>({});
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);

  const [resourceIdOptions, setResourceIdOptions] = useState<string[]>([]);
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);
  const [subresource, setSubresource] = useState("");

  const loadPlanes = useCallback(async () => {
    try {
      setUpdating(true);

      const planesData = await specsApi.getPlanes();
      setUpdating(false);

      if (planesData.length > 0) {
        const firstPlane = planesData[0];
        setSelectedPlane(firstPlane.displayName);
        await loadSwaggerModules(firstPlane);
      }
    } catch (err: any) {
      console.error(err);
      const message = errorHandlerApi.getErrorMessage(err);
      setUpdating(false);
      setInvalidText(`ResponseError: ${message}`);
    }
  }, []);

  const loadSwaggerModules = useCallback(async (plane: Plane | null) => {
    if (plane !== null) {
      if (plane!.moduleOptions?.length) {
        setModuleOptions(plane!.moduleOptions!);
        setModuleOptionsCommonPrefix(`/Swagger/Specs/${plane!.name}/`);
        await onModuleSelectionUpdate(null);
      } else {
        try {
          setUpdating(true);
          const options = await specsApi.getSwaggerModules(plane!.name);
          setUpdating(false);
          setModuleOptions(options);
          setModuleOptionsCommonPrefix(`/Swagger/Specs/${plane!.name}/`);
          await onModuleSelectionUpdate(null);
        } catch (err: any) {
          console.error(err);
          const message = errorHandlerApi.getErrorMessage(err);
          setUpdating(false);
          setInvalidText(`ResponseError: ${message}`);
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
        setUpdating(true);
        const options = await specsApi.getResourceProviders(moduleUrl);
        const selectedRP = options.length === 1 ? options[0] : null;
        setUpdating(false);
        setResourceProviderOptions(options);
        setResourceProviderOptionsCommonPrefix(`${moduleUrl}/ResourceProviders/`);
        onResourceProviderUpdate(selectedRP);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setUpdating(false);
        setInvalidText(`ResponseError: ${message}`);
      }
    } else {
      setResourceProviderOptions([]);
      setResourceProviderOptionsCommonPrefix("");
      onResourceProviderUpdate(null);
    }
  }, []);

  const onResourceProviderUpdate = useCallback(
    async (resourceProviderUrl: string | null) => {
      if (selectedResourceProvider !== resourceProviderUrl) {
        setSelectedResourceProvider(resourceProviderUrl);
        await loadResources(resourceProviderUrl, null);
      } else {
        setSelectedResourceProvider(resourceProviderUrl);
      }
    },
    [selectedResourceProvider],
  );

  const loadResources = useCallback(async (resourceProviderUrl: string | null, selectVersion: string | null) => {
    if (resourceProviderUrl != null) {
      setInvalidText(undefined);
      setUpdating(true);
      try {
        const resources = await specsApi.getProviderResources(resourceProviderUrl);
        const versionResIdMap: SwaggerVersionResourceIdMap = {};
        const versionOpts: string[] = [];
        const resourceIdList: string[] = [];
        resources.forEach((resource: any) => {
          resourceIdList.push(resource.id);
          const resourceVersions = resource.versions
            .filter((v: ResourceVersion) => {
              for (const key in v.operations) {
                if (v.operations[key].toUpperCase() === "GET") {
                  return true;
                }
              }
              return false;
            })
            .map((v: any) => v.version);
          resourceVersions.forEach((v: any) => {
            if (!(v in versionResIdMap)) {
              versionResIdMap[v] = [];
              versionOpts.push(v);
            }
            versionResIdMap[v].push(resource.id);
          });
        });
        versionOpts.sort((a, b) => a.localeCompare(b)).reverse();
        if (
          selectVersion === null &&
          (versionOpts.length === 0 || versionOpts.findIndex((v) => v === selectVersion) < 0)
        ) {
          selectVersion = null;
        }
        if (!selectVersion && versionOpts.length > 0) {
          selectVersion = versionOpts[0];
        }

        setUpdating(false);
        setVersionResourceIdMap(versionResIdMap);
        setVersionOptions(versionOpts);
        onVersionUpdate(selectVersion, versionResIdMap);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
      }
    } else {
      setVersionOptions([]);
      onVersionUpdate(null);
    }
  }, []);

  const onVersionUpdate = useCallback(
    (version: string | null, versionResIdMap?: SwaggerVersionResourceIdMap) => {
      const mapToUse = versionResIdMap || versionResourceIdMap;
      let newSelectedResourceId = selectedResourceId;
      let resourceIdOpts: string[] = [];
      if (version != null && mapToUse[version]) {
        resourceIdOpts = [...mapToUse[version]].sort((a, b) => a.toString().localeCompare(b.toString()));
        if (newSelectedResourceId !== null && resourceIdOpts.findIndex((v) => v === newSelectedResourceId) < 0) {
          newSelectedResourceId = null;
        }
      }
      setResourceIdOptions(resourceIdOpts);
      setSelectedVersion(version);
      setSelectedResourceId(newSelectedResourceId);
    },
    [selectedResourceId, versionResourceIdMap],
  );

  const loadWorkspaceClientConfig = useCallback(async () => {
    setUpdating(true);
    try {
      const clientConfigData = await workspaceApi.getClientConfig(workspaceUrl);
      const clientConfig: ClientConfig = {
        version: clientConfigData.version,
        auth: clientConfigData.auth,
      };
      let templateAzureCloudVal = "";
      let templateAzureChinaCloudVal = "";
      let templateAzureUSGovernmentVal = "";
      let templateAzureGermanCloudVal = "";
      let cloudMetadataSelectorIndexVal = "";
      let cloudMetadataPrefixTemplateVal = "";
      let endpointTypeVal: "template" | "http-operation" = "template";
      let selectedPlaneVal: string | null = null;
      let selectedModuleVal: string | null = null;
      let selectedResourceProviderVal: string | null = null;
      let selectedVersionVal: string | null = null;
      let selectedResourceIdVal: string | null = null;
      let subresourceVal: string = "";

      if (clientConfigData.endpoints.type === "template") {
        clientConfig.endpointTemplates = {};
        clientConfigData.endpoints.templates.forEach((value: any) => {
          clientConfig.endpointTemplates![value.cloud] = value.template;
        });
        clientConfig.endpointCloudMetadata = clientConfigData.endpoints.cloudMetadata;

        endpointTypeVal = "template";
        templateAzureCloudVal = clientConfig.endpointTemplates!["AzureCloud"] ?? "";
        templateAzureChinaCloudVal = clientConfig.endpointTemplates!["AzureChinaCloud"] ?? "";
        templateAzureUSGovernmentVal = clientConfig.endpointTemplates!["AzureUSGovernment"] ?? "";
        templateAzureGermanCloudVal = clientConfig.endpointTemplates!["AzureGermanCloud"] ?? "";
        cloudMetadataSelectorIndexVal = clientConfig.endpointCloudMetadata?.selectorIndex ?? "";
        cloudMetadataPrefixTemplateVal = clientConfig.endpointCloudMetadata?.prefixTemplate ?? "";
      } else if (clientConfigData.endpoints.type === "http-operation") {
        clientConfig.endpointResource = clientConfigData.endpoints.resource;
        const rpUrl: string = clientConfig.endpointResource!.swagger.split("/Paths/")[0];
        const moduleUrl: string = rpUrl.split("/ResourceProviders/")[0];
        const planeUrl: string = moduleUrl.split("/")[0];
        selectedResourceProviderVal = `/Swagger/Specs/${rpUrl}`;
        selectedModuleVal = `/Swagger/Specs/${moduleUrl}`;
        selectedPlaneVal = `/Swagger/Specs/${planeUrl}`;
        selectedVersionVal = clientConfig.endpointResource!.version;
        selectedResourceIdVal = clientConfig.endpointResource!.id;
        subresourceVal = clientConfig.endpointResource!.subresource ?? "";
        endpointTypeVal = "http-operation";
      }

      setAadAuthScopes(clientConfig.auth.aad.scopes ?? [""]);
      setEndpointType(endpointTypeVal);
      setTemplateAzureCloud(templateAzureCloudVal);
      setTemplateAzureChinaCloud(templateAzureChinaCloudVal);
      setTemplateAzureUSGovernment(templateAzureUSGovernmentVal);
      setTemplateAzureGermanCloud(templateAzureGermanCloudVal);
      setCloudMetadataSelectorIndex(cloudMetadataSelectorIndexVal);
      setCloudMetadataPrefixTemplate(cloudMetadataPrefixTemplateVal);
      setSelectedPlane(selectedPlaneVal);
      setSelectedModule(selectedModuleVal);
      setSelectedResourceProvider(selectedResourceProviderVal);
      setSelectedVersion(selectedVersionVal);
      setSelectedResourceId(selectedResourceIdVal);
      setSubresource(subresourceVal);
      setIsAdd(false);
    } catch (err: any) {
      if (errorHandlerApi.isHttpError(err, 404)) {
        setIsAdd(true);
      } else {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
      }
    }

    setUpdating(false);
  }, [workspaceUrl]);

  useEffect(() => {
    const initializeComponent = async () => {
      await loadPlanes();
      await loadWorkspaceClientConfig();
    };

    if (open) {
      initializeComponent();
    }
  }, [open, loadPlanes, loadWorkspaceClientConfig]);

  const handleClose = useCallback(() => {
    onClose(false);
  }, [onClose]);

  const handleUpdate = useCallback(async () => {
    let currentAadAuthScopes = [...aadAuthScopes];
    let templates: ClientEndpointTemplate[] | undefined = undefined;
    let resource: ClientEndpointResource | undefined = undefined;
    let cloudMetadata: ClientEndpointCloudMetadata | undefined = undefined;

    if (endpointType === "template") {
      let currentTemplateAzureCloud = templateAzureCloud.trim();
      if (currentTemplateAzureCloud.length < 1) {
        setInvalidText("Azure Cloud Endpoint Template is required.");
        return;
      }
      let currentTemplateAzureChinaCloud = templateAzureChinaCloud.trim();
      let currentTemplateAzureUSGovernment = templateAzureUSGovernment.trim();
      let currentTemplateAzureGermanCloud = templateAzureGermanCloud.trim();
      const templateRegex = /^https:\/\/((\{[a-zA-Z0-9]+\})|([^{}.]+))(.((\{[a-zA-Z0-9]+\})|([^{}.]+)))*(\/)?$/;
      if (!templateRegex.test(currentTemplateAzureCloud)) {
        setInvalidText("Azure Cloud Endpoint Template is invalid.");
        return;
      }

      if (currentTemplateAzureChinaCloud.length > 0 && !templateRegex.test(currentTemplateAzureChinaCloud)) {
        setInvalidText("Azure China Cloud Endpoint Template is invalid.");
        return;
      }

      if (currentTemplateAzureUSGovernment.length > 0 && !templateRegex.test(currentTemplateAzureUSGovernment)) {
        setInvalidText("Azure US Government Endpoint Template is invalid.");
        return;
      }

      if (currentTemplateAzureGermanCloud.length > 0 && !templateRegex.test(currentTemplateAzureGermanCloud)) {
        setInvalidText("Azure German Cloud Endpoint Template is invalid.");
        return;
      }

      templates = [{ cloud: "AzureCloud", template: currentTemplateAzureCloud }];
      if (currentTemplateAzureChinaCloud.length > 0) {
        templates.push({ cloud: "AzureChinaCloud", template: currentTemplateAzureChinaCloud });
      }
      if (currentTemplateAzureUSGovernment.length > 0) {
        templates.push({ cloud: "AzureUSGovernment", template: currentTemplateAzureUSGovernment });
      }
      if (currentTemplateAzureGermanCloud.length > 0) {
        templates.push({ cloud: "AzureGermanCloud", template: currentTemplateAzureGermanCloud });
      }

      let currentCloudMetadataSelectorIndex = cloudMetadataSelectorIndex.trim();
      let currentCloudMetadataPrefixTemplate = cloudMetadataPrefixTemplate.trim();
      if (currentCloudMetadataSelectorIndex.length < 1 && currentCloudMetadataPrefixTemplate.length > 0) {
        setInvalidText("Cloud Metadata Selector Index is required.");
        return;
      } else if (currentCloudMetadataSelectorIndex.length > 0) {
        cloudMetadata = {
          selectorIndex: currentCloudMetadataSelectorIndex,
        };
        if (currentCloudMetadataPrefixTemplate.length > 0) {
          if (!templateRegex.test(currentCloudMetadataPrefixTemplate)) {
            setInvalidText("Cloud Metadata Prefix is invalid.");
            return;
          }
          cloudMetadata.prefixTemplate = currentCloudMetadataPrefixTemplate;
        }
      }
    } else if (endpointType === "http-operation") {
      let currentSubresource = subresource;
      if (!selectedModule) {
        setInvalidText("Module is required.");
        return;
      }
      if (!selectedResourceProvider) {
        setInvalidText("Resource Provider is required.");
        return;
      }
      if (!selectedVersion) {
        setInvalidText("API Version is required.");
        return;
      }
      if (!selectedResourceId) {
        setInvalidText("Resource ID is required.");
        return;
      }
      currentSubresource = currentSubresource.trim();
      if (currentSubresource.length < 1) {
        setInvalidText("Endpoint Property Index is required.");
        return;
      }

      resource = {
        plane: selectedPlane?.replace("/Swagger/Specs/", "") ?? "",
        module: selectedModule.replace(moduleOptionsCommonPrefix, ""),
        version: selectedVersion,
        id: selectedResourceId,
        subresource: currentSubresource,
      };
    }

    currentAadAuthScopes = currentAadAuthScopes.map((scope) => scope.trim()).filter((scope) => scope.length > 0);
    if (currentAadAuthScopes.length < 1) {
      setInvalidText("MS Entra(AAD) Auth Scopes is required.");
      return;
    }

    const auth = {
      aad: {
        scopes: currentAadAuthScopes,
      },
    };

    onUpdateClientConfig(templates, cloudMetadata, resource, auth);
  }, [
    aadAuthScopes,
    endpointType,
    templateAzureCloud,
    templateAzureChinaCloud,
    templateAzureUSGovernment,
    templateAzureGermanCloud,
    cloudMetadataSelectorIndex,
    cloudMetadataPrefixTemplate,
    selectedPlane,
    selectedModule,
    selectedResourceProvider,
    selectedVersion,
    selectedResourceId,
    subresource,
    moduleOptionsCommonPrefix,
  ]);

  const onUpdateClientConfig = useCallback(
    async (
      templates: ClientEndpointTemplate[] | undefined,
      cloudMetadata: ClientEndpointCloudMetadata | undefined,
      resource: ClientEndpointResource | undefined,
      auth: ClientAuth,
    ) => {
      setUpdating(true);
      try {
        await workspaceApi.updateClientConfig(workspaceUrl, {
          templates: templates,
          cloudMetadata: cloudMetadata,
          resource: resource,
          auth: auth,
        });
        setUpdating(false);
        onClose(true);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
        setUpdating(false);
      }
    },
    [workspaceUrl, onClose],
  );

  const onRemoveAadScope = useCallback((idx: number) => {
    setAadAuthScopes((prev) => {
      const newScopes = [...prev.slice(0, idx), ...prev.slice(idx + 1)];
      if (newScopes.length === 0) {
        newScopes.push("");
      }
      return newScopes;
    });
  }, []);

  const onModifyAadScope = useCallback((scope: string, idx: number) => {
    setAadAuthScopes((prev) => [...prev.slice(0, idx), scope, ...prev.slice(idx + 1)]);
  }, []);

  const onAddAadScope = useCallback(() => {
    setAadAuthScopes((prev) => [...prev, ""]);
  }, []);

  const buildAadScopeInput = useCallback(
    (scope: string, idx: number) => {
      return (
        <Box
          key={idx}
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "flex-start",
            ml: 1,
          }}
        >
          <IconButton edge="start" color="inherit" onClick={() => onRemoveAadScope(idx)} aria-label="remove">
            <DoDisturbOnRoundedIcon fontSize="small" />
          </IconButton>
          <Input
            id={`aadScope-${idx}`}
            value={scope}
            onChange={(event: any) => {
              onModifyAadScope(event.target.value, idx);
            }}
            sx={{ flexGrow: 1 }}
            placeholder="Input Microsoft Entra(AAD) auth Scope here, e.g. https://metrics.monitor.azure.com/.default"
          />
        </Box>
      );
    },
    [onRemoveAadScope, onModifyAadScope],
  );

  return (
    <Dialog disableEscapeKeyDown fullWidth={true} maxWidth="md" open={open}>
      <DialogTitle>{isAdd ? "Setup Client Config" : "Modify Client Config"}</DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <InputLabel required sx={{ font: "inherit", mt: 1 }}>
          Endpoint
        </InputLabel>
        <Paper square={false} sx={{ mt: 1 }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs
              value={endpointType}
              textColor="secondary"
              indicatorColor="secondary"
              onChange={(_event: any, newValue: any) => {
                setEndpointType(newValue);
              }}
            >
              <Tab label="By templates" value="template" />
              <Tab label="By resource property" value="http-operation" />
            </Tabs>
          </Box>
          {endpointType === "template" && (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                justifyContent: "flex-start",
                pl: 2,
                pr: 2,
                pb: 2,
              }}
            >
              <InputLabel sx={{ font: "inherit", pt: 2 }}>Default Templates</InputLabel>

              <TextField
                id="AzureCloud"
                label="Azure Cloud"
                type="text"
                InputLabelProps={{
                  shrink: true,
                }}
                fullWidth
                variant="standard"
                placeholder="Endpoint template in Azure Cloud, e.g. https://{vaultName}.vault.azure.net"
                value={templateAzureCloud}
                onChange={(event: any) => {
                  setTemplateAzureCloud(event.target.value);
                }}
                margin="dense"
                required
              />

              <TextField
                id="AzureChinaCloud"
                label="Azure China Cloud"
                type="text"
                InputLabelProps={{
                  shrink: true,
                }}
                fullWidth
                variant="standard"
                placeholder="Endpoint template in Azure China Cloud, e.g. https://{vaultName}.vault.azure.cn"
                value={templateAzureChinaCloud}
                onChange={(event: any) => {
                  setTemplateAzureChinaCloud(event.target.value);
                }}
                margin="normal"
              />

              <TextField
                id="AzureUSGovernment"
                label="Azure US Government"
                type="text"
                InputLabelProps={{
                  shrink: true,
                }}
                fullWidth
                variant="standard"
                placeholder="Endpoint template in Azure US Government, e.g. https://{vaultName}.vault.usgovcloudapi.net"
                value={templateAzureUSGovernment}
                onChange={(event: any) => {
                  setTemplateAzureUSGovernment(event.target.value);
                }}
                margin="normal"
              />

              <TextField
                id="AzureGermanCloud"
                label="Azure German Cloud"
                type="text"
                InputLabelProps={{
                  shrink: true,
                }}
                fullWidth
                variant="standard"
                placeholder="Endpoint template in Azure German Cloud, e.g. https://{vaultName}.vault.microsoftazure.de"
                value={templateAzureGermanCloud}
                onChange={(event: any) => {
                  setTemplateAzureGermanCloud(event.target.value);
                }}
                margin="normal"
              />
              <InputLabel sx={{ font: "inherit", pt: 2 }}>From Cloud Metadata</InputLabel>

              <TextField
                id="selector-index"
                label="Endpoint/Suffix Index"
                type="text"
                InputLabelProps={{
                  shrink: true,
                }}
                fullWidth
                variant="standard"
                placeholder="Property index to fetch endpoint or suffix from cloud metadata api response, e.g. suffixes.keyVaultDns"
                value={cloudMetadataSelectorIndex}
                onChange={(event: any) => {
                  setCloudMetadataSelectorIndex(event.target.value);
                }}
                margin="dense"
              />
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "flex-end",
                  justifyContent: "flex-start",
                }}
              >
                <TextField
                  id="prefix-template"
                  label="Prefix"
                  type="text"
                  fullWidth
                  variant="standard"
                  placeholder="Template appended before suffix, e.g. https://{vaultName}"
                  value={cloudMetadataPrefixTemplate}
                  onChange={(event: any) => {
                    setCloudMetadataPrefixTemplate(event.target.value);
                  }}
                  margin="dense"
                />
                <AddRoundedIcon />
                <TemplateSuffixTypography sx={{ flexShrink: 0, mr: 1 }}>.Suffix</TemplateSuffixTypography>
              </Box>
            </Box>
          )}
          {endpointType === "http-operation" && (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                justifyContent: "flex-start",
                pt: 2,
                pl: 2,
                pr: 2,
                pb: 2,
              }}
            >
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
              <MiddlePadding />
              <SwaggerItemSelector
                name="API Version"
                commonPrefix=""
                options={versionOptions}
                value={selectedVersion}
                onValueUpdate={onVersionUpdate}
              />
              <MiddlePadding />
              <SwaggerItemSelector
                name="Resource ID"
                commonPrefix=""
                options={resourceIdOptions}
                value={selectedResourceId}
                onValueUpdate={(resourceId: string | null) => {
                  setSelectedResourceId(resourceId);
                }}
              />
              <MiddlePadding />
              <TextField
                id="subresource"
                label="Endpoint Property Index"
                type="text"
                InputLabelProps={{
                  shrink: true,
                }}
                fullWidth
                variant="standard"
                placeholder="Property index for the api response to fetch the endpoint, e.g. properties.attestUri"
                value={subresource}
                onChange={(event: any) => {
                  setSubresource(event.target.value);
                }}
                margin="dense"
                required
              />
            </Box>
          )}
        </Paper>

        <InputLabel required sx={{ font: "inherit", mt: 4 }}>
          MS Entra(AAD) Auth Scopes
        </InputLabel>
        {aadAuthScopes?.map(buildAadScopeInput)}
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "flex-start",
            ml: 1,
          }}
        >
          <IconButton edge="start" color="inherit" onClick={onAddAadScope} aria-label="add">
            <AddCircleRoundedIcon fontSize="small" />
          </IconButton>
          <AuthTypography sx={{ flexShrink: 0 }}> One more scope </AuthTypography>
        </Box>
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
          <React.Fragment>
            {!isAdd && <Button onClick={handleClose}>Cancel</Button>}
            <Button onClick={handleUpdate}>Update</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

interface ClientEndpointTemplate {
  cloud: string;
  template: string;
}

interface ClientEndpointCloudMetadata {
  selectorIndex: string;
  prefixTemplate?: string;
}

interface ClientTemplateMap {
  [cloud: string]: string;
}

interface ClientAADAuth {
  scopes: string[];
}

interface ClientAuth {
  aad: ClientAADAuth;
}

interface ClientConfig {
  version: string;
  endpointTemplates?: ClientTemplateMap;
  endpointCloudMetadata?: ClientEndpointCloudMetadata;
  endpointResource?: Resource;
  auth: ClientAuth;
}

type ResourceVersion = {
  version: string;
  operations: ResourceVersionOperations;
  file: string;
  id: string;
  path: string;
};

type ResourceVersionOperations = {
  [Named: string]: string;
};

export default WSEditorClientConfigDialog;
export type { ClientEndpointTemplate, ClientTemplateMap, ClientAADAuth, ClientConfig };
