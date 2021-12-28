import React, { Component } from "react";
import { Input, InputGroup, Button, ListGroup, ListGroupItem} from "reactstrap";
import { Accordion } from "react-bootstrap";


type Name = string
type Type = string

type Argument = {
  name: Name,
  type: Type
}

type Command = {
  name: Name,
  arguments: Argument[]
}

type Resource = {
  name: Name,
  commands: Command[]
} | null

type EditorState = {
  resource: Resource
}

export default class Editor extends Component<{}, EditorState> {

    constructor(props: any) {
      super(props);
      this.state = {
        resource: null
      }
    }

    componentDidMount = () => {
      this.setState({
        resource:{
          "name": "user",
          "commands": [{
            "name":"create",
            "arguments":[{
              "name":"username",
              "type":"string"
            }, {
              "name":"password",
              "type":"string"
            }, {
              "name":"phone",
              "type":"number"
            }]
          }, {
            "name":"update",
            "arguments":[{
              "name":"id",
              "type":"string"
            }, {
              "name":"username",
              "type":"string"
            }, {
              "name":"password",
              "type":"string"
            }, {
              "name":"phone",
              "type":"number"
            }]
          }, {
            "name":"show",
            "arguments":[{
              "name":"id",
              "type":"string"
            }]
          }]
        }
      })
    }

    getCommandDetail = (argumentList: Argument[]) => {
      return argumentList.map(arg=>{
        return <ListGroupItem key={arg["name"]}>{arg["name"]}</ListGroupItem>
        })
    }

    getModuleDetail = (commands: Command[]) => {
      return commands && commands.map((command) =>{
        return <Accordion key={command["name"]}>
            <Accordion.Item eventKey={command["name"]}>
                <Accordion.Header>{command["name"]}</Accordion.Header>
                <Accordion.Body>
                  <ListGroup>{this.getCommandDetail(command["arguments"])}</ListGroup>
                </Accordion.Body>
            </Accordion.Item>
            </Accordion>
        }
      )
          
    }

    specLinks = () => {
      return <div>
                <p>Module Name: {this.state.resource && this.state.resource["name"]}</p>
                {this.state.resource && this.getModuleDetail(this.state.resource["commands"])}
            </div>  
      
    }


    render() {
      return  <div>
                <div className="container-fluid row">
                  <div className="col-md-6">
                    <InputGroup>
                      <Input placeholder="Draft Name" />
                    </InputGroup>
                  </div>
                  <div className="col-md-3">
                    <InputGroup>
                      <Input placeholder="Resource Id" />
                    </InputGroup>
                  </div>
                  <div className="col-md-3">
                    <Button>Save</Button> <Button>Commit</Button>
                  </div>
                </div>
                <div className="container-fluid row">
                  <div className="col-md-2">
                    <this.specLinks/>
                  </div>
                  <div className="col-md-10">
                    <p>Editor View</p>
                  </div>

                </div>
              </div>
    }
} 