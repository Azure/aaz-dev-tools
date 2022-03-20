import { Component, useState } from "react";
import axios from "axios";
import { Modal, Row, Col, Button, Form } from "react-bootstrap";
import { Typeahead } from "react-bootstrap-typeahead";
import type { Option } from "react-bootstrap-typeahead/types/types";
import "./TargetSelector.css";

const RepoMap = {
  "Azure CLI": "Main",
  "Azure CLI Extension": "Extension",
};

type Module = {
  folder: string;
  name: string;
  url: string;
};

type TargetSelectorState = {
  currMode: "initial" | "search" | "create";
  currRepo: "Azure CLI" | "Azure CLI Extension";
  modules: Module[];
  moduleName: string;
};

export default class TargetSelector extends Component<
  any,
  TargetSelectorState
> {
  constructor(props: any) {
    super(props);
    this.state = {
      currMode: "initial",
      currRepo: "Azure CLI",
      modules: [],
      moduleName: "",
    };
  }

  SelectTarget = () => {
    const handleClick = (event: any) => {
      const targetName = event.target.innerText;
      this.setState({ currRepo: targetName });
      const currRepo = RepoMap[this.state.currRepo];
      axios.get(`/CLI/Az/${currRepo}/Modules`).then((res) => {
        this.setState({
          modules: res.data.map((module: any) => {
            return {
              folder: module.folder,
              name: module.name,
              url: module.url,
            };
          }),
        });
      });
      this.setState({ currMode: "search" });
    };

    const handleClose = () => {
      window.location.href = "/";
    };

    return (
      <div>
        <Modal
          show={this.state.currMode === "initial"}
          onHide={handleClose}
          dialogClassName="target-dialog"
          contentClassName="target-content"
          centered
        >
          <Modal.Header className="target-header" closeButton>
            <Modal.Title className="target-title">
              Welcome to CodeGen 2.0
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="d-grid gap-2">
              <Button
                variant="secondary"
                size="lg"
                onClick={handleClick}
                className="cli"
              >
                Azure CLI
              </Button>
              <Button variant="secondary" size="lg" onClick={handleClick}>
                Azure CLI Extension
              </Button>
            </div>
          </Modal.Body>
        </Modal>
      </div>
    );
  };

  SearchTarget = () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [singleSelections, setSingleSelections] = useState([] as Option[]);

    const handleOptionSelection = (options: Option[]) => {
      setSingleSelections(options);
      this.setState({ moduleName: String(options[0]) });
    };

    const handleSubmit = (event: any) => {
      event.preventDefault();
      event.stopPropagation();

      window.location.href = `/module/${this.state.currRepo}/${this.state.moduleName}`;
    };

    return (
      <div>
        <Modal
          show={this.state.currMode === "search"}
          dialogClassName="target-dialog"
          contentClassName="target-content"
          centered
        >
          <Modal.Header className="target-header">
            <Modal.Title className="target-title">
              Welcome to CodeGen 2.0
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col sm={8}>
                <Form
                  id="moduleName"
                  onSubmit={handleSubmit}
                  className="search"
                >
                  <Typeahead
                    id="basic-typeahead-single"
                    labelKey="name"
                    onChange={handleOptionSelection}
                    options={this.state.modules.map((module) => {
                      return module.name;
                    })}
                    placeholder="Search modules"
                    selected={singleSelections}
                  />
                </Form>
              </Col>
              <Col sm={4}>
                <Button
                  variant="secondary"
                  onClick={() => this.setState({ currMode: "create" })}
                  className="module"
                >
                  New Module
                </Button>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer className="justify-content-right">
            <Button type="submit" form="moduleName" variant="primary">
              OK
            </Button>
            <Button
              variant="secondary"
              onClick={() => this.setState({ currMode: "initial" })}
            >
              Cancel
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  };

  NewTarget = () => {
    const handleSubmit = (event: any) => {
      event.preventDefault();
      event.stopPropagation();

      const currRepo = RepoMap[this.state.currRepo];
      const moduleName = event.target[0].value;
      axios
        .post(`/CLI/Az/${currRepo}/Modules`, { name: moduleName })
        .then((res) => {
          this.setState({
            modules: res.data.map((module: any) => {
              return {
                folder: module.folder,
                name: module.name,
                url: module.url,
              };
            }),
          });
        });

      window.location.href = `/module/${this.state.currRepo}/${moduleName}`;
    };

    return (
      <div>
        <Modal
          show={this.state.currMode === "create"}
          dialogClassName="target-dialog"
          contentClassName="target-content"
          centered
        >
          <Modal.Header className="target-header">
            <Modal.Title className="target-title">
              Welcome to CodeGen 2.0
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form id="newTargetForm" onSubmit={handleSubmit}>
              <Form.Group>
                <Form.Label>Module Name:</Form.Label>
                <Form.Control type="text" required />
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer className="justify-content-right">
            <Button type="submit" form="newTargetForm" variant="primary">
              Create
            </Button>
            <Button
              variant="secondary"
              onClick={() => this.setState({ currMode: "search" })}
            >
              Cancel
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  };

  render() {
    return (
      <div>
        <this.SelectTarget />
        <this.SearchTarget />
        <this.NewTarget />
      </div>
    );
  }
}
