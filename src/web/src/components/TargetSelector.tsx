import {Component, useState} from "react";
import axios from "axios";
import {Link} from "react-router-dom";
import {Modal, Row, Col, ButtonGroup, ToggleButton, Button, Form} from "react-bootstrap";
import {Typeahead} from 'react-bootstrap-typeahead';
import type {Option} from "react-bootstrap-typeahead/types/types"
import "./TargetSelector.css";

import options from './data.js';


type TargetSelectorState = {
  isNew: boolean,
  moduleName: string,
}


export default class TargetSelector extends Component<any, TargetSelectorState>{
  constructor(props: any) {
    super(props);
    this.state = {
      isNew: false,
      moduleName: "",
    }
  }

  SelectTarget = () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [singleSelections, setSingleSelections] = useState([] as Option[]);

    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [radioValue, setRadioValue] = useState('1');
    const radios = [
      { name: 'Azure CLI', value: '1' },
      { name: 'Azure CLI Extension', value: '2' },
    ];

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
                {radios.map((radio, idx) => (
                  <ToggleButton
                    key={idx}
                    id={`radio-${idx}`}
                    type="radio"
                    variant={idx % 2 ? 'outline-secondary' : 'outline-secondary'}
                    size = "lg"
                    name="radio"
                    value={radio.value}
                    checked={radioValue === radio.value}
                    onChange={(e) => setRadioValue(e.currentTarget.value)}
                  >
                    {radio.name}
                  </ToggleButton>
                ))}
              </ButtonGroup>
            </Col>
            <Col sm={8}>
              <Row>
                <Col sm={8}>
                  <Form.Group>
                    <Typeahead
                      id="basic-typeahead-single"
                      labelKey="label"
                      onChange={setSingleSelections}
                      options={options}
                      placeholder="Search modules"
                      selected={singleSelections}
                    />
                  </Form.Group>
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
          <Link to={"generator"}>
            <Button variant="primary">
              OK
            </Button>
          </Link>
        </Modal.Footer>
      </Modal>
    </div>
  }

  NewTarget = () => {
    const handleSubmit = (event: any) => {
      event.preventDefault();
      event.stopPropagation();
      const form = event.currentTarget;

      if (form.checkValidity() === true) {
        const workspaceName = event.target[0].value
        axios.post('/AAZ/Editor/Workspaces', {
          name: workspaceName,
          plane: 'mgmt-plane'
        })
            .then(() => {
              window.location.href = `/workspace/${workspaceName}`
            });
      }
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
          <Link to={"/module/generator"}>
            <Button type="submit" form="newTargetForm" variant="primary">
              Create
            </Button>
          </Link>
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
