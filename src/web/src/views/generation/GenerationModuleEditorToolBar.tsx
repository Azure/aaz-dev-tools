import * as React from "react";
import {
  AppBar,
  Button,
  IconButton,
  Toolbar,
  Typography,
  Tooltip,
} from "@mui/material";
import { Box } from "@mui/system";
import HomeIcon from "@mui/icons-material/Home";

interface GenerationModuleEditorToolBarProps {
  moduleName: string;
  onHomePage: () => void;
  onGenerate: () => void;
}

class GenerationModuleEditorToolBar extends React.Component<GenerationModuleEditorToolBarProps> {
  render() {
    const { moduleName, onHomePage, onGenerate } = this.props;
    return (
      <React.Fragment>
        <AppBar
          sx={{ position: "fixed", zIndex: (theme) => theme.zIndex.drawer + 1 }}
        >
          <Toolbar
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-start",
              height: 64,
            }}
          >
            <IconButton
              color="inherit"
              onClick={onHomePage}
              aria-label="home"
              sx={{ mr: 2, flexShrink: 0 }}
            >
              <HomeIcon sx={{ mr: 2 }} />
              <Typography
                variant="h6"
                component="div"
                color="inherit"
                sx={{ mr: 2 }}
              >
                GENERATION
              </Typography>
            </IconButton>

            <Typography variant="h5" component="div" color="inherit">
              {moduleName}
            </Typography>

            <Box sx={{ flexGrow: 1 }} />
            <Box sx={{ flexShrink: 0 }}>
              <Tooltip title="Generate CLI Commands">
                <Button variant="outlined" color="inherit" onClick={onGenerate}>
                  Generate
                </Button>
              </Tooltip>
            </Box>
          </Toolbar>
        </AppBar>
      </React.Fragment>
    );
  }
}

export default GenerationModuleEditorToolBar;
