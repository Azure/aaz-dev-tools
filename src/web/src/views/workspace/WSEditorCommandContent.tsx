import { Box, Button, Card, CardActions, CardContent, Typography } from '@mui/material';
import * as React from 'react';


interface Command {
    id: string
    names: string[]
    help?: {
        short: string
        lines?: string[]
    }
    // examples?: ExampleType[],
    // argGroups?: ArgGroups
}

interface WSEditorCommandContentProps {
    command: Command
}

interface WSEditorCommandContentState {
}

const commandPrefix = 'Az '

class WSEditorCommandContent extends React.Component<WSEditorCommandContentProps, WSEditorCommandContentState> {

    constructor(props: WSEditorCommandContentProps) {
        super(props);
        this.state = {

        };
    }

    render() {
        const { command } = this.props;        
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
                           [ COMMAND ]
                       </Typography>
                       <Typography
                           variant='h4'
                           color='inherit'
                           sx= {{
                               p: 1
                           }}
                           >
                           {commandPrefix + command.names.join(' ')}
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

export default WSEditorCommandContent;

export type { Command };

