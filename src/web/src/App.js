import React, { Component } from "react";
import Modal from "./components/Modal";
import axios from "axios";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      customizationList: [],
      modal: false,
      activeItem: {
        module_name: "",
        module_path: "",
      },
      mgmtPlaneSpecs: null,
      dataPlaneSpecs: null
    };
  }

  componentDidMount(){
    this.refreshList();
    this.listAllSpecs();
  }

  refreshList = () => {
    axios
      .get("/api/customizations/")
      .then((res) => this.setState({ customizationList: res.data }))
      .catch((err) => console.log(err));
  };

  listAllSpecs = () => {
    axios
      .get("/api/specifications")
      .then((res) => this.setState({ mgmtPlaneSpecs: res.data[0], dataPlaneSpecs: res.data[1]}))
      .catch((err) => console.log(err));
  };

  toggle = () => {
    this.setState({ modal: !this.state.modal });
  };

  handleSubmit = (item) => {
    this.toggle();
    if (item.id) {
      axios
        .put(`/api/customizations/${item.id}/`, item)
        .then((res) => this.refreshList());
      return;
    }
    axios
      .post("/api/customizations/", item)
      .then((res) => this.refreshList());
  };

  handleDelete = (item) => {
    axios
      .delete(`/api/customizations/${item.id}/`)
      .then((res) => this.refreshList());
  };

  createItem = () => {
    const item = { module_name: "", module_path: ""};

    this.setState({ activeItem: item, modal: !this.state.modal });
  };

  editItem = (item) => {
    this.setState({ activeItem: item, modal: !this.state.modal });
  };


  renderTabList = () => {
    return (
      <div className="nav nav-tabs">
        <span
          className="nav-link"
        >
          Configurations
        </span>
      </div>
    );
  };

  renderItems = () => {
    const newItems = this.state.customizationList;

    return newItems.map((item) => (
      <li
        key={item.id}
        className="list-group-item d-flex justify-content-between align-items-center"
      >
        <span
          className={`customization-title mr-2`}
          title={item.module_name}
        >
          {item.module_path}
        </span>
        <span>
          <button
            className="btn btn-secondary mr-2"
            onClick={() => this.editItem(item)}
          >
            Edit
          </button>
          <button
            className="btn btn-danger"
            onClick={() => this.handleDelete(item)}
          >
            Delete
          </button>
        </span>
      </li>
    ));
  };

  render() {
    return (
      <main className="container">
        <h1 className="text-white text-uppercase text-center my-4">customization app</h1>
        <div className="row">
          <div className="col-md-6 col-sm-10 mx-auto p-0">
            <div className="card p-3">
              <div className="mb-4">
                <button
                  className="btn btn-primary"
                  onClick={this.createItem}
                >
                  Add task
                </button>
              </div>
              {this.renderTabList()}
              <ul className="list-group list-group-flush border-top-0">
                {this.renderItems()}
              </ul>
            </div>
          </div>
        </div>
        {this.state.modal ? (
          <Modal
            activeItem={this.state.activeItem}
            toggle={this.toggle}
            onSave={this.handleSubmit}
          />
        ) : null}
      </main>
    );
  }
}

export default App;