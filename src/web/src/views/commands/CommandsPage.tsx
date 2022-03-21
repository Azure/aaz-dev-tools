import * as React from 'react';
import withRoot from '../../withRoot';
import { AppAppBar } from '../../components/AppAppBar';

class CommandsPage extends React.Component {
    render() {
        return (
            <React.Fragment>
                <AppAppBar pageName={'Commands'} />
                {/* <Typography variant='h1' gutterBottom>
                    Commands Page
                </Typography> */}
            </React.Fragment>
        )
    }
}

export default withRoot(CommandsPage);
