import React, { PureComponent} from "react";
import {Accordion} from "react-bootstrap";
import { ListGroup, ListGroupItem} from "reactstrap";

type VersionList = []

type ResourceId = string

type Module = [{
  [key: ResourceId]: VersionList
}]

type ModuleName = string

type Spec = {
  [key: ModuleName]: Module
}

type AccordionProp = {
  mgmtPlaneSpecs: Spec | null,
  dataPlaneSpecs: Spec | null,
  hidden: boolean
}

type AccordionState = {
  mgmtPlaneSpecs: Spec | null,
  dataPlaneSpecs: Spec | null,
  hidden: boolean,
  activeModule: string | null
}


export default class CustomAccordion extends PureComponent<AccordionProp, AccordionState> {
    constructor(props: AccordionProp) {
        super(props);
        this.state = {
            mgmtPlaneSpecs: this.props.mgmtPlaneSpecs,
            dataPlaneSpecs: this.props.dataPlaneSpecs,
            hidden: this.props.hidden,
            activeModule: null
        };
      }

    getVersion = (versionList: VersionList) => {
      return versionList.map((version, index)=>{
        return <ListGroupItem key={index}>{version}</ListGroupItem>
      })
    }

    getResourceId = (resourceIdList: Module) => {
      return  <Accordion>
                {resourceIdList.map((resourceId: {[key: ResourceId]: VersionList}, index: number) =>{
                  let id = Object.keys(resourceId)[0]
                  return  <Accordion.Item eventKey={index.toString()} key={index.toString()}>
                            <Accordion.Header>{id}</Accordion.Header>
                            <Accordion.Body>
                            <ListGroup>
                              {this.getVersion(resourceId[id])}
                            </ListGroup>
                            </Accordion.Body>
                          </Accordion.Item>
                })}
              </Accordion>
    }

    getModule = (spec: Spec) =>{
      return  <Accordion activeKey={this.state.activeModule?this.state.activeModule:undefined} onSelect={e => this.setState({activeModule: e})}>
                {Object.keys(spec).map((moduleName, index) =>{
                  return <Accordion.Item eventKey={index.toString()} key={index.toString()}>
                          <Accordion.Header>{moduleName}</Accordion.Header>
                          <Accordion.Body>
                            {this.state.activeModule===index.toString() && this.getResourceId(spec[moduleName])}
                          </Accordion.Body>
                          </Accordion.Item>
                })}
              </Accordion>
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

export type {Spec}