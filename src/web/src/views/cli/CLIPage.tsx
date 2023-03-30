import * as React from 'react';
import withRoot from '../../withRoot';
import { Outlet } from 'react-router';

class CLIPage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <Outlet />
            </React.Fragment>
        )
    }
}

export default withRoot(CLIPage);
