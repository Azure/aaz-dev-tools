import * as React from 'react';
import withRoot from '../../withRoot';
import { Outlet } from 'react-router';
import { AppAppBar } from '../../components/AppAppBar';


class DocumentsPage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'Documents'} />
                <Outlet />
            </React.Fragment>
        )
    }
}

export default withRoot(DocumentsPage);
