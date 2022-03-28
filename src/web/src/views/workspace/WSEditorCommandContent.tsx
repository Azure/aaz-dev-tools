import { Alert, Box, Button, Card, CardActions, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, Accordion, InputLabel, LinearProgress, Radio, RadioGroup, TextField, Typography, TypographyProps, AccordionSummary, AccordionDetails, IconButton, Input, InputAdornment, InputBase, AccordionActions, Paper, PaperProps, AccordionSummaryProps, Tooltip } from '@mui/material';
import { styled } from '@mui/system';
import axios from 'axios';
import * as React from 'react';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import { NameTypography, ShortHelpTypography, ShortHelpPlaceHolderTypography, LongHelpTypography, StableTypography, PreviewTypography, ExperimentalTypography, SubtitleTypography, CardTitleTypography } from './WSEditorTheme';
import DoDisturbOnRoundedIcon from '@mui/icons-material/DoDisturbOnRounded';
import AddCircleRoundedIcon from '@mui/icons-material/AddCircleRounded';
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import LabelIcon from '@mui/icons-material/Label';
import WSEditorCommandArgumentsContent from './WSEditorCommandArgumentsContent';
import EditIcon from '@mui/icons-material/Edit';

interface Example {
    name: string,
    commands: string[],
}

interface Resource {
    id: string,
    version: string,
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
}

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
}

interface ResponseCommands {
    [name: string]: ResponseCommand
}

interface WSEditorCommandContentProps {
    workspaceUrl: string
    command: Command
    onUpdateCommand: (command: Command | null) => void
}

interface WSEditorCommandContentState {
    displayCommandDialog: boolean
    displayExampleDialog: boolean
    displayCommandDeleteDialog: boolean
    exampleIdx?: number
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

const ExampleEditTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
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
))(({ theme }) => ({
    flexDirection: 'row-reverse',
    '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
        transform: 'rotate(0deg)',
    },
}));


class WSEditorCommandContent extends React.Component<WSEditorCommandContentProps, WSEditorCommandContentState> {

    constructor(props: WSEditorCommandContentProps) {
        super(props);
        this.state = {
            displayCommandDialog: false,
            displayExampleDialog: false,
            displayCommandDeleteDialog: false,
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
        this.setState({
            displayCommandDialog: false,
        })
        if (newCommand) {
            this.props.onUpdateCommand(newCommand!);
        }
    }

    handleCommandDeleteDialogClose = (deleted: boolean) => {
        this.setState({
            displayCommandDeleteDialog: false,
        })
        if (deleted) {
            this.props.onUpdateCommand(null);
        }
    }

    onExampleDialogDisplay = (idx?: number) => {
        this.setState({
            displayExampleDialog: true,
            exampleIdx: idx,
        })
    }

    handleExampleDialogClose = (newCommand?: Command) => {
        this.setState({
            displayExampleDialog: false,
        })
        if (newCommand) {
            this.props.onUpdateCommand(newCommand!);
        }
    }

    render() {
        const { workspaceUrl, command } = this.props;
        const name = commandPrefix + this.props.command.names.join(' ');
        const shortHelp = this.props.command.help?.short;
        const longHelp = this.props.command.help?.lines?.join('\n');
        const lines: string[] = this.props.command.help?.lines ?? [];
        const stage = this.props.command.stage;
        const version = this.props.command.version;
        const examples: Example[] = this.props.command.examples ?? [];
        const commandUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + command.names.slice(0, -1).join('/') + '/Leaves/' + command.names[command.names.length - 1];
        const { displayCommandDialog, displayExampleDialog, displayCommandDeleteDialog, exampleIdx } = this.state;

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
                                startIcon={<EditIcon color="info" fontSize='small' />}
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

        return (
            <React.Fragment>
                <Box sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'stretch',
                }}>
                    <Card
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
                            {!shortHelp && <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>Please add command short summery!</ShortHelpPlaceHolderTypography>}
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
                            <Box sx={{
                                display: "flex",
                                flexDirection: "row",
                                alignContent: "center",
                                justifyContent: "flex-start"
                            }}>

                                <Button
                                    variant='contained' size="small" color='info' disableElevation
                                    onClick={this.onCommandDialogDisplay}
                                    sx={{ mr: 2 }}
                                >
                                    <Typography variant='body2'>
                                        Edit
                                    </Typography>
                                </Button>
                                <Button
                                    variant='outlined' size="small" color='info'
                                    onClick={this.onCommandDeleteDialogDisplay}
                                    sx={{ mr: 2 }}
                                >
                                    <Typography variant='body2'>
                                        Delete
                                    </Typography>
                                </Button>
                                <Button
                                    variant='outlined' size="small" color='info'
                                    sx={{ mr: 2 }}
                                    disabled
                                >
                                    <Typography variant='body2'>
                                        Try
                                    </Typography>
                                </Button>
                            </Box>
                        </CardActions>
                    </Card>

                    <Card
                        elevation={3}
                        sx={{
                            flexGrow: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            mt: 1,
                            p: 2
                        }}>
                        <WSEditorCommandArgumentsContent commandUrl={commandUrl} />
                    </Card>

                    <Card
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
                                variant='contained' size="small" color='info' disableElevation
                                onClick={() => this.onExampleDialogDisplay(undefined)}
                            >
                                <Typography variant='body2'>
                                    Add
                                </Typography>
                            </Button>
                        </CardActions>
                    </Card>

                </Box>
                {displayCommandDialog && <CommandDialog open={displayCommandDialog} workspaceUrl={workspaceUrl} command={command} onClose={this.handleCommandDialogClose} />}
                {displayExampleDialog && <ExampleDialog open={displayExampleDialog} workspaceUrl={workspaceUrl} command={command} idx={exampleIdx} onClose={this.handleExampleDialogClose} />}

                {displayCommandDeleteDialog && <CommandDeleteDialog open={displayCommandDeleteDialog} workspaceUrl={workspaceUrl} command={command} onClose={this.handleCommandDeleteDialogClose} />}
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

    React.useEffect(() => {
        setRelatedCommands([]);
        const urls = props.command.resources.map(resource => {
            const resourceId = btoa(resource.id)
            const version = btoa(resource.version)
            return `${props.workspaceUrl}/Resources/${resourceId}/V/${version}`
        })
        const promisesAll = urls.map(url => {
            return axios.get(`${url}/Commands`)
        })

        Promise.all(promisesAll)
            .then(responses => {
                const commands = new Set<string>();
                responses.forEach(response => {
                    const responseCommands: ResponseCommand[] = response.data
                    responseCommands
                        .map(responseCommand => DecodeResponseCommand(responseCommand))
                        .map(cmd => { commands.add(cmd.names.join(" ")) });
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
        const urls = props.command.resources.map(resource => {
            const resourceId = btoa(resource.id)
            const version = btoa(resource.version)
            return `${props.workspaceUrl}/Resources/${resourceId}/V/${version}`
        })
        const promisesAll = urls.map(url => {
            return axios.delete(url)
        })

        Promise.all(promisesAll)
            .then(res => {
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
                        <LinearProgress color='info' />
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
            updating: false
        }
    }

    handleModify = (event: any) => {
        let { name, stage, shortHelp, longHelp } = this.state
        let { workspaceUrl, command } = this.props

        name = name.trim();
        shortHelp = shortHelp.trim();
        longHelp = longHelp.trim();

        const names = name.split(' ').filter((n) => n.length > 0);

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
            if (!/^[a-z0-9]+(\-[a-z0-9]+)*$/.test(piece)) {
                this.setState({
                    invalidText: `Invalid Name part: '${piece}'. Supported regular expression is: [a-z0-9]+(\-[a-z0-9]+)* `
                })
                return
            }
        }

        if (shortHelp.length < 1) {
            this.setState({
                invalidText: `Field 'Short Summery' is required.`
            })
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
            if (err.resource?.message) {
                this.setState({
                    invalidText: `ResponseError: ${err.resource!.message!}`,
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
        const { name, shortHelp, longHelp, invalidText, updating, stage } = this.state;
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
                        id="shortSummery"
                        label="Short Summery"
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
                        id="longSummery"
                        label="Long Summery"
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
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='info' />
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
        let { workspaceUrl, command } = this.props;

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
            if (err.resource?.message) {
                this.setState({
                    invalidText: `ResponseError: ${err.resource!.message!}`,
                })
            }
            this.setState({
                updating: false,
            })
        });
    }

    handleDelete = () => {
        let { command } = this.props;
        let examples: Example[] = command.examples ?? [];
        let idx = this.props.idx!;
        examples = [...examples.slice(0, idx), ...examples.slice(idx + 1)];
        this.onUpdateExamples(examples);
    }

    handleModify = () => {
        let { command } = this.props;
        let { name, exampleCommands } = this.state;
        let examples: Example[] = command.examples ?? [];
        let idx = this.props.idx!;

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
        let { command } = this.props;
        let { name, exampleCommands } = this.state;
        let examples: Example[] = command.examples ?? [];

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
            let exampleCommands: string[] = [...preState.exampleCommands.slice(0, idx), ...preState.exampleCommands.slice(idx + 1)];
            if (exampleCommands.length == 0) {
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
                            aria-label="remove"
                        >
                            <AddCircleRoundedIcon fontSize="small" />
                        </IconButton>
                        <ExampleCommandTypography sx={{ flexShrink: 0 }}> One more command</ExampleCommandTypography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='info' />
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

const DecodeResponseCommand = (command: ResponseCommand): Command => {
    return {
        id: 'command:' + command.names.join('/'),
        names: command.names,
        help: command.help,
        stage: command.stage ?? "Stable",
        examples: command.examples,
        resources: command.resources,
        version: command.version,
    }
}
export default WSEditorCommandContent;

export { DecodeResponseCommand };
export type { Command, ResponseCommand, ResponseCommands };

