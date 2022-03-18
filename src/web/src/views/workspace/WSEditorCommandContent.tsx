import { Box, Button, Card, CardActions, CardContent, InputBase, InputBaseProps, Typography, TypographyProps } from '@mui/material';
import { createTheme, styled } from '@mui/system';
import * as React from 'react';
import { Input } from 'reactstrap';


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
    workspaceUrl: string,
    command: Command
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

const LongHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 18,
    fontWeight: 400,
}))

const DecodeResponseCommand = (command: ResponseCommand): Command => {
    return {
        id: 'command:' + command.names.join('/'),
        names: command.names,
        help: command.help,
        stage: command.stage ?? "Stable",
    }
}

class WSEditorCommandContent extends React.Component<WSEditorCommandContentProps> {

    constructor(props: WSEditorCommandContentProps) {
        super(props);
    }

    onEdit = () => {

    }

    render() {
        const name = commandPrefix + this.props.command.names.join(' ');
        const shortHelp = this.props.command.help?.short;
        const longHelp = this.props.command.help?.lines?.join('\n');
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
                            <Typography sx={{ ml: 2, mr: 2, mt: 1, mb: 2 }}
                                variant='h6'
                            >
                                [ COMMAND ]
                            </Typography>
                            <NameTypography sx={{ ml: 2, mr: 2, mt: 1 }}>
                                {name}
                            </NameTypography>
                            {shortHelp && <ShortHelpTypography sx={{ ml: 8, mr: 2, mt: 2 }}> {shortHelp} </ShortHelpTypography>}
                            {longHelp && <LongHelpTypography sx={{ ml: 8, mr: 2, mt: 1, mb: 1 }}> {longHelp} </LongHelpTypography>}
                        </CardContent>
                        <CardActions sx={{
                            display: "flex",
                            flexDirection: "row-reverse"
                        }}>
                            <Button
                                variant='outlined' size="small" color='info'
                                onClick={this.onEdit}
                            >
                                <Typography variant='body2'>
                                    Edit
                                </Typography>
                            </Button>
                        </CardActions>
                    </Card>
                </Box>
            </React.Fragment>
        )
    }
}

export default WSEditorCommandContent;

export { DecodeResponseCommand };
export type { Command, ResponseCommand, ResponseCommands };

