import { FC } from "react";
import { Outlet } from "react-router";

const CLIPage: FC = () => {
  return (
    <>
      <Outlet />
    </>
  );
};

export default CLIPage;
