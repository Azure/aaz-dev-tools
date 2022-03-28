import { BorderColor } from '@mui/icons-material';
import { AppBar, Button, Container, IconButton, styled, Theme, Toolbar, Typography, Tooltip } from '@mui/material';
import { borderBottom, Box } from '@mui/system';
import HomeIcon from '@mui/icons-material/Home';

import * as React from 'react';


interface WSEditorToolBarProps {
    workspaceName: string
    onHomePage: () => void
    onGenerate: () => void
}


const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '6vh'
}));

class WSEditorToolBar extends React.Component<WSEditorToolBarProps> {

    render() {
        const { workspaceName, onHomePage, onGenerate } = this.props;
        return (
            <React.Fragment>
                <AppBar sx={{
                    position: "fixed",
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                }}>
                    <Toolbar sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: "flex-start",
                        height: 64,
                    }}>
                        <IconButton
                            color='inherit'
                            onClick={onHomePage}
                            aria-label='home'
                            sx={{ mr: 2, flexShrink: 0 }}
                        >
                            <HomeIcon sx={{ mr: 2 }} />
                            <Typography
                                variant='h6'
                                component='div'
                                color='inherit'
                                sx={{ mr: 2 }}
                            >
                                WORKSPACE
                            </Typography>
                        </IconButton>

                        <Typography
                            variant='h5'
                            component='div'
                            color='inherit'

                        >
                            {workspaceName}
                        </Typography>

                        <Box sx={{ flexGrow: 1 }} />
                        <Box sx={{ flexShrink: 0 }} >
                       
                            <Tooltip title='Export Command Models'>
                                <Button
                                    variant="outlined"
                                    color='inherit'
                                    onClick={onGenerate}
                                >
                                    Export
                                </Button>
                            </Tooltip>

                        </Box>
                    </Toolbar>
                </AppBar>
            </React.Fragment>
        )
    }

}


export default WSEditorToolBar;
