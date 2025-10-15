import React from "react";
import { Outlet } from "react-router";

const WorkspacePage: React.FC = () => {
  return (
    <React.Fragment>
      <Outlet />
    </React.Fragment>
  );
};

export default WorkspacePage;
