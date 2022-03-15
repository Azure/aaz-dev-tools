import * as React from 'react';
import { Typography } from '@mui/material';
import withRoot from '../withRoot';
import { AppAppBar } from '../components/AppAppBar';

class WorkspacePage extends React.Component {

    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'Workspace'}/>
                {/* <Typography variant='h1' gutterBottom>
                    Welcome to WorkspacePage
                </Typography> */}
            </React.Fragment>
        )
    }
}

export default withRoot(WorkspacePage);
