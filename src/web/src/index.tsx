import React from "react";
import { createRoot } from "react-dom/client";
import { HashRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import "./index.css";
import App from "./App";
import HomePage from "./views/home/HomePage";
import WorkspacePage from "./views/workspace/WorkspacePage";
import WorkspaceInstruction from "./views/workspace/WorkspaceInstruction";
import { WSEditor } from "./views/workspace/WSEditor";
import CommandsPage from "./views/commands/CommandsPage";
import CLIPage from "./views/cli/CLIPage";
import CLIInstruction from "./views/cli/CLIInstruction";
import { CLIModuleGenerator } from "./views/cli/CLIModuleGenerator";
import theme from "./theme";
// import reportWebVitals from './reportWebVitals';

const container = document.getElementById("root");
const root = createRoot(container!);
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <HashRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<HomePage />} />
            <Route path="HomePage" element={<HomePage />} />
            <Route path="Workspace" element={<WorkspacePage />}>
              <Route index element={<WorkspaceInstruction />} />
              <Route path="Instruction" element={<WorkspaceInstruction />} />
              <Route path=":workspaceName" element={<WSEditor />} />
            </Route>
            <Route path="Commands" element={<CommandsPage />}></Route>
            <Route path="CLI" element={<CLIPage />}>
              <Route index element={<CLIInstruction />} />
              <Route path="Instruction" element={<CLIInstruction />}></Route>
              <Route path=":repoName/:moduleName" element={<CLIModuleGenerator />} />
            </Route>
          </Route>
        </Routes>
      </HashRouter>
    </ThemeProvider>
  </React.StrictMode>,
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();
