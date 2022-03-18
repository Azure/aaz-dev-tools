import { Alert, Box, Button, Card, CardActions, CardContent, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, InputBase, InputBaseProps, InputLabel, LinearProgress, Radio, RadioGroup, TextField, Typography, TypographyProps } from '@mui/material';
import { display, styled } from '@mui/system';
import axios from 'axios';
import * as React from 'react';
import { FormLabel } from 'react-bootstrap';
import { ResponseCommands } from './WSEditorCommandContent';

interface CommandGroup {
    id: string
    names: string[]
    stage: "Stable" | "Preview" | "Experimental"
    help?: {
        short: string
        lines?: string[]
    }
}

interface ResponseCommandGroup {
    names: string[]
    stage?: "Stable" | "Preview" | "Experimental"
    help?: {
        short: string
        lines?: string[]
    }
    commands?: ResponseCommands
    commandGroups?: ResponseCommandGroups
}


interface ResponseCommandGroups {
    [name: string]: ResponseCommandGroup
}


const DecodeResponseCommandGroup = (commandGroup: ResponseCommandGroup): CommandGroup => {
    return {
        id: 'group:' + commandGroup.names.join('/'),
        names: commandGroup.names,
        help: commandGroup.help,
        stage: commandGroup.stage ?? "Stable"
    }
}

const commandPrefix = 'Az '

const NameTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 32,
    fontWeight: 700,
}))

const ShortHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 24,
    fontWeight: 200,
}))

const ShortHelpPlaceHolderTypography = styled(ShortHelpTypography)<TypographyProps>(({ theme }) => ({
    color: '#5d64cf',
}))

const LongHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 18,
    fontWeight: 400,
}))

const StableTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: '#67b349',
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 20,
    fontWeight: 200,
}))

const PreviewTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    color: '#dba339',
}))

const ExperimentalTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    color: '#e05376',
}))



interface WSEditorCommandGroupContentProps {
    workspaceUrl: string,
    commandGroup: CommandGroup
    onUpdateCommandGroup: (commandGroup: CommandGroup | null) => void
}

interface WSEditorCommandGroupContentState {
    displayDialog: boolean
}

class WSEditorCommandGroupContent extends React.Component<WSEditorCommandGroupContentProps, WSEditorCommandGroupContentState> {

    constructor(props: WSEditorCommandGroupContentProps) {
        super(props);
        this.state = {
            displayDialog: false,
        }
    }

    onDialogDisplay = () => {
        this.setState({
            displayDialog: true,
        })
    }

    handleDialogClose = (newCommandGroup?: CommandGroup) => {
        this.setState({
            displayDialog: false,
        })
        if (newCommandGroup) {
            this.props.onUpdateCommandGroup(newCommandGroup!);
        }
    }

    render() {
        const { workspaceUrl, commandGroup } = this.props;
        const name = commandPrefix + this.props.commandGroup.names.join(' ');
        const shortHelp = this.props.commandGroup.help?.short;
        const longHelp = this.props.commandGroup.help?.lines?.join('\n');
        const stage = this.props.commandGroup.stage;
        const { displayDialog } = this.state;
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
                                    [ GROUP ]
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
                            {!shortHelp && <ShortHelpPlaceHolderTypography  sx={{ ml: 8, mr: 2, mt: 2 }}>Please add command group short summery!</ShortHelpPlaceHolderTypography>}
                            {longHelp && <LongHelpTypography sx={{ ml: 8, mr: 2, mt: 1, mb: 1 }}> {longHelp} </LongHelpTypography>}
                        </CardContent>
                        <CardActions sx={{
                            display: "flex",
                            flexDirection: "row-reverse"
                        }}>
                            <Button variant='outlined' size="small" color='info' onClick={this.onDialogDisplay}>
                                <Typography variant='body2'>
                                    Edit
                                </Typography>
                            </Button>
                        </CardActions>
                    </Card>
                </Box>
                {displayDialog && <CommandGroupDialog open={displayDialog} workspaceUrl={workspaceUrl} commandGroup={commandGroup} onClose={this.handleDialogClose} />}
            </React.Fragment>
        )
    }

}

interface CommandGroupDialogProps {
    workspaceUrl: string,
    open: boolean
    commandGroup: CommandGroup
    onClose: (newCommandGroup?: CommandGroup) => void
}

interface CommandGroupDialogState {
    name: string,
    stage: string,
    shortHelp: string,
    longHelp: string,
    invalidText?: string,
    updating: boolean
}

class CommandGroupDialog extends React.Component<CommandGroupDialogProps, CommandGroupDialogState> {

    constructor(props: CommandGroupDialogProps) {
        super(props);
        this.state = {
            name: this.props.commandGroup.names.join(' '),
            shortHelp: this.props.commandGroup.help?.short ?? "",
            longHelp: this.props.commandGroup.help?.lines?.join('\n') ?? "",
            stage: this.props.commandGroup.stage,
            updating: false
        }
    }

    // component

    handleModify = (event: any) => {
        let { name, stage, shortHelp, longHelp } = this.state
        let { workspaceUrl, commandGroup } = this.props

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

        const nodeUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + commandGroup.names.join('/')

        axios.patch(nodeUrl, {
            help: {
                short: shortHelp,
                lines: lines,
            },
            stage: stage,
        }).then(res => {
            const name = names.join(' ');
            if (name === commandGroup.names.join(' ')) {
                const cmdGroup = DecodeResponseCommandGroup(res.data);
                this.setState({
                    updating: false,
                })
                this.props.onClose(cmdGroup);
            } else {
                // Rename command Group
                axios.post(`${nodeUrl}/Rename`, {
                    name: name
                }).then(res => {
                    const cmdGroup = DecodeResponseCommandGroup(res.data);
                    this.setState({
                        updating: false,
                    })
                    this.props.onClose(cmdGroup);
                })
            }
        })
            .catch(err => {
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
                <DialogTitle>Command Group</DialogTitle>
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

export default WSEditorCommandGroupContent;

export { DecodeResponseCommandGroup };
export type { CommandGroup, ResponseCommandGroup, ResponseCommandGroups };

