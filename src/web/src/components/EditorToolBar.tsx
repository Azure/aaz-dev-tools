import { BorderColor } from '@mui/icons-material';
import { AppBar, Container, styled, Theme, Toolbar } from '@mui/material';
import { borderBottom, Box } from '@mui/system';
// import { SxProps } from '@mui/system';
import * as React from 'react';

export default function EditorToolBar(
    props: React.HTMLAttributes<HTMLDivElement>
) {
    const { children } = props;
    return (
        <React.Fragment >
            <AppBar sx={{ position: "fixed" }}>
                <Toolbar sx={{ justifyContent: "space-between", height: 64 }}>
                    {children}
                </Toolbar>
            </AppBar>
        </React.Fragment>
    )
}