import * as React from 'react';
import { Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import WorkspaceSelector from './WorkspaceSelector';
import { AppAppBar } from '../../components/AppAppBar';
import PageLayout from '../../components/PageLayout';


const MiddlePadding = styled(Box)(() => ({
    height: '6vh'
}));

class WorkspaceInstruction extends React.Component {
    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'Workspace'} />
                <PageLayout>
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        flexDirection: 'column',
                        justifyContent: 'center',
                    }}>
                        <Box sx={{ flexGrow: 3 }} />
                        <Box sx={{
                            flexGrow: 3,
                            flexShrink: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexDirection: 'column'
                        }}>
                            <Typography variant='h3' gutterBottom>
                                Please select a Workspace
                            </Typography>
                            <MiddlePadding />
                            <WorkspaceSelector name='Open or create a workspace' />
                        </Box>
                        <Box sx={{ flexGrow: 5 }} />
                    </Box>
                </PageLayout>
            </React.Fragment>
        )
    }
}

export default WorkspaceInstruction;
