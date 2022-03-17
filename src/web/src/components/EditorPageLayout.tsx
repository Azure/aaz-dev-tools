import { Container, styled, Theme, Toolbar } from '@mui/material';
import { Box } from '@mui/system';
// import { SxProps } from '@mui/system';
import * as React from 'react';

const PageContainer = styled(Box)(({theme}) => ({
    color: theme.palette.common.white,
    position: 'absolute',
    left: '6vh',
    right: '6vh',
    top: 64,
    bottom: 0,
    display: 'flex',
    alignItems: 'stretch',
    flexDirection: 'row',
    justifyContent: 'flex-start',
}));


const Background = styled(Box)({
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    backgroundSize: 'cover',
    backgroundRepeat: 'no-repeat',
    zIndex: -2,
});


export default function EditorPageLayout(
    props: React.HTMLAttributes<HTMLDivElement>
) {
    const { children } = props;

    return (
        <React.Fragment >
            <PageContainer>
                {children}
            </PageContainer>
            <Background/>
        </React.Fragment>
    )
}

