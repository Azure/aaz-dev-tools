import { AppBar, Button, IconButton, styled, Toolbar, Typography, Tooltip, TypographyProps } from '@mui/material';
import { Box } from '@mui/system';
import HomeIcon from '@mui/icons-material/Home';
import EditIcon from '@mui/icons-material/Edit';
import { grey } from '@mui/material/colors'

import * as React from 'react';


const ArgEditTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: "#ffffff",
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}));

interface WSEditorToolBarProps {
    workspaceName: string
    onHomePage: () => void
    onGenerate: () => void
    onDelete: () => void
    onModify: () => void
}

class WSEditorToolBar extends React.Component<WSEditorToolBarProps> {

    render() {
        const { workspaceName, onHomePage, onGenerate, onDelete, onModify } = this.props;
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
                        <Button sx={{ flexShrink: 0, ml: 3 }}
                            startIcon={<EditIcon sx={{ color: grey[100] }} fontSize='small' />}
                            onClick={onModify}
                        >
                            <ArgEditTypography>Edit</ArgEditTypography>
                        </Button>
                        <Box sx={{ marginLeft: '20px' }} >
                            <Tooltip title='Delete Workspace'>
                                <Button
                                    variant="outlined"
                                    color='inherit'
                                    onClick={onDelete}
                                >
                                    Delete
                                </Button>
                            </Tooltip>
                        </Box>

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
