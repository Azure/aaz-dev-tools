import React, { Component } from "react";
import { Input, InputGroup, Button, ListGroup, ListGroupItem} from "reactstrap";
import { Accordion } from "react-bootstrap";
import {useParams} from "react-router-dom"

type ParamsType = {
  workspaceName: String
}

type SpecSelectorProp = {
  params: ParamsType
} 

class SpecSelector extends Component<SpecSelectorProp,{}> {
  constructor(props: any) {
    super(props);
  }

  render() {
    console.log(this.props.params.workspaceName)
    return <div>Workspace Name: {this.props.params.workspaceName}</div>
  }
}

const SpecSelectorWrapper = (props:any) => {
  const params = useParams()

  return <SpecSelector params={params} {...props} />
}

export {SpecSelectorWrapper as SpecSelector};