import React, { PureComponent } from "react";
import {Accordion} from "react-bootstrap";
import { ListGroup, ListGroupItem} from "reactstrap";

export default class CustomAccordion extends PureComponent {

    constructor(props) {
        super(props);
        this.state = {
            mgmtPlaneSpecs: this.props.mgmtPlaneSpecs,
            dataPlaneSpecs: this.props.dataPlaneSpecs,
            hidden: this.props.hidden
        };
      }

    getVersion = versionList => {
        return versionList.map(version=>{
        return <ListGroupItem>{version}</ListGroupItem>
        })
    }

    getResourceId = resourceIdList => {
        return resourceIdList.map((resourceId) =>{
            let id = Object.keys(resourceId)[0]
            return <Accordion>
                <Accordion.Item eventKey={id}>
                    <Accordion.Header>{id}</Accordion.Header>
                    <Accordion.Body>
                    <ListGroup>{this.getVersion(resourceId[id])}</ListGroup>
                    </Accordion.Body>
                </Accordion.Item>
                </Accordion>
            }
        )
    }

    getModule = spec =>{
        return Object.keys(spec).map((moduleName) =>{
            return <Accordion>
                    <Accordion.Item eventKey={moduleName}>
                    <Accordion.Header>{moduleName}</Accordion.Header>
                    <Accordion.Body>
                        {this.getResourceId(spec[moduleName])}
                    </Accordion.Body>
                    </Accordion.Item>
            </Accordion>
        })
    }

    render() {
        return <Accordion hidden={this.props.hidden}>
                {this.props.mgmtPlaneSpecs && 
                <Accordion.Item eventKey="0">
                  <Accordion.Header>Management Plane</Accordion.Header>
                  <Accordion.Body>
                    {this.getModule(this.props.mgmtPlaneSpecs)}
                  </Accordion.Body>
                </Accordion.Item>
                }
                {this.props.dataPlaneSpecs &&
                <Accordion.Item eventKey="1">
                  <Accordion.Header>Data Plane</Accordion.Header>
                  <Accordion.Body>
                    {this.getModule(this.props.dataPlaneSpecs)}
                  </Accordion.Body>
                </Accordion.Item>
                }
              </Accordion>
    }
} 