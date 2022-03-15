import * as React from 'react';
import {Typography, Box, Link } from '@mui/material';
import { styled } from '@mui/material/styles';
import WorkspaceSelector from './WorkspaceSelector';

const TopPadding = styled(Box)(({ theme }) => ({
    [theme.breakpoints.up('sm')]: {
        height: '20vh',
    },
}));

const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '6vh'
}));

const SpacePadding = styled(Box)(({ theme }) => ({
    width: '3vh'
}));


class WorkspaceInstruction extends React.Component {
    
    render() {
        return (
            <Box sx={{
                display: 'flex',
                alignItems: 'center',
                flexDirection: 'column',
            }}>
                <TopPadding />
                <Typography variant='h4' gutterBottom>
                    Please select a Workspace
                </Typography>
                <MiddlePadding />
                <WorkspaceSelector name='Open or create a workspace'/>
            </Box>
        )
    }
}

export default WorkspaceInstruction;
