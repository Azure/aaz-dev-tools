import React, { Component } from "react";
import {
  Button,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Form,
  FormGroup,
  Input,
  Label,
} from "reactstrap";

export default class CustomModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeItem: this.props.activeItem,
    };
  }

  handleChange = (e) => {
    let { name, value } = e.target;

    const activeItem = { ...this.state.activeItem, [name]: value };

    this.setState({ activeItem });
  };

  render() {
    const { toggle, onSave } = this.props;

    return (
      <Modal isOpen={true} toggle={toggle}>
        <ModalHeader toggle={toggle}>Customizations</ModalHeader>
        <ModalBody>
          <Form>
            <FormGroup>
              <Label for="customization-module-name">Module name</Label>
              <Input
                type="text"
                id="customization-module-name"
                name="module_name"
                value={this.state.activeItem.module_name}
                onChange={this.handleChange}
                placeholder="Enter module name"
              />
            </FormGroup>
            <FormGroup>
              <Label for="customization-module-path">Module path</Label>
              <Input
                type="text"
                id="customization-module-path"
                name="module_path"
                value={this.state.activeItem.module_path}
                onChange={this.handleChange}
                placeholder="Enter module path"
              />
            </FormGroup>
          </Form>
        </ModalBody>
        <ModalFooter>
          <Button
            color="success"
            onClick={() => onSave(this.state.activeItem)}
          >
            Save
          </Button>
        </ModalFooter>
      </Modal>
    );
  }
}