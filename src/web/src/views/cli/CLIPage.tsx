import * as React from "react";
import { Outlet } from "react-router";

class CLIPage extends React.Component {
  render() {
    return (
      <React.Fragment>
        <Outlet />
      </React.Fragment>
    );
  }
}

export default CLIPage;
