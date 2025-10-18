import React from "react";
import { Outlet } from "react-router";

const CLIPage: React.FC = () => {
  return (
    <>
      <Outlet />
    </>
  );
};

export default CLIPage;
