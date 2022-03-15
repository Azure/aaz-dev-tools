import { Container, styled, Theme, Toolbar } from '@mui/material';
import { Box } from '@mui/system';
// import { SxProps } from '@mui/system';
import * as React from 'react';

const PageContainer = styled(Container)(({theme}) => ({
    color: theme.palette.common.white,
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
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


export default function PageLayout(
    props: React.HTMLAttributes<HTMLDivElement>
) {
    const { children } = props;

    return (
        <React.Fragment >
            <Toolbar />
            <PageContainer>
                {children}
            </PageContainer>
            <Background/>
        </React.Fragment>
    )
}

