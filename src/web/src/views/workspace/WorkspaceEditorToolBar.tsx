import { BorderColor } from '@mui/icons-material';
import { AppBar, Container, styled, Theme, Toolbar } from '@mui/material';
import { borderBottom, Box } from '@mui/system';
// import { SxProps } from '@mui/system';
import * as React from 'react';


interface WorkspaceEditorToolBarProps {
    workspaceName: string
    onHomePage: () => void
    onLayout: () => void
}


class WorkspaceEditorToolBar extends React.Component<WorkspaceEditorToolBarProps> {

    render() {
        return (
            <React.Fragment>
                <AppBar sx={{ position: "fixed" }}>
                    <Toolbar sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: "space-between",
                        height: 64
                    }}>
                    </Toolbar>
                </AppBar>
            </React.Fragment>
        )
    }

}


export default WorkspaceEditorToolBar;
