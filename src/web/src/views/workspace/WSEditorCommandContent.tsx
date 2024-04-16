import { styled, Alert, Box, Button, Card, CardActions, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, Accordion, InputLabel, LinearProgress, Radio, RadioGroup, TextField, Typography, TypographyProps, AccordionDetails, IconButton, Input, InputAdornment, AccordionSummaryProps, FormLabel } from '@mui/material';
import axios from 'axios';
import React, { useState, useEffect } from 'react';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import { NameTypography, ShortHelpTypography, ShortHelpPlaceHolderTypography, LongHelpTypography, StableTypography, PreviewTypography, ExperimentalTypography, SubtitleTypography, CardTitleTypography } from './WSEditorTheme';
import DoDisturbOnRoundedIcon from '@mui/icons-material/DoDisturbOnRounded';
import AddCircleRoundedIcon from '@mui/icons-material/AddCircleRounded';
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import LabelIcon from '@mui/icons-material/Label';
import WSEditorCommandArgumentsContent, { ClsArgDefinitionMap, CMDArg, DecodeArgs } from './WSEditorCommandArgumentsContent';
import EditIcon from '@mui/icons-material/Edit';


interface Plane {
    name: string,
    displayName: string,
    moduleOptions?: string[],
}

interface Example {
    name: string,
    commands: string[],
}

interface Resource {
    id: string,
    version: string,
    subresource?: string,
    swagger: string,
}

interface Command {
    id: string
    names: string[]
    help?: {
        short: string
        lines?: string[]
    }
    stage: "Stable" | "Preview" | "Experimental"
    version: string
    examples?: Example[]
    resources: Resource[]

    // additional property
    confirmation?: string
    args?: CMDArg[]
    clsArgDefineMap?: ClsArgDefinitionMap
}

// interface ClientConfig {
//     args?: CMDArg[]
// }

interface ResponseCommand {
    names: string[],
    help?: {
        short: string
        lines?: string[]
    }
    stage?: "Stable" | "Preview" | "Experimental"
    version: string,
    examples?: Example[],
    resources: Resource[],
    confirmation?: string,
    argGroups?: any[],
}

interface ResponseCommands {
    [name: string]: ResponseCommand
}

interface WSEditorCommandContentProps {
    workspaceUrl: string
    previewCommand: Command
    reloadTimestamp: number
    onUpdateCommand: (command: Command | null) => void
}

interface WSEditorCommandContentState {
    command?: Command,
    displayCommandDialog: boolean,
    displayExampleDialog: boolean,
    displayCommandDeleteDialog: boolean,
    displayAddSubcommandDialog: boolean,
    subcommandDefaultGroupNames?: string[],
    subcommandArgVar?: string,
    subcommandSubArgOptions?: { var: string, options: string }[],
    exampleIdx?: number,
    loading: boolean,
}

const commandPrefix = 'az '

const ExampleCommandHeaderTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}))

const ExampleCommandBodyTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}))

const ExampleEditTypography = styled(Typography)<TypographyProps>(() => ({
    color: "#5d64cf",
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}));

const ExampleAccordionSummary = styled((props: AccordionSummaryProps) => (
    <MuiAccordionSummary
        expandIcon={<LabelIcon fontSize="small" color="primary" />}
        {...props}
    />
))(() => ({
    flexDirection: 'row-reverse',
    '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
        transform: 'rotate(0deg)',
    },
}));


class WSEditorCommandContent extends React.Component<WSEditorCommandContentProps, WSEditorCommandContentState> {

    constructor(props: WSEditorCommandContentProps) {
        super(props);
        this.state = {
            command: undefined,
            displayCommandDialog: false,
            displayExampleDialog: false,
            displayCommandDeleteDialog: false,
            displayAddSubcommandDialog: false,
            loading: false,
        }
    }

    loadCommand = async () => {
        this.setState({ loading: true })
        const { workspaceUrl, previewCommand } = this.props
        const commandNames = previewCommand.names;
        const leafUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + commandNames.slice(0, -1).join('/') + '/Leaves/' + commandNames[commandNames.length - 1];
        try {
            const res = await axios.get(leafUrl);
            const command = DecodeResponseCommand(res.data);
            if (command.id === this.props.previewCommand.id) {
                this.setState({
                    loading: false,
                    command: command
                })
            }
        } catch (err: any) {
            this.setState({ loading: false })
            console.error(err)
            return
        }
    }

    componentDidMount() {
        this.loadCommand();
    }

    componentDidUpdate(prevProps: WSEditorCommandContentProps) {
        if (prevProps.workspaceUrl !== this.props.workspaceUrl || prevProps.previewCommand.id !== this.props.previewCommand.id || prevProps.reloadTimestamp !== this.props.reloadTimestamp) {
            if (prevProps.previewCommand.id !== this.props.previewCommand.id) {
                this.setState({ command: undefined })
            }
            this.loadCommand();
        }
    }

    onCommandDialogDisplay = () => {
        this.setState({
            displayCommandDialog: true,
        })
    }

    onCommandDeleteDialogDisplay = () => {
        this.setState({
            displayCommandDeleteDialog: true,
        })
    }

    handleCommandDialogClose = (newCommand?: Command) => {
        if (newCommand) {
            this.props.onUpdateCommand(newCommand!);
        }
        this.setState({
            displayCommandDialog: false,
        })
    }

    handleCommandDeleteDialogClose = (deleted: boolean) => {
        if (deleted) {
            this.props.onUpdateCommand(null);
        }
        this.setState({
            displayCommandDeleteDialog: false,
        })
    }

    onExampleDialogDisplay = (idx?: number) => {
        this.setState({
            displayExampleDialog: true,
            exampleIdx: idx,
        })
    }

    handleExampleDialogClose = (newCommand?: Command) => {
        if (newCommand) {
            this.props.onUpdateCommand(newCommand!);
        }
        this.setState({
            displayExampleDialog: false,
        })
    }

    onAddSubcommandDialogDisplay = (argVar: string, subArgOptions: { var: string, options: string }[], argStackNames: string[]) => {
        this.setState({
            displayAddSubcommandDialog: true,
            subcommandArgVar: argVar,
            subcommandSubArgOptions: subArgOptions,
            subcommandDefaultGroupNames: [...this.props.previewCommand.names.slice(0, -1), ...argStackNames],
        })
    }

    handleAddSubcommandDisplayClose = (add: boolean) => {
        if (add) {
            this.props.onUpdateCommand(this.state.command!);
        }
        this.setState({
            displayAddSubcommandDialog: false,
            subcommandArgVar: undefined,
            subcommandDefaultGroupNames: undefined
        })
    }

    render() {
        const { workspaceUrl, previewCommand } = this.props;
        const commandNames = previewCommand.names;
        const name = commandPrefix + commandNames.join(' ');
        const commandUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + commandNames.slice(0, -1).join('/') + '/Leaves/' + commandNames[commandNames.length - 1];

        const { command, displayCommandDialog, displayExampleDialog, displayCommandDeleteDialog, displayAddSubcommandDialog, exampleIdx, loading } = this.state;

        const buildExampleView = (example: Example, idx: number) => {
            const buildCommand = (exampleCommand: string, cmdIdx: number) => {
                return (<Box key={`example-${idx}-command-${cmdIdx}`} sx={{
                    display: "flex",
                    flexDirection: 'row',
                    alignItems: 'flex-start',
                    justifyContent: 'flex-start',
                }}>
                    <Box component="span" sx={{
                        flexShrink: 0,
                        display: "flex",
                        flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-start',
                    }}>
                        <KeyboardDoubleArrowRightIcon fontSize="small" />
                        <ExampleCommandHeaderTypography sx={{ flexShrink: 0 }}>{commandPrefix}</ExampleCommandHeaderTypography>
                    </Box>
                    <Box component="span" sx={{
                        ml: 0.8,
                    }}>
                        <ExampleCommandBodyTypography>{exampleCommand}</ExampleCommandBodyTypography>
                    </Box>
                </Box>)
            }
            return (
                <Accordion
                    elevation={0}
                    expanded
                    key={`example-${idx}`}
                    onDoubleClick={() => { this.onExampleDialogDisplay(idx) }}
                >
                    <ExampleAccordionSummary
                        id={`example-${idx}-header`}
                    >
                        <Box sx={{
                            ml: 1,
                            flexGrow: 1,
                            display: "flex",
                            flexDirection: "row",
                            alignItems: "center",
                        }}>
                            <SubtitleTypography sx={{ flexShrink: 0 }} >{example.name}</SubtitleTypography>
                            {/* <Box sx={{ flexGrow: 1 }} /> */}
                            <Button sx={{ flexShrink: 0, ml: 3 }}
                                startIcon={<EditIcon color="secondary" fontSize='small' />}
                                onClick={() => { this.onExampleDialogDisplay(idx) }}
                            >
                                <ExampleEditTypography>Edit</ExampleEditTypography>
                            </Button>
                        </Box>
                    </ExampleAccordionSummary>
                    <AccordionDetails sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'stretch',
                        justifyContent: 'flex-start',
                        ml: 3,
                        mr: 3,
                        paddingTop: 0,
                    }}>
                        {example.commands.map(buildCommand)}
                    </AccordionDetails>
                </Accordion>
            )
        }

        const buildCommandCard = () => {
            const shortHelp = (command ?? previewCommand).help?.short;
            const longHelp = (command ?? previewCommand).help?.lines?.join('\n');
            const lines: string[] = (command ?? previewCommand).help?.lines ?? [];
            const stage = (command ?? previewCommand).stage;
            const version = (command ?? previewCommand).version;

            return (<Card
                onDoubleClick={this.onCommandDialogDisplay}
                elevation={3}
                sx={{
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    p: 2
                }}>
                <CardContent sx={{
                    flex: '1 0 auto',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'stretch',
                }}>
                    <Box sx={{
                        mb: 2,
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: "center"
                    }}>
                        <CardTitleTypography sx={{ flexShrink: 0 }}>
                            [ COMMAND ]
                        </CardTitleTypography>
                        <Box sx={{ flexGrow: 1 }} />
                        {stage === "Stable" && <StableTypography
                            sx={{ flexShrink: 0 }}
                        >
                            {`v${version}`}
                        </StableTypography>}
                        {stage === "Preview" && <PreviewTypography
                            sx={{ flexShrink: 0 }}
                        >
                            {`v${version}`}
                        </PreviewTypography>}
                        {stage === "Experimental" && <ExperimentalTypography
                            sx={{ flexShrink: 0 }}
                        >
                            {`v${version}`}
                        </ExperimentalTypography>}
                    </Box>

                    <NameTypography sx={{ mt: 1 }}>
                        {name}
                    </NameTypography>
                    {shortHelp && <ShortHelpTypography sx={{ ml: 6, mt: 2 }}> {shortHelp} </ShortHelpTypography>}
                    {!shortHelp && <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>Please add command short summary!</ShortHelpPlaceHolderTypography>}
                    {longHelp && <Box sx={{ ml: 6, mt: 1, mb: 1 }}>
                        {lines.map((line, idx) => (<LongHelpTypography key={idx}>{line}</LongHelpTypography>))}
                    </Box>}
                </CardContent>
                <CardActions sx={{
                    display: "flex",
                    flexDirection: "row-reverse",
                    alignContent: "center",
                    justifyContent: "flex-start"
                }}>
                    {loading && <Box sx={{ width: '100%' }}>
                        <LinearProgress color='secondary' />
                    </Box>}
                    {!loading && <Box sx={{
                        display: "flex",
                        flexDirection: "row",
                        alignContent: "center",
                        justifyContent: "flex-start"
                    }}>

                        <Button
                            variant='contained' size="small" color='secondary' disableElevation
                            onClick={this.onCommandDialogDisplay}
                            disabled={loading}
                            sx={{ mr: 2 }}
                        >
                            <Typography variant='body2'>
                                Edit
                            </Typography>
                        </Button>
                        <Button
                            variant='outlined' size="small" color='secondary'
                            onClick={this.onCommandDeleteDialogDisplay}
                            disabled={loading}
                            sx={{ mr: 2 }}
                        >
                            <Typography variant='body2'>
                                Delete
                            </Typography>
                        </Button>
                        <Button
                            variant='outlined' size="small" color='secondary'
                            sx={{ mr: 2 }}
                            disabled
                        >
                            <Typography variant='body2'>
                                Try
                            </Typography>
                        </Button>
                    </Box>}
                </CardActions>
            </Card>)
        }

        const buildArgumentsCard = () => {
            return (<Card
                elevation={3}
                sx={{
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    mt: 1,
                    p: 2
                }}>
                <WSEditorCommandArgumentsContent commandUrl={commandUrl} args={command!.args!} clsArgDefineMap={command!.clsArgDefineMap!} onReloadArgs={this.loadCommand} onAddSubCommand={this.onAddSubcommandDialogDisplay} />
            </Card>)
        }

        const buildExampleCard = () => {
            const examples = command!.examples ?? []
            return (<Card
                elevation={3}
                sx={{
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    mt: 1,
                    p: 2
                }}>

                <CardContent sx={{
                    flex: '1 0 auto',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'stretch',
                }}>
                    <Box sx={{
                        mb: 2,
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: "center"
                    }}>
                        <CardTitleTypography sx={{ flexShrink: 0 }}>
                            [ EXAMPLE ]
                        </CardTitleTypography>

                    </Box>
                    {examples.length > 0 && <Box>
                        {examples.map(buildExampleView)}
                    </Box>}
                </CardContent>

                <CardActions sx={{
                    display: "flex",
                    flexDirection: "row-reverse",
                }}>
                    <Button
                        variant='contained' size="small" color='secondary' disableElevation
                        onClick={() => this.onExampleDialogDisplay(undefined)}
                    >
                        <Typography variant='body2'>
                            Add
                        </Typography>
                    </Button>
                </CardActions>
            </Card>)
        }

        return (
            <React.Fragment>
                <Box sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'stretch',
                }}>
                    {buildCommandCard()}
                    {command !== undefined && command.args !== undefined && buildArgumentsCard()}
                    {command !== undefined && buildExampleCard()}
                </Box>
                {command !== undefined && displayCommandDialog && <CommandDialog open={displayCommandDialog} workspaceUrl={workspaceUrl} command={command!} onClose={this.handleCommandDialogClose} />}
                {command !== undefined && displayExampleDialog && <ExampleDialog open={displayExampleDialog} workspaceUrl={workspaceUrl} command={command!} idx={exampleIdx} onClose={this.handleExampleDialogClose} />}
                {command !== undefined && displayCommandDeleteDialog && <CommandDeleteDialog open={displayCommandDeleteDialog} workspaceUrl={workspaceUrl} command={command!} onClose={this.handleCommandDeleteDialogClose} />}
                {command !== undefined && displayAddSubcommandDialog && <AddSubcommandDialog open={displayAddSubcommandDialog} workspaceUrl={workspaceUrl} command={command!} onClose={this.handleAddSubcommandDisplayClose} argVar={this.state.subcommandArgVar!} subArgOptions={this.state.subcommandSubArgOptions!} defaultGroupNames={this.state.subcommandDefaultGroupNames!} />}
            </React.Fragment>
        )
    }
}


function CommandDeleteDialog(props: {
    workspaceUrl: string,
    open: boolean,
    command: Command,
    onClose: (deleted: boolean) => void
}) {
    const [updating, setUpdating] = React.useState<boolean>(false);
    const [relatedCommands, setRelatedCommands] = React.useState<string[]>([]);

    const getUrls = () => {
        const urls: string[] = [];

        props.command.resources.forEach(resource => {
            const resourceId = btoa(resource.id)
            const version = btoa(resource.version)
            if (resource.subresource !== undefined) {
                const subresource = btoa(resource.subresource)
                // TODO: delete list command together with crud
                // if (resource.subresource.endsWith('[]') || resource.subresource.endsWith('{}')) {
                //     let subresource2 = btoa(resource.subresource.slice(0, -2))
                //     urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources/${subresource2}`)
                // } else {
                //     let subresource2 = btoa(resource.subresource + '[]');
                //     urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources/${subresource2}`)
                //     subresource2 = btoa(resource.subresource + '{}');
                //     urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources/${subresource2}`)
                // }
                urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources/${subresource}`)
            } else {
                urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}`)
            }
        })
        return urls;
    }

    React.useEffect(() => {
        setRelatedCommands([]);
        const urls = getUrls();
        const promisesAll = urls.map(url => {
            return axios.get(`${url}/Commands`)
        })
        Promise.all(promisesAll)
            .then(responses => {
                const commands = new Set<string>();
                responses.forEach((response: any) => {
                    const responseCommands: ResponseCommand[] = response.data
                    responseCommands
                        .map(responseCommand => DecodeResponseCommand(responseCommand))
                        .forEach(cmd => { commands.add(cmd.names.join(" ")) });
                });

                const cmdNames: string[] = [];
                commands.forEach(cmdName => cmdNames.push(cmdName));
                cmdNames.sort((a, b) => a.localeCompare(b));
                setRelatedCommands(cmdNames);
            })
            .catch(err => {
                console.error(err.response)
            })

    }, [props.command]);

    const handleClose = () => {
        props.onClose(false);
    }
    const handleDelete = () => {
        setUpdating(true);
        const urls = getUrls();
        const promisesAll = urls.map(url => {
            return axios.delete(url)
        })
        Promise.all(promisesAll)
            .then(() => {
                setUpdating(false);
                props.onClose(true);
            })
            .catch(err => {
                setUpdating(false);
                console.error(err.response)
            })
    }
    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
        >
            <DialogTitle>Delete Commands</DialogTitle>
            <DialogContent dividers={true}>
                {relatedCommands.map((command, idx) => (
                    <Typography key={`command-${idx}`} variant="body2">{`${commandPrefix}${command}`}</Typography>
                ))}
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='secondary' />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleDelete}>Delete</Button>
                </React.Fragment>}
            </DialogActions>

        </Dialog>
    )
}

interface CommandDialogProps {
    workspaceUrl: string,
    open: boolean
    command: Command
    onClose: (newCommand?: Command) => void
}

interface CommandDialogState {
    name: string,
    stage: string,
    shortHelp: string,
    longHelp: string,
    invalidText?: string,
    confirmation: string,
    updating: boolean
}


class CommandDialog extends React.Component<CommandDialogProps, CommandDialogState> {

    constructor(props: CommandDialogProps) {
        super(props);
        this.state = {
            name: this.props.command.names.join(' '),
            shortHelp: this.props.command.help?.short ?? "",
            longHelp: this.props.command.help?.lines?.join('\n') ?? "",
            stage: this.props.command.stage,
            confirmation: this.props.command.confirmation ?? "",
            updating: false
        }
    }

    handleModify = () => {
        let { name, shortHelp, longHelp, confirmation } = this.state
        const { stage } = this.state

        const { workspaceUrl, command } = this.props

        name = name.trim();
        shortHelp = shortHelp.trim();
        longHelp = longHelp.trim();
        confirmation = confirmation.trim();

        const names = name.split(' ').filter(n => n.length > 0);

        this.setState({
            invalidText: undefined
        })

        if (names.length < 1) {
            this.setState({
                invalidText: `Field 'Name' is required.`
            })
            return
        }

        for (const idx in names) {
            const piece = names[idx];
            if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                this.setState({
                    invalidText: `Invalid Name part: '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `
                })
                return
            }
        }

        if (shortHelp.length < 1) {
            this.setState({
                invalidText: `Field 'Short Summary' is required.`
            })
            return
        }

        let lines: string[] | null = null;
        if (longHelp.length > 1) {
            lines = longHelp.split('\n').filter(l => l.length > 0);
        }

        this.setState({
            updating: true,
        })

        const leafUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + command.names.slice(0, -1).join('/') + '/Leaves/' + command.names[command.names.length - 1];

        axios.patch(leafUrl, {
            help: {
                short: shortHelp,
                lines: lines,
            },
            stage: stage,
            confirmation: confirmation,
        }).then(res => {
            const name = names.join(' ');
            if (name === command.names.join(' ')) {
                const cmd = DecodeResponseCommand(res.data);
                this.setState({
                    updating: false,
                })
                this.props.onClose(cmd);
            } else {
                // Rename command
                axios.post(`${leafUrl}/Rename`, {
                    name: name
                }).then(res => {
                    const cmd = DecodeResponseCommand(res.data);
                    this.setState({
                        updating: false,
                    })
                    this.props.onClose(cmd);
                })
            }
        }).catch(err => {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`,
                })
            }
            this.setState({
                updating: false,
            })
        });
    }

    handleClose = () => {
        this.setState({
            invalidText: undefined
        });
        this.props.onClose();
    }

    render() {
        const { name, shortHelp, longHelp, invalidText, updating, stage, confirmation } = this.state;
        return (
            <Dialog
                disableEscapeKeyDown
                open={this.props.open}
                sx={{ '& .MuiDialog-paper': { width: '80%' } }}
            >
                <DialogTitle>Command</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <InputLabel required shrink sx={{ font: "inherit" }}>Stage</InputLabel>
                    <RadioGroup
                        row
                        value={stage}
                        name="stage"
                        onChange={(event: any) => {
                            this.setState({
                                stage: event.target.value,
                            })
                        }}
                    >
                        <FormControlLabel value="Stable" control={<Radio />} label="Stable" sx={{ ml: 4 }} />
                        <FormControlLabel value="Preview" control={<Radio />} label="Preview" sx={{ ml: 4 }} />
                        <FormControlLabel value="Experimental" control={<Radio />} label="Experimental" sx={{ ml: 4 }} />
                    </RadioGroup>

                    <TextField
                        id="name"
                        label="Name"
                        type="text"
                        fullWidth
                        variant='standard'
                        value={name}
                        onChange={(event: any) => {
                            this.setState({
                                name: event.target.value,
                            })
                        }}
                        margin="normal"
                        required
                    />
                    <TextField
                        id="shortSummary"
                        label="Short Summary"
                        type="text"
                        fullWidth
                        variant='standard'
                        value={shortHelp}
                        onChange={(event: any) => {
                            this.setState({
                                shortHelp: event.target.value,
                            })
                        }}
                        margin="normal"
                        required
                    />
                    <TextField
                        id="longSummary"
                        label="Long Summary"
                        helperText="Please add long summer in lines."
                        type="text"
                        fullWidth
                        multiline
                        variant='standard'
                        value={longHelp}
                        onChange={(event: any) => {
                            this.setState({
                                longHelp: event.target.value,
                            })
                        }}
                        margin="normal"
                    />
                    <TextField
                        id="confirmation"
                        label="Command confirmation"
                        helperText="Modify or clear confirmation message as needed."
                        type="text"
                        fullWidth
                        multiline
                        variant='standard'
                        value={confirmation}
                        onChange={(event: any) => {
                            this.setState({
                                confirmation: event.target.value,
                            })
                        }}
                        margin="normal"
                    />
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='secondary' />
                        </Box>
                    }
                    {!updating && <React.Fragment>
                        <Button onClick={this.handleClose}>Cancel</Button>
                        <Button onClick={this.handleModify}>Save</Button>
                    </React.Fragment>}
                </DialogActions>
            </Dialog>
        )
    }
}

// function CommandDeleteDialog

interface ExampleDialogProps {
    workspaceUrl: string
    open: boolean
    command: Command
    idx?: number
    onClose: (newCommand?: Command) => void
}

interface ExampleDialogState {
    name: string
    exampleCommands: string[]
    isAdd: boolean
    invalidText?: string
    updating: boolean
}

const ExampleCommandTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 400,
}))

class ExampleDialog extends React.Component<ExampleDialogProps, ExampleDialogState> {

    constructor(props: ExampleDialogProps) {
        super(props);
        const examples: Example[] = this.props.command.examples ?? [];
        if (this.props.idx === undefined) {
            this.state = {
                name: "",
                exampleCommands: ["",],
                isAdd: true,
                invalidText: undefined,
                updating: false,
            }
        } else {
            const example = examples[this.props.idx];
            this.state = {
                name: example.name,
                exampleCommands: example.commands,
                isAdd: false,
                invalidText: undefined,
                updating: false,
            }
        }
    }

    onUpdateExamples = (examples: Example[]) => {
        const { workspaceUrl, command } = this.props;

        const leafUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + command.names.slice(0, -1).join('/') + '/Leaves/' + command.names[command.names.length - 1];

        this.setState({
            updating: true,
        })
        axios.patch(leafUrl, {
            examples: examples
        }).then(res => {
            const cmd = DecodeResponseCommand(res.data);
            this.setState({
                updating: false,
            })
            this.props.onClose(cmd);
        }).catch(err => {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`,
                })
            }
            this.setState({
                updating: false,
            })
        });
    }

    handleDelete = () => {
        const { command } = this.props;
        let examples: Example[] = command.examples ?? [];
        const idx = this.props.idx!;
        examples = [...examples.slice(0, idx), ...examples.slice(idx + 1)];
        this.onUpdateExamples(examples);
    }

    handleModify = () => {
        const { command } = this.props;
        let { name, exampleCommands } = this.state;
        let examples: Example[] = command.examples ?? [];
        const idx = this.props.idx!;

        name = name.trim();
        if (name.length < 1) {
            this.setState({
                invalidText: `Field 'Name' is required.`
            })
            return
        }
        exampleCommands = exampleCommands.map(cmd => {
            return cmd.split('\n')
                .map(cmdLine => cmdLine.trim())
                .filter(cmdLine => cmdLine.length > 0)
                .join(' ')
                .trim();
        }).filter(cmd => cmd.length > 0);

        if (exampleCommands.length < 1) {
            this.setState({
                invalidText: `Field 'Commands' is required.`
            })
            return
        }

        const newExample: Example = {
            name: name,
            commands: exampleCommands
        }

        examples = [...examples.slice(0, idx), newExample, ...examples.slice(idx + 1)];

        this.onUpdateExamples(examples);
    }

    handleAdd = () => {
        const { command } = this.props;
        let { name, exampleCommands } = this.state;
        const examples: Example[] = command.examples ?? [];

        name = name.trim();
        if (name.length < 1) {
            this.setState({
                invalidText: `Field 'Name' is required.`
            })
            return
        }
        exampleCommands = exampleCommands.map(cmd => {
            return cmd.split('\n')
                .map(cmdLine => cmdLine.trim())
                .filter(cmdLine => cmdLine.length > 0)
                .join(' ')
                .trim();
        }).filter(cmd => cmd.length > 0);

        if (exampleCommands.length < 1) {
            this.setState({
                invalidText: `Field 'Commands' is required.`
            })
            return
        }

        const newExample: Example = {
            name: name,
            commands: exampleCommands
        }
        examples.push(newExample);

        this.onUpdateExamples(examples);
    }

    handleClose = () => {
        this.setState({
            invalidText: undefined
        });
        this.props.onClose()
    }

    onModifyExampleCommand = (cmd: string, idx: number) => {
        this.setState(preState => {
            return {
                ...preState,
                exampleCommands: [...preState.exampleCommands.slice(0, idx), cmd, ...preState.exampleCommands.slice(idx + 1)]
            }
        })
    }

    onRemoveExampleCommand = (idx: number) => {
        this.setState(preState => {
            const exampleCommands: string[] = [...preState.exampleCommands.slice(0, idx), ...preState.exampleCommands.slice(idx + 1)];
            if (exampleCommands.length === 0) {
                exampleCommands.push("");
            }
            return {
                ...preState,
                exampleCommands: exampleCommands,
            }
        })
    }

    onAddExampleCommand = () => {
        this.setState(preState => {
            return {
                ...preState,
                exampleCommands: [...preState.exampleCommands, ""]
            }
        })
    }

    render() {
        const { name, exampleCommands, isAdd, invalidText, updating } = this.state;

        const buildExampleInput = (cmd: string, idx: number) => {
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
                        onClick={() => this.onRemoveExampleCommand(idx)}
                        aria-label="remove"
                    >
                        <DoDisturbOnRoundedIcon fontSize="small" />
                    </IconButton>
                    <Input
                        id={`command-${idx}`}
                        multiline
                        value={cmd}
                        onChange={(event: any) => {
                            this.onModifyExampleCommand(event.target.value, idx)
                        }}
                        sx={{ flexGrow: 1 }}
                        placeholder="Input a command here."
                        startAdornment={
                            <InputAdornment position="start">
                                <ExampleCommandTypography>{commandPrefix}</ExampleCommandTypography>
                            </InputAdornment>
                        }
                    />
                </Box>
            );
        }

        return (
            <Dialog
                disableEscapeKeyDown
                open={this.props.open}
                sx={{ '& .MuiDialog-paper': { width: '80%' } }}
            >
                <DialogTitle>{isAdd ? "Add Example" : "Modify Example"}</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <TextField
                        id="name"
                        label="Name"
                        type="text"
                        fullWidth
                        variant='standard'
                        value={name}
                        onChange={(event: any) => {
                            this.setState({
                                name: event.target.value,
                            })
                        }}
                        margin="normal"
                        required
                    />
                    <InputLabel required sx={{ font: "inherit", mt: 1 }}>Commands</InputLabel>
                    {exampleCommands.map(buildExampleInput)}
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
                            onClick={this.onAddExampleCommand}
                            aria-label="add"
                        >
                            <AddCircleRoundedIcon fontSize="small" />
                        </IconButton>
                        <ExampleCommandTypography sx={{ flexShrink: 0 }}> One more command</ExampleCommandTypography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='secondary' />
                        </Box>
                    }
                    {!updating && <React.Fragment>
                        <Button onClick={this.handleClose}>Cancel</Button>
                        {!isAdd && <React.Fragment>
                            <Button onClick={this.handleDelete}>Delete</Button>
                            <Button onClick={this.handleModify}>Save</Button>
                        </React.Fragment>}
                        {isAdd && <Button onClick={this.handleAdd}>Add</Button>}
                    </React.Fragment>}
                </DialogActions>
            </Dialog>
        )
    }
}

function AddSubcommandDialog(props: {
    workspaceUrl: string,
    command: Command,
    argVar: string,
    subArgOptions: { var: string, options: string }[],
    defaultGroupNames: string[],
    open: boolean,
    onClose: (added: boolean) => void,
}) {

    const [updating, setUpdating] = useState<boolean>(false);
    const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
    const [commandGroupName, setCommandGroupName] = useState<string>("");
    const [refArgsOptions, setRefArgsOptions] = useState<{ var: string, options: string }[]>([]);

    useEffect(() => {
        setCommandGroupName(props.defaultGroupNames.join(' '));
        setRefArgsOptions(props.subArgOptions);
    }, [props.argVar, props.defaultGroupNames]);

    const handleClose = () => {
        setInvalidText(undefined);
        props.onClose(false);
    }

    const verifyAddSubresource = () => {
        setInvalidText(undefined);
        const argOptions: { [argVar: string]: string[] } = {}
        let invalidText: string | undefined = undefined;
        refArgsOptions.forEach((arg, idx) => {
            const names = arg.options.split(' ').filter(n => n.length > 0);
            if (names.length < 1) {
                invalidText = `Prop ${idx + 1} option name is required.`
                return undefined
            }

            for (const idx in names) {
                const piece = names[idx];
                if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                    invalidText = `Invalid 'Prop ${idx + 1} option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `
                    return undefined
                }
            }
            argOptions[arg.var] = names;
        });

        const names = commandGroupName.split(' ').filter(n => n.length > 0);
        if (names.length < 1) {
            invalidText = 'Invalid Command group name';
            return
        }

        if (invalidText !== undefined) {
            setInvalidText(invalidText);
            return undefined
        }

        return {
            commandGroupName: names.join(' '),
            refArgsOptions: argOptions,
        }
    }

    const handleAddSubresource = async () => {
        const urls = props.command.resources.map(resource => {
            const resourceId = btoa(resource.id)
            const version = btoa(resource.version)
            return `${props.workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources`
        })

        if (urls.length !== 1) {
            setInvalidText(`Cannot create subcommands, command contains ${props.command.resources.length} resources`);
            return;
        }

        const data = verifyAddSubresource();
        if (data === undefined) {
            return;
        }

        setUpdating(true);

        try {
            await axios.post(urls[0], {
                ...data,
                arg: props.argVar,
            })
            props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(`ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`);
            }
            setUpdating(false);
        }
    }

    const buildRefArgText = (arg: { var: string, options: string }, idx: number) => {
        return (<TextField
            id={`subArg-${arg.var}`}
            key={arg.var}
            label={`${arg.var}`}
            helperText={idx === 0 ? "You can input multiple names separated by a space character" : undefined}
            type="text"
            fullWidth
            variant='standard'
            value={arg.options}
            onChange={(event: any) => {
                const options = refArgsOptions.map(value => {
                    if (value.var === arg.var) {
                        return {
                            ...value,
                            options: event.target.value,
                        }
                    } else {
                        return value
                    }
                });
                setRefArgsOptions(options)
            }}
            margin="normal"
            required
        />)
    }

    return (<Dialog
        disableEscapeKeyDown
        open={props.open}
        sx={{ '& .MuiDialog-paper': { width: '80%' } }}
    >
        <DialogTitle>Add Subcommands</DialogTitle>
        <DialogContent dividers={true}>
            {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
            <FormLabel>Subcommand Group</FormLabel>
            <TextField
                id='subcommand-group-name'
                label='name'
                placeholder='Please input command group name for subcommands'
                type="text"
                variant='standard'
                value={commandGroupName}
                fullWidth
                margin="normal"
                required
                onChange={(event: any) => {
                    setCommandGroupName(event.target.value)
                }}
            />
            {refArgsOptions.length > 0 && <>
                <FormLabel>Argument Options</FormLabel>
                {refArgsOptions.map(buildRefArgText)}
            </>}
        </DialogContent>
        <DialogActions>
            {updating &&
                <Box sx={{ width: '100%' }}>
                    <LinearProgress color='secondary' />
                </Box>
            }
            {!updating && <>
                <Button onClick={handleClose}>Cancel</Button>
                <Button onClick={handleAddSubresource}>Add Subcommands</Button>
            </>}
        </DialogActions>
    </Dialog>)
}

const DecodeResponseCommand = (command: ResponseCommand): Command => {
    let cmd: Command = {
        id: 'command:' + command.names.join('/'),
        names: command.names,
        help: command.help,
        stage: command.stage ?? "Stable",
        examples: command.examples,
        resources: command.resources,
        version: command.version,
    }

    if (command.confirmation) {
        cmd.confirmation = command.confirmation
    }

    if (command.argGroups) {
        cmd = {
            ...cmd,
            ...DecodeArgs(command.argGroups!)
        }
    }

    return cmd;
}

export default WSEditorCommandContent;

export { DecodeResponseCommand };
export type { Plane, Command, Resource, ResponseCommand, ResponseCommands };
