import * as React from 'react';
import { Typography } from '@mui/material';
import withRoot from '../withRoot';
import { AppAppBar } from '../components/AppAppBar';

class GenerationPage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'Generation'}/>
                {/* <Typography variant='h1' gutterBottom>
                    Generation Page
                </Typography> */}
            </React.Fragment>
        )
    }
}

export default withRoot(GenerationPage);
