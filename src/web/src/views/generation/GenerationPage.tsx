import * as React from 'react';
import withRoot from '../../withRoot';
import { Outlet } from 'react-router';

class GenerationPage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <Outlet />
            </React.Fragment>
        )
    }
}

export default withRoot(GenerationPage);
