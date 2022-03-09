import React, { Component } from "react";
import { Routes, Route, useParams} from "react-router-dom";
import { Modal, Button } from "react-bootstrap"

import Generator from "./components/Generator"
import WorkspaceSelector from "./components/WorkspaceSelector"
import TargetSelector from "./components/TargetSelector"
import {SpecSelector} from "./components/SpecSelector";
import Workspace from "./components/Workspace";
import {ConfigEditor} from "./components/ConfigEditor";

class App extends Component {
  ModeSelection = () => {
    return <div className="container-fluid row">
      <Modal show="true" size='sm' centered >
        <Modal.Body>
          <div className="row">
            <div className="col text-center">
              <Button href="workspace" variant="dark">Editor</Button>
            </div>
          </div>
          <br />
          <div className="row">
            <div className="col text-center">
              <Button href="module" variant="dark">Generator</Button>
            </div>
          </div>

        </Modal.Body>
      </Modal>
    </div>
  }

  


  render() {
    return (
      <main>
        <Routes>
          <Route path="/" element={<this.ModeSelection />}/>
          <Route path="workspace" element={<Workspace />}>
            <Route index element={<WorkspaceSelector/>}/>
            {/* <Route path=":workspaceName/resourceSelection" element={<SpecSelector />}/> */}
            <Route path=":workspaceName" element={<ConfigEditor />} />
          </Route>
          <Route path="module" element={<TargetSelector/>}/>
          <Route path="module/generator" element={<Generator/>}/>
        </Routes>
      </main>
    );
  }
}

export default App;