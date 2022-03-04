import {Component} from "react";
import {Modal, Button} from "react-bootstrap";


export default class TargetSelector extends Component {

  SelectTarget = () => {
    return <div>
      <Modal show="true" centered>
        <Modal.Header>
          <Modal.Title>
            Please select your target
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="d-grid gap-2">
            <Button variant="secondary" size="lg">
              Azure CLI
            </Button>
            <Button variant="secondary" size="lg">
              Azure CLI Extension
            </Button>
          </div>
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
