import * as React from 'react';
import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import { AppBar, Toolbar } from '@mui/material';
import theme from '../theme';



type AppAppBarProps = {
    pageName: string | null,
};


class AppAppBar extends React.Component<AppAppBarProps> {

    constructor(props: AppAppBarProps) {
        super(props);
    }

    render() {

        return (
            <div>
                <AppBar position='fixed'>
                    <Toolbar sx={{ justifyContent: "space-between", height: 64 }}>
                        <Box sx={{ flex: 1, display: 'flex', justifyContent: "flex-start", alignItems: "center"}} >
                        <Link
                            variant="h6"
                            underline="none"
                            color="inherit"
                            
                            href="/?#/HomePage"
                            fontWeight={
                                this.props.pageName == "HomePage" ? 
                                theme.typography.fontWeightMedium : 
                                theme.typography.fontWeightLight
                            }
                        >
                            {'Home'}
                        </Link>
                        <Box sx={{ p: 4}}/>
                        <Link
                            variant="h6"
                            underline="none"
                            color="inherit"
                            href="/?#/Workspace"
                            fontWeight={
                                this.props.pageName == "Workspace" ? 
                                theme.typography.fontWeightMedium : 
                                theme.typography.fontWeightLight
                            }
                        >
                            {'Workspace'}
                        </Link>
                        {/* <Box sx={{ p: 4}}/>
                        <Link
                            variant="h6"
                            underline="none"
                            color="inherit"
                            href="/?#/Commands"
                            fontWeight={
                                this.props.pageName == "Commands" ? 
                                theme.typography.fontWeightMedium : 
                                theme.typography.fontWeightLight
                            }
                        >
                            {'Commands'}
                        </Link> */}
                        <Box sx={{ p: 4}}/>
                        <Link
                            variant="h6"
                            underline="none"
                            color="inherit"
                            href="/?#/Generation"
                            fontWeight={
                                this.props.pageName == "Generation" ? 
                                theme.typography.fontWeightMedium : 
                                theme.typography.fontWeightLight
                            }
                        >
                            {'CLI'}
                        </Link>
                        </Box>
                        
                        <Box sx={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
                            <Link
                                color="inherit"
                                variant="h6"
                                underline="none"
                                href="/?#/Documents"
                                fontWeight={
                                    this.props.pageName == "Documents" ?
                                    theme.typography.fontWeightMedium : 
                                    theme.typography.fontWeightLight
                                }
                                sx={{
                                    fontSize: 16,
                                    color: 'common.white',
                                    ml: 3,
                                }}
                            >
                                {'Docs'}
                            </Link>
                        </Box>
                    </Toolbar>
                </AppBar>
            </div>
        );
    }
}

export { AppAppBar };