import * as React from 'react';
import { Typography, Box, Link } from '@mui/material';
import { styled } from '@mui/material/styles';

import withRoot from '../../withRoot';
import { AppAppBar } from '../../components/AppAppBar';
import PageLayout from '../../components/PageLayout';


const TopPadding = styled(Box)(({ theme }) => ({
    [theme.breakpoints.up('sm')]: {
        height: '12vh',
    },
}));

const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '6vh'
}));


class HomePage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'HomePage'} />
                <PageLayout>
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        flexDirection: 'column',
                    }}>
                        <TopPadding />
                        <Typography variant='h2' gutterBottom>
                            Welcome to
                        </Typography>
                        <Typography variant='h2' gutterBottom>
                            AAZ Development Tool
                        </Typography>
                        <MiddlePadding />
                        <Typography variant="h6" align="center" gutterBottom>

                            {'Convert Swagger to Command Model? '}
                            <Link
                                href="/?#/Workspace"
                                align="center"
                                underline="always"
                            >
                                Workspace
                            </Link>
                        </Typography>
                        <Typography variant="h6" align="center" gutterBottom>
                            {'Convert Command Model to Code? '}
                            <Link
                                href="/?#/Generation"
                                align="center"
                                underline="always"
                            >
                                Generation
                            </Link>
                        </Typography>
                    </Box>
                </PageLayout>
            </React.Fragment>
        )
    }
}

export default withRoot(HomePage);
