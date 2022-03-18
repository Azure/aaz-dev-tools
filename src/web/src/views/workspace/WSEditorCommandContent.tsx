import { Alert, Box, Button, Card, CardActions, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, InputBase, InputBaseProps, InputLabel, LinearProgress, Radio, RadioGroup, TextField, Typography, TypographyProps } from '@mui/material';
import { createTheme, styled } from '@mui/system';
import axios from 'axios';
import * as React from 'react';
import { Input } from 'reactstrap';
import { NameTypography, ShortHelpTypography, ShortHelpPlaceHolderTypography, LongHelpTypography, StableTypography, PreviewTypography, ExperimentalTypography } from './WSEditorTheme';


interface Command {
    id: string
    names: string[]
    help?: {
        short: string
        lines?: string[]
    }
    stage: "Stable" | "Preview" | "Experimental"
    // examples?: ExampleType[],
    // argGroups?: ArgGroups
}

interface ResponseCommand {
    names: string[],
    help?: {
        short: string
        lines?: string[]
    }
    stage?: "Stable" | "Preview" | "Experimental"
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
    displayCommandDisplay: boolean

}

const commandPrefix = 'Az '

class WSEditorCommandContent extends React.Component<WSEditorCommandContentProps, WSEditorCommandContentState> {

    constructor(props: WSEditorCommandContentProps) {
        super(props);
        this.state = {

            displayCommandDisplay: false,
        }
    }

    onCommandDialogDisplay = () => {
        this.setState({
            displayCommandDisplay: true,
        })
    }

    handleCommandDialogClose = (newCommand?: Command) => {
        this.setState({
            displayCommandDisplay: false,
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
        const { displayCommandDisplay } = this.state;

        return (
            <React.Fragment>
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'stretch',
                }}>
                    <Card variant='outlined'
                        sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                        <CardContent sx={{
                            flex: '1 0 auto',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'stretch',
                        }}>
                            <Box sx={{
                                ml: 2, mr: 2, mt: 1, mb: 2,
                                display: 'flex',
                                flexDirection: 'row',
                                alignItems: "center"
                            }}>
                                <Typography
                                    variant='h6'
                                    sx={{ flexShrink: 0 }}
                                >
                                    [ COMMAND ]
                                </Typography>
                                <Box sx={{ flexGrow: 1 }} />
                                {stage === "Stable" && <StableTypography
                                    sx={{ flexShrink: 0 }}
                                >
                                    {stage}
                                </StableTypography>}
                                {stage === "Preview" && <PreviewTypography
                                    sx={{ flexShrink: 0 }}
                                >
                                    {stage}
                                </PreviewTypography>}
                                {stage === "Experimental" && <ExperimentalTypography
                                    sx={{ flexShrink: 0 }}
                                >
                                    {stage}
                                </ExperimentalTypography>}
                            </Box>

                            <NameTypography sx={{ ml: 2, mr: 2, mt: 1 }}>
                                {name}
                            </NameTypography>
                            {shortHelp && <ShortHelpTypography sx={{ ml: 8, mr: 2, mt: 2 }}> {shortHelp} </ShortHelpTypography>}
                            {!shortHelp && <ShortHelpPlaceHolderTypography sx={{ ml: 8, mr: 2, mt: 2 }}>Please add command short summery!</ShortHelpPlaceHolderTypography>}
                            {longHelp && <Box sx={{ ml: 8, mr: 2, mt: 1, mb: 1 }}>
                                {lines.map((line) => (<LongHelpTypography>{line}</LongHelpTypography>))}
                            </Box>}
                        </CardContent>
                        <CardActions sx={{
                            display: "flex",
                            flexDirection: "row-reverse"
                        }}>
                            <Button
                                variant='outlined' size="small" color='info'
                                onClick={this.onCommandDialogDisplay}
                            >
                                <Typography variant='body2'>
                                    Edit
                                </Typography>
                            </Button>
                        </CardActions>
                    </Card>
                </Box>
                {displayCommandDisplay && <CommandDialog open={displayCommandDisplay} workspaceUrl={workspaceUrl} command={command} onClose={this.handleCommandDialogClose} />}

            </React.Fragment>
        )
    }
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
            console.log(err.response);
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
        const { name, shortHelp, longHelp, invalidText, updating, stage } = this.state
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
                        <Button onClick={this.handleModify}>Submit</Button>
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
    }
}
export default WSEditorCommandContent;

export { DecodeResponseCommand };
export type { Command, ResponseCommand, ResponseCommands };

