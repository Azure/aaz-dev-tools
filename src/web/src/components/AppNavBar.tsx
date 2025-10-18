import React, { useState } from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import { AppBar, Toolbar } from "@mui/material";
import theme from "../theme";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";

type AppNavBarProps = {
  pageName: string | null;
};

const AppNavBar: React.FC<AppNavBarProps> = ({ pageName }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <div>
      <AppBar position="fixed">
        <Toolbar sx={{ justifyContent: "space-between", height: 64 }}>
          <Box sx={{ flex: 1, display: "flex", justifyContent: "flex-start", alignItems: "center" }}>
            <Link
              variant="h6"
              underline="none"
              color="inherit"
              href="/?#/HomePage"
              fontWeight={
                pageName === "HomePage" ? theme.typography.fontWeightMedium : theme.typography.fontWeightLight
              }
            >
              Home
            </Link>
            <Box sx={{ p: 4 }} />
            <Link
              variant="h6"
              underline="none"
              color="inherit"
              href="/?#/Workspace"
              fontWeight={
                pageName === "Workspace" ? theme.typography.fontWeightMedium : theme.typography.fontWeightLight
              }
            >
              Workspace
            </Link>
            <Box sx={{ p: 4 }} />
            <Link
              variant="h6"
              underline="none"
              color="inherit"
              href="/?#/CLI"
              fontWeight={pageName === "CLI" ? theme.typography.fontWeightMedium : theme.typography.fontWeightLight}
            >
              CLI
            </Link>
          </Box>

          <Button
            color="inherit"
            sx={{
              fontSize: "18px",
              fontFamily: "Roboto Condensed, sans-serif",
            }}
            onClick={handleMenuOpen}
          >
            Help
          </Button>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
            <MenuItem
              onClick={handleMenuClose}
              component="a"
              href="https://azure.github.io/aaz-dev-tools/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Document
            </MenuItem>
            <MenuItem
              onClick={handleMenuClose}
              component="a"
              href="https://forms.office.com/r/j6rQuFUqUf?origin=lprLink"
              target="_blank"
              rel="noopener noreferrer"
            >
              Send a Feedback
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
    </div>
  );
};

export { AppNavBar };
