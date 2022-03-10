import {Component, useState} from "react";
import axios from "axios";
import {Modal, Row, Col, ButtonGroup, ToggleButton, Button, Form} from "react-bootstrap";
import {Typeahead} from 'react-bootstrap-typeahead';
import type {Option} from "react-bootstrap-typeahead/types/types"
import "./TargetSelector.css";


type Module = {
  folder: string,
  name: string,
  url: string
}


type TargetSelectorState = {
  isNew: boolean,
  currRepo: string,
  modules: Module[],
  moduleName: string
}

export default class TargetSelector extends Component<any, TargetSelectorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      isNew: false,
      currRepo: "",
      modules: [],
      moduleName: "",
    }
  }

  handleSubmit = (event: any) => {
    event.preventDefault();
    event.stopPropagation();

    window.location.href = `/module/${this.state.currRepo}/${this.state.moduleName}`
  }

  SelectTarget = () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [singleSelections, setSingleSelections] = useState([] as Option[]);

    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [targetValue, setTargetValue] = useState('1');
    const targets = [
      {name: "Azure CLI", value: "1"},
      {name: "Azure CLI Extension", value: "2"}
    ];

    const handleClick = (event: any) => {
      const targetName = event.target.innerText
      this.setState({currRepo: targetName})
      if (targetName === "Azure CLI") {
        axios.get("/CLI/Az/Main/Modules")
          .then(res => {
            this.setState({
              modules: res.data.map((module: any) => {
                return {
                  folder: module.folder,
                  name: module.name,
                  url: module.url
                }
              })
            })
          })
      }
      if (targetName === "Azure CLI Extension") {
        axios.get("/CLI/Az/Extension/Modules")
          .then(res => {
            this.setState({
              modules: res.data.map((module: any) => {
                return {
                  folder: module.folder,
                  name: module.name,
                  url: module.url
                }
              })
            })
          })
      }
    }

    const handleOptionSelection = (options: Option[]) => {
      setSingleSelections(options)
      this.setState({moduleName: String(options[0])})
    }

    return <div>
      <Modal show={!this.state.isNew} dialogClassName="target-dialog" contentClassName="target-content" centered>
        <Modal.Header className="target-header" closeButton>
          <Modal.Title className="target-title">
            Welcome to CodeGen 2.0
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row>
            <Col sm={4}>
              <ButtonGroup className="d-grid gap-2">
                {targets.map((target, idx) => (
                  <ToggleButton
                    key={idx}
                    id={`target-${idx}`}
                    type="radio"
                    variant={idx % 2 ? 'outline-secondary' : 'outline-secondary'}
                    size = "lg"
                    name="target"
                    value={target.value}
                    checked={targetValue === target.value}
                    onChange={(e) => setTargetValue(e.currentTarget.value)}
                    onClick={handleClick}
                  >
                    {target.name}
                  </ToggleButton>
                ))}
              </ButtonGroup>
            </Col>
            <Col sm={8}>
              <Row>
                <Col sm={8}>
                  <Form id="moduleName" onSubmit={this.handleSubmit}>
                    <Typeahead
                      id="basic-typeahead-single"
                      labelKey="name"
                      onChange={handleOptionSelection}
                      options={this.state.modules.map(module => {return module.name})}
                      placeholder="Search modules"
                      selected={singleSelections}
                    />
                  </Form>
                </Col>
                <Col sm={4}>
                  <Button variant="secondary" onClick={() => this.setState({isNew: true})}>
                    New Module
                  </Button>
                </Col>
              </Row>
            </Col>
          </Row>
        </Modal.Body>
        <Modal.Footer className='justify-content-right'>
          <Button type="submit" form="moduleName" variant="primary">
            OK
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  }

  NewTarget = () => {
    const handleSubmit = (event: any) => {
      event.preventDefault();
      event.stopPropagation();

      const moduleName = event.target[0].value
      if (this.state.currRepo === "Azure CLI") {
        axios.post('/CLI/Az/Main/Modules', {name: moduleName})
          .then(res => {
            this.setState({
              modules: res.data.map((module: any) => {
                return {
                  folder: module.folder,
                  name: module.name,
                  url: module.url
                }
              })
            })
          })
      }
      if (this.state.currRepo === "Azure CLI Extension") {
        axios.post('/CLI/Az/Extension/Modules', {name: moduleName})
          .then(res => {
            this.setState({
              modules: res.data.map((module: any) => {
                return {
                  folder: module.folder,
                  name: module.name,
                  url: module.url
                }
              })
            })
          })
      }

      window.location.href = `/module/${this.state.currRepo}/${moduleName}`
    }

    return <div>
      <Modal show={this.state.isNew} dialogClassName="target-dialog" contentClassName="target-content" centered>
        <Modal.Header className="target-header" closeButton>
          <Modal.Title className="target-title">
            Welcome to CodeGen 2.0
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form id="newTargetForm" onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Label>Module Name:</Form.Label>
              <Form.Control type="text" required/>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className='justify-content-right'>
          <Button type="submit" form="newTargetForm" variant="primary">
            Create
          </Button>
          <Button variant="secondary" onClick={() => this.setState({isNew: false})}>
            Cancel
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  }

  render() {
    return (
      <div>
        <this.SelectTarget/>
        <this.NewTarget/>
      </div>
    )
  }
}
