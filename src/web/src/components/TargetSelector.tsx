import {Component} from "react";
import {Modal, Navbar, Row, Col, Button} from "react-bootstrap";
import "./TargetSelector.css";


export default class TargetSelector extends Component {

  SelectTarget = () => {
    return <div>
      <Modal show="true" dialogClassName="modal-width" centered>
        <Modal.Header className="modal-header" closeButton>
          <Modal.Title className="model-title">
            Welcome to CodeGen 2.0
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row>
            <Col sm={4}>
              <div className="d-grid gap-2">
                <Button variant="secondary" size="lg">
                  Azure CLI
                </Button>
                <Button variant="secondary" size="lg">
                  Azure CLI Extension
                </Button>
              </div>
            </Col>
            <Col sm={8}>
              <div className="d-grid gap-2">
                <Button variant="secondary" size="lg">
                  Azure CLI
                </Button>
                <Button variant="secondary" size="lg">
                  Azure CLI Extension
                </Button>
              </div>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </div>
  }

  render() {
    return (
      <div>
        <this.SelectTarget/>
      </div>
    )
  }
}
