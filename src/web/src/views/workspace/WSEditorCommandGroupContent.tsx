import { Box, Button, Card, CardActions, CardContent, Typography } from '@mui/material';
import { display } from '@mui/system';
import * as React from 'react';

interface CommandGroup {
    // commandGroups?: CommandGroups,
    // commands?: Commands,
    id: string
    names: string[]
    help?: {
        short: string
        lines?: string[]
    }

}

interface WSEditorCommandGroupContentProps {
    commandGroup: CommandGroup
}

interface WSEditorCommandGroupContentState {

}

const commandPrefix = 'Az '

class WSEditorCommandGroupContent extends React.Component<WSEditorCommandGroupContentProps, WSEditorCommandGroupContentState> {

    constructor(props: WSEditorCommandGroupContentProps) {
        super(props);
        this.state = {

        };
    }

    render() {
        const { commandGroup } = this.props
        return (
            <Box sx={{
                 display: 'flex',
                 justifyContent: 'stretch',
                 }}>
                <Card variant="outlined" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flex: '1 0 auto'}}>
                        <Typography
                        variant='h6'
                        
                        >
                            [ COMMAND GROUP ]
                        </Typography>
                        <Typography
                            variant='h4'
                            color='inherit'
                            sx= {{
                                p: 1
                            }}
                            >
                            {commandPrefix + commandGroup.names.join(' ')}
                        </Typography>
                    </CardContent>
                    <CardActions sx={{
                        display: "flex",
                        flexDirection: "row-reverse"
                    }}>
                        <Button variant='outlined' size="small" color='info'>
                            <Typography variant='body2'>
                            Edit
                            </Typography>
                            </Button>
                    </CardActions>
                </Card>
            </Box>
        )
    }

}

export default WSEditorCommandGroupContent;

export type { CommandGroup };

