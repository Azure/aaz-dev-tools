import * as React from 'react';
import { Typography } from '@mui/material';
import withRoot from '../../withRoot';
import { AppAppBar } from '../../components/AppAppBar';
import PageLayout from '../../components/PageLayout';
import { Outlet } from 'react-router';

class GenerationPage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'Generation'}/>
                <PageLayout>
                    <Outlet />
                </PageLayout>
            </React.Fragment>
        )
    }
}

export default withRoot(GenerationPage);
