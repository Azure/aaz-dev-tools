import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, HashRouter, Routes, Route } from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.css';
import './index.css';
import App from './App';
import HomePage from './views/home/HomePage';
import WorkspacePage from './views/workspace/WorkspacePage';
import WorkspaceInstruction from './views/workspace/WorkspaceInstruction';
import WorkspaceEditor from './views/workspace/WorkspaceEditor';
import CommandsPage from './views/commands/CommandsPage';
import GenerationPage from './views/generation/GenerationPage';
import GenerationInstruction from './views/generation/GenerationInstruction';
import GenerationModuleEditor from './views/generation/GenerationModuleEditor';
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
            <Route path="Instruction" element={<WorkspaceInstruction />}/>
            <Route path=":workspaceName" element={<WorkspaceEditor />} />
          </Route>
          <Route path="Commands" element={<CommandsPage />}>
          </Route>
          <Route path="Generation" element={<GenerationPage />}>
            <Route index element={<GenerationInstruction />} />
            <Route path="Instruction" element={<GenerationInstruction />} > 
            </Route>
            <Route path=":repoName/:moduleName" element={<GenerationModuleEditor />} />
          </Route>
        </Route>
        {/* <Route path="workspace" element={<Workspace />}>
            <Route index element={<WorkspaceSelector/>}/>
            <Route path=":workspaceName/resourceSelection" element={<SpecSelector />}/>
            <Route path=":workspaceName" element={<ConfigEditor />} />
          </Route>
          <Route path="generator" element={<Generator/>}>
            <Route index element={<TargetSelector/>}/>
          </Route> */}
      </Routes>
    </HashRouter>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();
