import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter, Routes, Route } from "react-router-dom";
import './index.css';
import App from './App';
import HomePage from './views/home/HomePage';
import WorkspacePage from './views/workspace/WorkspacePage';
import WorkspaceInstruction from './views/workspace/WorkspaceInstruction';
import { WSEditor } from './views/workspace/WSEditor';
import CommandsPage from './views/commands/CommandsPage';
import CLIPage from './views/cli/CLIPage';
import CLIInstruction from './views/cli/CLIInstruction';
import { CLIModuleGenerator } from './views/cli/CLIModuleGenerator';
// import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
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
          <Route path="Commands" element={<CommandsPage />}>
          </Route>
          <Route path="CLI" element={<CLIPage />}>
            <Route index element={<CLIInstruction />} />
            <Route path="Instruction" element={<CLIInstruction />} >
            </Route>
            <Route path=":repoName/:moduleName" element={<CLIModuleGenerator />} />
          </Route>
        </Route>
      </Routes>
    </HashRouter>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();
