import React, { PureComponent} from "react";
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
      return versionList.map((version, index)=>{
        return <ListGroupItem key={index}>{version}</ListGroupItem>
      })
    }

    getResourceId = resourceIdList => {
        return resourceIdList.map((resourceId, index) =>{
          let id = Object.keys(resourceId)[0]
          return <Accordion key={index}>
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
        return Object.keys(spec).map((moduleName, index) =>{
            return <Accordion key={index}>
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
                <Accordion.Item key='0' eventKey="0">
                  <Accordion.Header>Management Plane</Accordion.Header>
                  <Accordion.Body>
                    {this.getModule(this.props.mgmtPlaneSpecs)}
                  </Accordion.Body>
                </Accordion.Item>
                }
                {this.props.dataPlaneSpecs &&
                <Accordion.Item key='1' eventKey="1">
                  <Accordion.Header>Data Plane</Accordion.Header>
                  <Accordion.Body>
                    {this.getModule(this.props.dataPlaneSpecs)}
                  </Accordion.Body>
                </Accordion.Item>
                }
              </Accordion>
    }
} 