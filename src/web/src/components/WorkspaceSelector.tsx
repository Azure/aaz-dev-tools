import React, { Component } from "react";
import { Modal, Button, ListGroup, Row, Col, Form, Alert } from "react-bootstrap";
import axios from "axios";
import { Url } from "url";

type workspaceSelectorState = {
  creatingNew: boolean,
  workspaces: Workspace[],
  alertText: string,
  showAlert: boolean,
  validated: boolean
}

type Workspace = {
  name: Text,
  lastModified: Date,
  url: Url
}

export default class WorkspaceSelector extends Component<{}, workspaceSelectorState> {

  constructor(props: any) {
    super(props);
    this.state = {
      creatingNew: false,
      workspaces: [],
      alertText: "",
      showAlert: false,
      validated: false
    }
  }

  componentDidMount() {
    this.loadWorkspaces();
  }

  loadWorkspaces = () => {
    axios.get("/AAZ/Editor/Workspaces")
      .then((res) => {
        this.setState({
          workspaces: res.data.map((workspace: any) => {
            return {
              name: workspace.name,
              lastModified: new Date(workspace.updated * 1000),
              url: workspace.url
            }
          })
        })
      })
      .catch((err) => console.log(err));
  }

  calculatePageHeight = (subtractAmount: number) => {
    const body = document.body;
    const html = document.documentElement;

    return (Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight) - subtractAmount).toString() + 'px'
  }

  WorkspaceList = () => {
    return <div style={{ maxHeight: this.calculatePageHeight(300), overflow: `auto` }}>{
      this.state.workspaces.map((workspace: Workspace, index) => {
        return <ListGroup.Item key={index} action href={`/workspace/${workspace.name}`}>
          <Row>
            <Col>{workspace.name}</Col>
            <Col>{workspace.lastModified.toLocaleString()}</Col>
          </Row>
        </ListGroup.Item>
      })
    }
    </div>
  }

  SelectWorkspace = () => {
    return <div>
      <Modal show={!this.state.creatingNew} centered>
        <Modal.Header>
          <Modal.Title>Please select a workspace</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ListGroup>
            <ListGroup.Item>
              <Row>
                <Col>Name</Col>
                <Col>Last Modified</Col>
              </Row>
            </ListGroup.Item>
            <this.WorkspaceList />
          </ListGroup>
        </Modal.Body>
        <Modal.Footer className='justify-content-center'>
          <Button onClick={() => this.setState({ creatingNew: true })}>
            Create New
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  }

  handleClose = () => {
    this.setState({ creatingNew: false })
  }

  handleSubmit = (event: any) => {
    event.preventDefault();
    event.stopPropagation();
    const form = event.currentTarget;
    this.setState({ validated: true })

    if (form.checkValidity() === true) {
      const workspaceName = event.target[0].value
      axios.post('/AAZ/Editor/Workspaces', {
        name: workspaceName,
        plane: 'mgmt-plane'
      })
        .then(() => {
          // this.handleClose()
          // this.loadWorkspaces()
          // this.setState({ showAlert: false, alertText: "", validated: false })
          window.location.href = `/workspace/${workspaceName}`
        })
        .catch(error => {
          console.log(error);
          if (error.response.status === 409) {
            this.setState({ showAlert: true, alertText: `There is already another workspace with the name ${event.target[0].value}, please specify another name.` })
          }
        });
    }
  }

  NewWorkspaceModal = () => {
    return <div>
      <Modal show={this.state.creatingNew} onHide={this.handleClose} centered backdrop='static'>
        <Modal.Header closeButton>
          <Modal.Title>
            Creating New Workspace
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form id='newWorkspaceForm' onSubmit={this.handleSubmit} noValidate validated={this.state.validated}>
            <Form.Group controlId="workspaceName">
              <Form.Label>Workspace Name</Form.Label>
              <Form.Control type="text" placeholder="Name" required />
              <Form.Control.Feedback type="invalid">
                Please provide a workspace name.
              </Form.Control.Feedback>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className='justify-content-center'>
          <Button type='submit' form='newWorkspaceForm'>
            Create
          </Button>
        </Modal.Footer>
        <Alert show={this.state.showAlert} variant={"danger"}>
          {this.state.alertText}
        </Alert>
      </Modal>

    </div>
  }

  render() {
    return (
      <div>
        <this.SelectWorkspace />
        <this.NewWorkspaceModal />
      </div>
    )
  }
} 