import { useState } from "react";
import { Modal, Row, Col, ButtonGroup, ToggleButton, Button, Form } from "react-bootstrap";
import { Typeahead } from 'react-bootstrap-typeahead';
import "./TargetSelector.css";
import type { Option } from "react-bootstrap-typeahead/types/types"

import options from './data';

import 'react-bootstrap-typeahead/css/Typeahead.css';


const TargetSelector = () => {
  const SelectTarget = () => {
    const optionsTyped: Option[] = options;
    const [singleSelections, setSingleSelections] = useState(optionsTyped);
    const handleTypeChange = (selectedOption: Option[]) => {
      setSingleSelections(selectedOption)
    }

    const [radioValue, setRadioValue] = useState('1');
    const radios = [
      { name: 'Azure CLI', value: '1' },
      { name: 'Azure CLI Extension', value: '2' },
    ];

    return <div>
      <Modal show="true" dialogClassName="target-dialog" contentClassName="target-content" centered>
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
                      onChange={handleTypeChange}
                      options={optionsTyped}
                      placeholder="Search modules"
                      selected={singleSelections}
                    />
                  </Form.Group>
                </Col>
                <Col sm={4}>
                  <Button variant="secondary">
                    New Module
                  </Button>
                </Col>
              </Row>
            </Col>
          </Row>
        </Modal.Body>
        <Modal.Footer className='justify-content-right'>
          <Button variant="secondary">
            OK
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  }


  return (
    <div>
      <SelectTarget/>
    </div>
  )
}

export default TargetSelector;
