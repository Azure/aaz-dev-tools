import * as React from 'react';
import { Typography, Box, Link } from '@mui/material';
import { styled } from '@mui/material/styles';

import withRoot from '../../withRoot';
import { AppAppBar } from '../../components/AppAppBar';
import PageLayout from '../../components/PageLayout';


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
                        <Box sx={{ flexGrow: 5 }} />
                    </Box>
                </PageLayout>
            </React.Fragment>
        )
    }
}

export default withRoot(HomePage);
