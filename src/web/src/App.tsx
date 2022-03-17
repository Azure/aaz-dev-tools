// import React, { Component } from "react";
import { Routes, Route, useParams, Outlet} from "react-router-dom";
import * as React from 'react';

class App extends React.Component {
  render() {
    return (
      <Outlet />
    );
  }
}

export default App;