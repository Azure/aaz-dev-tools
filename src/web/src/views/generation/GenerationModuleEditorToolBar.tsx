import { BorderColor } from '@mui/icons-material';
import { AppBar, Button, Container, IconButton, styled, Theme, Toolbar, Typography, Tooltip } from '@mui/material';
import { borderBottom, Box } from '@mui/system';
// import { SxProps } from '@mui/system';
import HomeIcon from '@mui/icons-material/Home';
import AddIcon from '@mui/icons-material/Add';

import * as React from 'react';


interface GenerationModuleEditorToolBarProps {
  moduleName: string
  onHomePage: () => void
  onGenerate: () => void
}


const MiddlePadding = styled(Box)(({ theme }) => ({
  height: '6vh'
}));

class GenerationModuleEditorToolBar extends React.Component<GenerationModuleEditorToolBarProps> {

  render() {
    const { moduleName, onHomePage, onGenerate } = this.props;
    return (
        <React.Fragment>
          <AppBar sx={{ position: "fixed" }}>
            <Toolbar sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: "flex-start",
              height: 64
            }}>
              <IconButton
                  color='inherit'
                  onClick={onHomePage}
                  aria-label='home'
                  sx={{ mr: 2, flexShrink: 0 }}
              >
                <HomeIcon sx={{ mr: 2 }} />
                <Typography
                    variant='h6'
                    component='div'
                    color='inherit'
                    sx={{ mr: 2 }}
                >
                  GENERATION
                </Typography>
              </IconButton>

              <Typography
                  variant='h5'
                  component='div'
                  color='inherit'
              >
                {moduleName}
              </Typography>

              <Box sx={{ flexGrow: 1 }} />
              <Box sx={{ flexShrink: 0 }} >
                <Tooltip title='Generate CLI Commands'>
                  <Button
                      variant="outlined"
                      color='inherit'
                      onClick={onGenerate}
                  >
                    Generate
                  </Button>
                </Tooltip>

              </Box>
            </Toolbar>
          </AppBar>
        </React.Fragment>
    )
  }

}


export default GenerationModuleEditorToolBar;