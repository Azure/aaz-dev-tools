// import React, { Component } from "react";
import { Routes, Route, useParams} from "react-router-dom";
import * as React from 'react';

import HomePage from "./views/HomePage";
import WorkspacePage from "./views/WorkspacePage";
import GenerationPage from "./views/GenerationPage";
import CommandsPage from "./views/CommandsPage";


class App extends React.Component {
  render() {
    return (
      <main>
        <Routes>
          <Route path="/" element={<HomePage />}/>
          <Route path="/Workspace" element={<WorkspacePage />}>
            {/* <Route index element={}></Route> */}
          </Route>
          <Route path="/Commands" element={<CommandsPage />}>
            
          </Route>
          <Route path="/Generation" element={<GenerationPage />}>

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
      </main>
    );
  }
}

export default App;