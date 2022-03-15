import * as React from 'react';
import {Typography, Box, Link } from '@mui/material';
import { styled } from '@mui/material/styles';
import CLIModuleSelector from './CLIModuleSelector';

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

class GenerationInstruction extends React.Component {
    
    render() {
        return (
            <Box sx={{
                display: 'flex',
                alignItems: 'center',
                flexDirection: 'column',
            }}>
                <TopPadding />
                <Typography variant='h4' gutterBottom>
                    Please select a CLI Module
                </Typography>
                <MiddlePadding />
                <Box sx={{
                    flex: 1,
                    display: "flex",
                    flexDirection: 'row',
                    alignItems: "center"
                }}>
                <CLIModuleSelector repo='Main' name='Azure Cli Module' />
                <SpacePadding/>
                <Typography variant='h6' gutterBottom>
                    Or
                </Typography>
                <SpacePadding/>
                <CLIModuleSelector repo='Extension' name='Azure Cli Extension Module' />
                </Box>
            </Box>
        )
    }
}

export default GenerationInstruction;
