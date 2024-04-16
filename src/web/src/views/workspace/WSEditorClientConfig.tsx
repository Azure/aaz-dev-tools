import * as React from 'react';
import { styled, Box, Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress, Button, Paper, TextField, Alert, InputLabel, IconButton, Input, Typography, TypographyProps, Tabs, Tab } from '@mui/material';
import axios from 'axios';
import DoDisturbOnRoundedIcon from '@mui/icons-material/DoDisturbOnRounded';
import AddCircleRoundedIcon from '@mui/icons-material/AddCircleRounded';
import { Plane, Resource } from './WSEditorCommandContent';
import { SwaggerItemSelector } from './WSEditorSwaggerPicker';
import AddRoundedIcon from '@mui/icons-material/AddRounded';

interface WSEditorClientConfigDialogProps {
    workspaceUrl: string,
    open: boolean,
    onClose: (updated: boolean) => void
}

interface WSEditorClientConfigDialogState {
    updating: boolean,
    invalidText: string | undefined,
    isAdd: boolean,

    endpointType: "template" | "http-operation",

    templateAzureCloud: string,
    templateAzureChinaCloud: string,
    templateAzureUSGovernment: string,
    templateAzureGermanCloud: string,
    cloudMetadataSelectorIndex: string,
    cloudMetadataPrefixTemplate: string,

    aadAuthScopes: string[],

    planes: Plane[],
    planeOptions: string[],
    selectedPlane: string | null,

    moduleOptions: string[],
    moduleOptionsCommonPrefix: string,
    selectedModule: string | null,

    resourceProviderOptions: string[],
    resourceProviderOptionsCommonPrefix: string,
    selectedResourceProvider: string | null,

    versionOptions: string[],
    versionResourceIdMap: SwaggerVersionResourceIdMap,
    selectedVersion: string | null,

    resourceIdOptions: string[],
    selectedResourceId: string | null,
    subresource: string,
}

interface SwaggerVersionResourceIdMap {
    [version: string]: string[]
}

interface ClientEndpointResource {
    plane: string,
    module: string,
    version: string,
    id: string,
    subresource: string,
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
    height: '1.5vh'
}));

class WSEditorClientConfigDialog extends React.Component<WSEditorClientConfigDialogProps, WSEditorClientConfigDialogState> {

    constructor(props: WSEditorClientConfigDialogProps) {
        super(props);
        this.state = {
            updating: false,
            invalidText: undefined,
            isAdd: true,

            endpointType: "template",

            templateAzureCloud: "",
            templateAzureChinaCloud: "",
            templateAzureUSGovernment: "",
            templateAzureGermanCloud: "",
            cloudMetadataSelectorIndex: "",
            cloudMetadataPrefixTemplate: "",

            aadAuthScopes: ["",],

            planes: [],
            planeOptions: [],
            selectedPlane: null,

            moduleOptions: [],
            moduleOptionsCommonPrefix: '',
            selectedModule: null,

            resourceProviderOptions: [],
            resourceProviderOptionsCommonPrefix: '',
            selectedResourceProvider: null,

            versionOptions: [],
            versionResourceIdMap: {},
            selectedVersion: null,

            resourceIdOptions: [],
            selectedResourceId: null,
            subresource: "",

        }
    }

    componentDidMount(): void {
        this.loadPlanes().then(async () => {
            await this.loadWorkspaceClientConfig();
            const { selectedPlane, selectedModule, selectedResourceProvider, selectedVersion } = this.state;
            await this.onPlaneSelectorUpdate(selectedPlane ?? this.state.planeOptions[0]);
            if (selectedModule) {
                await this.loadResourceProviders(selectedModule);
            }
            if (selectedResourceProvider) {
                await this.loadResources(selectedResourceProvider, selectedVersion);
            }
        });
    }

    loadPlanes = async () => {
        try {
            this.setState({
                updating: true
            });

            const res = await axios.get(`/AAZ/Specs/Planes`);
            const planes: Plane[] = res.data.map((v: any) => {
                return {
                    name: v.name,
                    displayName: v.displayName,
                    moduleOptions: undefined,
                }
            })
            const planeOptions: string[] = res.data.map((v: any) => v.displayName)
            this.setState({
                planes: planes,
                planeOptions: planeOptions,
                updating: false
            })
            await this.onPlaneSelectorUpdate(planeOptions[0]);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    updating: false,
                    invalidText: `ResponseError: ${data.message!}`,
                })
            }
        }
    }

    onPlaneSelectorUpdate = async (planeDisplayName: string | null) => {
        const plane = this.state.planes.find((v) => v.displayName === planeDisplayName) ?? null;
        if (this.state.selectedPlane !== (plane?.displayName ?? null)) {
            if (!plane) {
                return
            }
            this.setState({
                selectedPlane: plane?.displayName ?? null,
            })
            await this.loadSwaggerModules(plane);
        } else {
            this.setState({
                selectedPlane: plane?.displayName ?? null
            })
        }
    }

    loadSwaggerModules = async (plane: Plane | null) => {
        if (plane !== null) {
            if (plane!.moduleOptions?.length) {
                this.setState({
                    moduleOptions: plane!.moduleOptions!,
                    moduleOptionsCommonPrefix: `/Swagger/Specs/${plane!.name}/`,
                })
                await this.onModuleSelectionUpdate(null);
            } else {
                try {
                    this.setState({
                        updating: true
                    });
                    const res = await axios.get(`/Swagger/Specs/${plane!.name}`);
                    const options: string[] = res.data.map((v: any) => (v.url));
                    this.setState(preState => {
                        const planes = preState.planes;
                        const index = planes.findIndex((v) => v.name === plane!.name);
                        planes[index].moduleOptions = options;
                        return {
                            ...preState,
                            updating: false,
                            planes: planes,
                            moduleOptions: options,
                            moduleOptionsCommonPrefix: `/Swagger/Specs/${plane!.name}/`,
                        }
                    })
                    await this.onModuleSelectionUpdate(null);
                } catch (err: any) {
                    console.error(err.response);
                    if (err.response?.data?.message) {
                        const data = err.response!.data!;
                        this.setState({
                            updating: false,
                            invalidText: `ResponseError: ${data.message!}`,
                        })
                    }
                }
            }
        } else {
            this.setState({
                moduleOptions: [],
                moduleOptionsCommonPrefix: '',
            })
            await this.onModuleSelectionUpdate(null);
        }

    }

    onModuleSelectionUpdate = async (moduleValueUrl: string | null) => {
        if (this.state.selectedModule !== moduleValueUrl) {
            this.setState({
                selectedModule: moduleValueUrl
            });
            await this.loadResourceProviders(moduleValueUrl);
        } else {
            this.setState({
                selectedModule: moduleValueUrl
            })
        }
    }

    loadResourceProviders = async (moduleUrl: string | null) => {
        if (moduleUrl !== null) {
            try {
                this.setState({
                    updating: true
                });
                const res = await axios.get(`${moduleUrl}/ResourceProviders`);
                const options: string[] = res.data.map((v: any) => (v.url));
                const selectedResourceProvider = options.length === 1 ? options[0] : null;
                this.setState({
                    updating: false,
                    resourceProviderOptions: options,
                    resourceProviderOptionsCommonPrefix: `${moduleUrl}/ResourceProviders/`,
                });
                this.onResourceProviderUpdate(selectedResourceProvider)
            } catch (err: any) {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        updating: false,
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            }
        } else {
            this.setState({
                resourceProviderOptions: [],
                resourceProviderOptionsCommonPrefix: '',
            })
            this.onResourceProviderUpdate(null);
        }
    }

    onResourceProviderUpdate = async (resourceProviderUrl: string | null) => {
        if (this.state.selectedResourceProvider !== resourceProviderUrl) {
            this.setState({
                selectedResourceProvider: resourceProviderUrl,
            })
            await this.loadResources(resourceProviderUrl, null);
        } else {
            this.setState({
                selectedResourceProvider: resourceProviderUrl
            })
        }
    }

    loadResources = async (resourceProviderUrl: string | null, selectVersion: string | null) => {
        if (resourceProviderUrl != null) {
            this.setState({
                invalidText: undefined,
                updating: true,
            })
            try {
                const res = await axios.get(`${resourceProviderUrl}/Resources`);
                const versionResourceIdMap: SwaggerVersionResourceIdMap = {}
                const versionOptions: string[] = []
                const resourceIdList: string[] = []
                res.data.forEach((resource: any) => {
                    resourceIdList.push(resource.id);
                    const resourceVersions = resource.versions.filter((v: ResourceVersion) => {
                        for (const key in v.operations) {
                            if (v.operations[key].toUpperCase() === 'GET') {
                                return true;
                            }
                        }
                        return false;
                    }).map((v: any) => v.version)
                    resourceVersions.forEach((v: any) => {
                        if (!(v in versionResourceIdMap)) {
                            versionResourceIdMap[v] = [];
                            versionOptions.push(v);
                        }
                        versionResourceIdMap[v].push(resource.id);
                    })
                })
                versionOptions.sort((a, b) => a.localeCompare(b)).reverse()
                if (selectVersion === null && (versionOptions.length === 0 || versionOptions.findIndex(v => v === selectVersion) < 0)) {
                    selectVersion = null;
                }
                if (!selectVersion && versionOptions.length > 0) {
                    selectVersion = versionOptions[0];
                }

                this.setState({
                    updating: false,
                    versionResourceIdMap: versionResourceIdMap,
                    versionOptions: versionOptions,
                })
                this.onVersionUpdate(selectVersion);
            } catch (err: any) {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            }
        } else {
            this.setState({
                versionOptions: [],
            })
            this.onVersionUpdate(null)
        }
    }

    onVersionUpdate = (version: string | null) => {
        this.setState(preState => {
            let selectedResourceId = preState.selectedResourceId;
            let resourceIdOptions: string[] = [];
            if (version != null) {
                resourceIdOptions = [...preState.versionResourceIdMap[version]]
                    .sort((a, b) => a.toString().localeCompare(b.toString()));
                if (selectedResourceId !== null && resourceIdOptions.findIndex(v => v === selectedResourceId) < 0) {
                    selectedResourceId = null;
                }
            }
            return {
                ...preState,
                resourceIdOptions: resourceIdOptions,
                selectedVersion: version,
                preferredAAZVersion: version,
                selectedResourceId: selectedResourceId,
            }
        })
    }

    loadWorkspaceClientConfig = async () => {
        this.setState({ updating: true });
        try {
            const res = await axios.get(`${this.props.workspaceUrl}/ClientConfig`);
            const clientConfig: ClientConfig = {
                version: res.data.version,
                auth: res.data.auth,
            }
            let templateAzureCloud = "";
            let templateAzureChinaCloud = "";
            let templateAzureUSGovernment = "";
            let templateAzureGermanCloud = "";
            let cloudMetadataSelectorIndex = "";
            let cloudMetadataPrefixTemplate = "";
            let endpointType: "template" | "http-operation" = "template";
            let selectedPlane: string | null = null;
            let selectedModule: string | null = null;
            let selectedResourceProvider: string | null = null;
            let selectedVersion: string | null = null;
            let selectedResourceId: string | null = null;
            let subresource: string = "";

            if (res.data.endpoints.type === "template") {
                clientConfig.endpointTemplates = {};
                res.data.endpoints.templates.forEach((value: any) => {
                    clientConfig.endpointTemplates![value.cloud] = value.template;
                });
                clientConfig.endpointCloudMetadata = res.data.endpoints.cloudMetadata;

                endpointType = "template";
                templateAzureCloud = clientConfig.endpointTemplates!['AzureCloud'] ?? "";
                templateAzureChinaCloud = clientConfig.endpointTemplates!['AzureChinaCloud'] ?? "";
                templateAzureUSGovernment = clientConfig.endpointTemplates!['AzureUSGovernment'] ?? "";
                templateAzureGermanCloud = clientConfig.endpointTemplates!['AzureGermanCloud'] ?? "";
                cloudMetadataSelectorIndex = clientConfig.endpointCloudMetadata?.selectorIndex ?? "";
                cloudMetadataPrefixTemplate = clientConfig.endpointCloudMetadata?.prefixTemplate ?? "";
            } else if (res.data.endpoints.type === "http-operation") {
                clientConfig.endpointResource = res.data.endpoints.resource;
                const rpUrl: string = clientConfig.endpointResource!.swagger.split('/Paths/')[0];
                const moduleUrl: string = rpUrl.split('/ResourceProviders/')[0];
                const planeUrl: string = moduleUrl.split('/')[0];
                selectedResourceProvider = `/Swagger/Specs/${rpUrl}`
                selectedModule = `/Swagger/Specs/${moduleUrl}`
                selectedPlane = `/Swagger/Specs/${planeUrl}`
                selectedVersion = clientConfig.endpointResource!.version;
                selectedResourceId = clientConfig.endpointResource!.id;
                subresource = clientConfig.endpointResource!.subresource ?? '';
                endpointType = "http-operation";
            }

            this.setState({
                aadAuthScopes: clientConfig.auth.aad.scopes ?? ["",],
                endpointType: endpointType,
                templateAzureCloud: templateAzureCloud,
                templateAzureChinaCloud: templateAzureChinaCloud,
                templateAzureUSGovernment: templateAzureUSGovernment,
                templateAzureGermanCloud: templateAzureGermanCloud,
                cloudMetadataSelectorIndex: cloudMetadataSelectorIndex,
                cloudMetadataPrefixTemplate: cloudMetadataPrefixTemplate,
                selectedPlane: selectedPlane,
                selectedModule: selectedModule,
                selectedResourceProvider: selectedResourceProvider,
                selectedVersion: selectedVersion,
                selectedResourceId: selectedResourceId,
                subresource: subresource,
                isAdd: false
            });
        } catch (err: any) {
            // catch 404 error
            if (err.response?.status === 404) {
                this.setState({
                    isAdd: true,
                });
            } else {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({ invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}` });
                }
            }
        }

        this.setState({ updating: false });
    }

    handleClose = () => {
        this.props.onClose(false);
    }

    handleUpdate = async () => {
        let { aadAuthScopes} = this.state
        const { endpointType } = this.state
        let templates: ClientEndpointTemplate[] | undefined = undefined;
        let resource: ClientEndpointResource | undefined = undefined;
        let cloudMetadata: ClientEndpointCloudMetadata | undefined = undefined;

        if (endpointType === "template") {
            let { templateAzureCloud, templateAzureChinaCloud, templateAzureGermanCloud, templateAzureUSGovernment } = this.state
            templateAzureCloud = templateAzureCloud.trim();
            if (templateAzureCloud.length < 1) {
                this.setState({
                    invalidText: "Azure Cloud Endpoint Template is required."
                });
                return;
            }
            templateAzureChinaCloud = templateAzureChinaCloud.trim();
            templateAzureUSGovernment = templateAzureUSGovernment.trim();
            templateAzureGermanCloud = templateAzureGermanCloud.trim();
            // verify template url using regex, like https://{vaultName}.vault.azure.net
            const templateRegex = /^https:\/\/((\{[a-zA-Z0-9]+\})|([^{}.]+))(.((\{[a-zA-Z0-9]+\})|([^{}.]+)))*(\/)?$/;
            if (!templateRegex.test(templateAzureCloud)) {
                this.setState({
                    invalidText: "Azure Cloud Endpoint Template is invalid."
                });
                return;
            }

            if (templateAzureChinaCloud.length > 0 && !templateRegex.test(templateAzureChinaCloud)) {
                this.setState({
                    invalidText: "Azure China Cloud Endpoint Template is invalid."
                });
                return;
            }

            if (templateAzureUSGovernment.length > 0 && !templateRegex.test(templateAzureUSGovernment)) {
                this.setState({
                    invalidText: "Azure US Government Endpoint Template is invalid."
                });
                return;
            }

            if (templateAzureGermanCloud.length > 0 && !templateRegex.test(templateAzureGermanCloud)) {
                this.setState({
                    invalidText: "Azure German Cloud Endpoint Template is invalid."
                });
                return;
            }

            templates = [
                { cloud: 'AzureCloud', template: templateAzureCloud },
            ];
            if (templateAzureChinaCloud.length > 0) {
                templates.push({ cloud: 'AzureChinaCloud', template: templateAzureChinaCloud });
            }
            if (templateAzureUSGovernment.length > 0) {
                templates.push({ cloud: 'AzureUSGovernment', template: templateAzureUSGovernment });
            }
            if (templateAzureGermanCloud.length > 0) {
                templates.push({ cloud: 'AzureGermanCloud', template: templateAzureGermanCloud });
            }

            let { cloudMetadataSelectorIndex, cloudMetadataPrefixTemplate } = this.state;
            cloudMetadataSelectorIndex = cloudMetadataSelectorIndex.trim();
            cloudMetadataPrefixTemplate = cloudMetadataPrefixTemplate.trim();
            if (cloudMetadataSelectorIndex.length < 1 && cloudMetadataPrefixTemplate.length > 0) {
                this.setState({
                    invalidText: "Cloud Metadata Selector Index is required."
                });
                return;
            } else if (cloudMetadataSelectorIndex.length > 0 ) {

                cloudMetadata = {
                    selectorIndex: cloudMetadataSelectorIndex,
                }
                if (cloudMetadataPrefixTemplate.length > 0) {
                    // verify template url using regex, like https://{vaultName}
                    if (!templateRegex.test(cloudMetadataPrefixTemplate)) {
                        this.setState({
                            invalidText: "Cloud Metadata Prefix is invalid."
                        });
                        return;
                    }
                    cloudMetadata.prefixTemplate = cloudMetadataPrefixTemplate;
                }
            }

        } else if (endpointType === "http-operation") {
            let { subresource } = this.state;
            const { selectedPlane, selectedModule, selectedResourceProvider, selectedVersion, selectedResourceId, moduleOptionsCommonPrefix } = this.state;
            if (!selectedPlane) {
                this.setState({
                    invalidText: "Plane is required."
                });
                return;
            }
            if (!selectedModule) {
                this.setState({
                    invalidText: "Module is required."
                });
                return;
            }
            if (!selectedResourceProvider) {
                this.setState({
                    invalidText: "Resource Provider is required."
                });
                return;
            }
            if (!selectedVersion) {
                this.setState({
                    invalidText: "API Version is required."
                });
                return;
            }
            if (!selectedResourceId) {
                this.setState({
                    invalidText: "Resource ID is required."
                });
                return;
            }
            subresource = subresource.trim();
            if (subresource.length < 1) {
                this.setState({
                    invalidText: "Endpoint Property Index is required."
                });
                return;
            }

            resource = {
                plane: selectedPlane.replace('/Swagger/Specs/', ''),
                module: selectedModule.replace(moduleOptionsCommonPrefix, ''),
                version: selectedVersion,
                id: selectedResourceId,
                subresource: subresource,
            }
        }

        aadAuthScopes = aadAuthScopes.map(scope => scope.trim()).filter(scope => scope.length > 0);
        if (aadAuthScopes.length < 1) {
            this.setState({
                invalidText: "MS Entra(AAD) Auth Scopes is required."
            });
            return;
        }

        const auth = {
            aad: {
                scopes: aadAuthScopes,
            }
        }

        this.onUpdateClientConfig(
            templates,
            cloudMetadata,
            resource,
            auth,
        );
    }

    onUpdateClientConfig = async (
        templates: ClientEndpointTemplate[] | undefined,
        cloudMetadata: ClientEndpointCloudMetadata | undefined,
        resource: ClientEndpointResource | undefined,
        auth: ClientAuth,
    ) => {
        this.setState({ updating: true });
        try {
            await axios.post(`${this.props.workspaceUrl}/ClientConfig`, {
                templates: templates,
                cloudMetadata: cloudMetadata,
                resource: resource,
                auth: auth,
            });
            this.setState({ updating: false });
            this.props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({ invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}` });
            }
            this.setState({ updating: false });
        }

    }

    onRemoveAadScope = (idx: number) => {
        this.setState(preState => {
            const aadAuthScopes: string[] = [...preState.aadAuthScopes.slice(0, idx), ...preState.aadAuthScopes.slice(idx + 1)];
            if (aadAuthScopes.length === 0) {
                aadAuthScopes.push("");
            }
            return {
                ...preState,
                aadAuthScopes: aadAuthScopes,
            }
        })
    }

    onModifyAadScope = (scope: string, idx: number) => {
        this.setState(preState => {
            return {
                ...preState,
                aadAuthScopes: [...preState.aadAuthScopes.slice(0, idx), scope, ...preState.aadAuthScopes.slice(idx + 1)]
            }
        })
    }

    onAddAadScope = () => {
        this.setState(preState => {
            return {
                ...preState,
                aadAuthScopes: [...preState.aadAuthScopes, ""],
            }
        })
    }

    buildAadScopeInput = (scope: string, idx: number) => {
        return (
            <Box key={idx} sx={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'flex-start',
                ml: 1,
            }}>
                <IconButton
                    edge="start"
                    color="inherit"
                    onClick={() => this.onRemoveAadScope(idx)}
                    aria-label='remove'
                >
                    <DoDisturbOnRoundedIcon fontSize="small" />
                </IconButton>
                <Input
                    id={`aadScope-${idx}`}
                    value={scope}
                    onChange={(event: any) => {
                        this.onModifyAadScope(event.target.value, idx);
                    }}
                    sx={{ flexGrow: 1 }}
                    placeholder="Input Microsoft Entra(AAD) auth Scope here, e.g. https://metrics.monitor.azure.com/.default"
                />
            </Box>
        )
    }

    render() {
        const { invalidText, updating, isAdd, aadAuthScopes, endpointType, templateAzureCloud, templateAzureChinaCloud, templateAzureUSGovernment, templateAzureGermanCloud, cloudMetadataSelectorIndex, cloudMetadataPrefixTemplate } = this.state;
        const { selectedModule, selectedResourceProvider, selectedVersion, selectedResourceId, subresource } = this.state;
        return (
            <Dialog
                disableEscapeKeyDown
                fullWidth={true}
                maxWidth="md"
                open={this.props.open}
            >
                <DialogTitle>{isAdd ? "Setup Client Config" : "Modify Client Config"}</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <InputLabel required sx={{ font: "inherit", mt: 1 }}>Endpoint</InputLabel>
                    <Paper square={false} sx={{ mt: 1 }} >
                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                            <Tabs
                                value={endpointType}
                                textColor="secondary"
                                indicatorColor="secondary"
                                onChange={(_event: any, newValue: any) => {
                                    this.setState({
                                        endpointType: newValue,
                                    })
                                }}>
                                <Tab label="By templates" value="template" />
                                <Tab label="By resource property" value="http-operation" />
                            </Tabs>
                        </Box>
                        {endpointType === "template" && <Box
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'stretch',
                                justifyContent: 'flex-start',
                                pl: 2,
                                pr: 2,
                                pb: 2,
                            }}>
                            <InputLabel sx={{ font: "inherit", pt: 2 }}>Default Templates</InputLabel>

                            <TextField
                                id="AzureCloud"
                                label="Azure Cloud"
                                type="text"
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                fullWidth
                                variant='standard'
                                placeholder="Endpoint template in Azure Cloud, e.g. https://{vaultName}.vault.azure.net"
                                value={templateAzureCloud}
                                onChange={(event: any) => {
                                    this.setState({
                                        templateAzureCloud: event.target.value,
                                    })
                                }}
                                margin='dense'
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
                                variant='standard'
                                placeholder="Endpoint template in Azure China Cloud, e.g. https://{vaultName}.vault.azure.cn"
                                value={templateAzureChinaCloud}
                                onChange={(event: any) => {
                                    this.setState({
                                        templateAzureChinaCloud: event.target.value,
                                    })
                                }}
                                margin='normal'
                            />

                            <TextField
                                id="AzureUSGovernment"
                                label="Azure US Government"
                                type="text"
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                fullWidth
                                variant='standard'
                                placeholder="Endpoint template in Azure US Government, e.g. https://{vaultName}.vault.usgovcloudapi.net"
                                value={templateAzureUSGovernment}
                                onChange={(event: any) => {
                                    this.setState({
                                        templateAzureUSGovernment: event.target.value,
                                    })
                                }}
                                margin='normal'
                            />

                            <TextField
                                id="AzureGermanCloud"
                                label="Azure German Cloud"
                                type="text"
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                fullWidth
                                variant='standard'
                                placeholder="Endpoint template in Azure German Cloud, e.g. https://{vaultName}.vault.microsoftazure.de"
                                value={templateAzureGermanCloud}
                                onChange={(event: any) => {
                                    this.setState({
                                        templateAzureGermanCloud: event.target.value,
                                    })
                                }}
                                margin='normal'
                            />
                            <InputLabel sx={{ font: "inherit", pt: 2}}>From Cloud Metadata</InputLabel>
                            
                            <TextField
                                id="selector-index"
                                label="Endpoint/Suffix Index"
                                type="text"
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                fullWidth
                                variant='standard'
                                placeholder="Property index to fetch endpoint or suffix from cloud metadata api response, e.g. suffixes.keyVaultDns"
                                value={cloudMetadataSelectorIndex}
                                onChange={(event: any) => {
                                    this.setState({
                                        cloudMetadataSelectorIndex: event.target.value,
                                    })
                                }}
                                margin='dense'
                            />
                            <Box sx={{
                                display: "flex",
                                flexDirection: "row",
                                alignItems: "flex-end",
                                justifyContent: "flex-start",
                            }}>
                                <TextField
                                    id="prefix-template"
                                    label="Prefix"
                                    type="text"
                                    fullWidth
                                    variant='standard'
                                    placeholder="Template appended before suffix, e.g. https://{vaultName}"
                                    value={cloudMetadataPrefixTemplate}
                                    onChange={(event: any) => {
                                        this.setState({
                                            cloudMetadataPrefixTemplate: event.target.value,
                                        })
                                    }}
                                    margin='dense'
                                />
                                <AddRoundedIcon />
                                <TemplateSuffixTypography sx={{flexShrink: 0, mr: 1}}>.Suffix</TemplateSuffixTypography> 
                            </Box>
                        </Box>}
                        {endpointType === "http-operation" && <Box sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'stretch',
                            justifyContent: 'flex-start',
                            pt: 2,
                            pl: 2,
                            pr: 2,
                            pb: 2,
                        }}>
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
                            <MiddlePadding />
                            <SwaggerItemSelector
                                name='API Version'
                                commonPrefix=''
                                options={this.state.versionOptions}
                                value={selectedVersion}
                                onValueUpdate={this.onVersionUpdate}
                            />
                            <MiddlePadding />
                            <SwaggerItemSelector
                                name='Resource ID'
                                commonPrefix=''
                                options={this.state.resourceIdOptions}
                                value={selectedResourceId}
                                onValueUpdate={(resourceId: string | null) => {
                                    this.setState({
                                        selectedResourceId: resourceId,
                                    })
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
                                variant='standard'
                                placeholder="Property index for the api response to fetch the endpoint, e.g. properties.attestUri"
                                value={subresource}
                                onChange={(event: any) => {
                                    this.setState({
                                        subresource: event.target.value,
                                    })
                                }}
                                margin='dense'
                                required
                            />

                        </Box>}
                    </Paper>

                    <InputLabel required sx={{ font: "inherit", mt: 4 }}>MS Entra(AAD) Auth Scopes</InputLabel>
                    {aadAuthScopes?.map(this.buildAadScopeInput)}
                    <Box sx={{
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: 'center',
                        justifyContent: 'flex-start',
                        ml: 1,
                    }}>
                        <IconButton
                            edge="start"
                            color="inherit"
                            onClick={this.onAddAadScope}
                            aria-label='add'
                        >
                            <AddCircleRoundedIcon fontSize="small" />
                        </IconButton>
                        <AuthTypography sx={{ flexShrink: 0 }}> One more scope </AuthTypography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='secondary' />
                        </Box>
                    }
                    {!updating && <React.Fragment>
                        {!isAdd && <Button onClick={this.handleClose}>Cancel</Button>}
                        <Button onClick={this.handleUpdate}>Update</Button>
                    </React.Fragment>}
                </DialogActions>
            </Dialog>)
    }
}


interface ClientEndpointTemplate {
    cloud: string,
    template: string,
}

interface ClientEndpointCloudMetadata {
    selectorIndex: string,
    prefixTemplate?: string,
}

interface ClientTemplateMap {
    [cloud: string]: string
}

interface ClientAADAuth {
    scopes: string[],
}

interface ClientAuth {
    aad: ClientAADAuth,
}

interface ClientConfig {
    version: string,
    endpointTemplates?: ClientTemplateMap,
    endpointCloudMetadata?: ClientEndpointCloudMetadata,
    endpointResource?: Resource,
    auth: ClientAuth,
}

type ResourceVersion = {
    version: string
    operations: ResourceVersionOperations
    file: string
    id: string
    path: string
}

type ResourceVersionOperations = {
    [Named: string]: string
}

export default WSEditorClientConfigDialog;
export type { ClientEndpointTemplate, ClientTemplateMap, ClientAADAuth, ClientConfig };
