import React from "react";
import { Typography, Box } from "@mui/material";
import { styled } from "@mui/material/styles";
import CLIModuleSelector from "./CLIModuleSelector";
import { AppNavBar } from "../../../components/AppNavBar";
import PageLayout from "../../../components/PageLayout";

const MiddlePadding = styled(Box)(() => ({
  height: "6vh",
}));

const SpacePadding = styled(Box)(() => ({
  width: "3vh",
}));

const CLIInstruction: React.FC = () => {
  return (
    <>
      <AppNavBar pageName="CLI" />
      <PageLayout>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <Box sx={{ flexGrow: 3 }} />
          <Box
            sx={{
              flexGrow: 3,
              flexShrink: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
            }}
          >
            <Typography variant="h3" gutterBottom>
              Please select a CLI Module
            </Typography>
            <MiddlePadding />
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
              }}
            >
              <CLIModuleSelector repo="Main" name="Azure CLI Module" />
              <SpacePadding />
              <Typography variant="h6" gutterBottom>
                Or
              </Typography>
              <SpacePadding />
              <CLIModuleSelector repo="Extension" name="Azure CLI Extension Module" />
            </Box>
          </Box>
          <Box sx={{ flexGrow: 5 }} />
        </Box>
      </PageLayout>
    </>
  );
};

export default CLIInstruction;
