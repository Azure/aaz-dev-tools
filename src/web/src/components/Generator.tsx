import {Component} from "react";
import {Outlet} from "react-router-dom";

export default class Generator extends Component {
  render() {
    return (
      <div>
        <Outlet/>
      </div>
    )
  }
}
