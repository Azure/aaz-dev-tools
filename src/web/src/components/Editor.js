import React, { Component } from "react";
import { Input, InputGroup, Button, ListGroup, ListGroupItem} from "reactstrap";
import { Accordion } from "react-bootstrap";

export default class Editor extends Component {

    constructor(props) {
      super(props);
      this.state = {
        module: {}
      }
    }

    componentDidMount = () => {
      this.setState({
        module:{
          "module_name": "user",
          "commands": [{
            "command_name":"create",
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
            "command_name":"update",
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
            "command_name":"show",
            "arguments":[{
              "name":"id",
              "type":"string"
            }]
          }]
        }
      })
    }

    getCommandDetail = argumentList => {
      return argumentList.map(arg=>{
        return <ListGroupItem key={arg["name"]}>{arg["name"]}</ListGroupItem>
        })
    }

    getModuleDetail = commands => {
      return commands && commands.map((command) =>{
        return <Accordion key={command["command_name"]}>
            <Accordion.Item>
                <Accordion.Header>{command["command_name"]}</Accordion.Header>
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
                <p>Module Name: {this.state.module["module_name"]}</p>
                {this.getModuleDetail(this.state.module["commands"])}
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