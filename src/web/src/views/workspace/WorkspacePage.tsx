import React from "react";
import withRoot from "../../withRoot";
import { Outlet } from "react-router";

const WorkspacePage: React.FC = () => {
  return (
    <React.Fragment>
      <Outlet />
    </React.Fragment>
  );
};

export default withRoot(WorkspacePage);
