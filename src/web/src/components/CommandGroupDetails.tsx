import React, { useRef, useState } from "react";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import TextareaAutosize from '@mui/base/TextareaAutosize';
import styles from "./TreeView/CustomNode.module.css";
import { NodeModel, useDragOver } from "@minoru/react-dnd-treeview";
import { Row, Col, ListGroup } from "react-bootstrap"
import type { CommandGroup, HelpType } from "./ConfigEditor"



type Props = {
    commandGroup: CommandGroup,
    id: NodeModel["id"],
    onHelpChange: (id: NodeModel["id"], help: HelpType) => void
};

export const CommandGroupDetails: React.FC<Props> = (props) => {
    const { names, help } = props.commandGroup;

    const id = Number(props.id)
    let shortHelp = ""
    let longHelp = ""
    if (help) {
        if (help!.short) {
            shortHelp = help!.short
        }
        if (help!.lines) {
            longHelp = help.lines.join('\n')
        }
    }

    const onShortHelpChange = (shortHelp: string) => {
        let helpObj: HelpType = {
            short: shortHelp,
        }
        if (help && help!.lines){
            helpObj.lines = help.lines
        }
        props.onHelpChange(id, helpObj)
    }

    const onLongHelpChange = (longHelp: string) => {
        let helpObj: HelpType = {
            short: ""
        }
        helpObj.short = (help && help.short)?shortHelp:""
        helpObj.lines = longHelp.split("\n")
        props.onHelpChange(id, helpObj)
    }

    type InputAreaProps = {
        prefix: string,
        value: string,
        initEditing: boolean,
        minRow: number,
        onSubmit: (help: string) => void
    }

    const InputArea: React.FC<InputAreaProps> = (props) => {
        const { value, prefix } = props;
        const [displayValue, setDisplayValue] = useState(value)
        const [changingValue, setChangingValue] = useState(displayValue)
        const [editing, setEditing] = useState(props.initEditing)


        const handleDoubleClick = (event: React.MouseEvent) => {
            event.stopPropagation();
            if (!editing) {
                setEditing(true)
                setChangingValue(displayValue)
            }
        }

        const handleChangeValue = (event: any) => {
            setChangingValue(event.target.value)
        }

        const handleSubmit = (event: any) => {
            setEditing(false)
            setDisplayValue(changingValue.trim())
            props.onSubmit(changingValue.trim())
        }

        const handleCancel = (event: any) => {
            setEditing(false)
            setChangingValue(displayValue)
        }



        return (
            <div >
                <Row className="g-1 align-items-top">
                    <Col lg="auto"> {prefix}</Col>
                    {!editing
                        ?
                        (<Col onDoubleClick={handleDoubleClick}>
                            {displayValue.split('\n').map((line, index) => {
                                return <div key={index}>
                                    {line}
                                </div>
                            })}
                        </Col>)
                        :
                        (
                            <Col lg="auto">
                                <TextareaAutosize minRows={props.minRow} style={{ width: `45em` }}
                                    value={changingValue}
                                    onChange={handleChangeValue}
                                />
                                <IconButton
                                    onClick={handleSubmit}
                                    disabled={displayValue === changingValue}
                                >
                                    <CheckIcon />
                                </IconButton>
                                <IconButton
                                    onClick={handleCancel}
                                    disabled={displayValue === ""}
                                >
                                    <CloseIcon />
                                </IconButton>
                            </Col>
                        )
                    }
                </Row>
            </div>
        )
    }

    // const commandDetails = (
    //     commands ? (<div>
    //         <p>Commands: </p>
    //         <ListGroup>
    //             {commands && Object.keys(commands).map(commandName => {
    //                 let namesJoined = commands![commandName].names.join('/')
    //                 return <ListGroup.Item key={namesJoined}>
    //                     <ListGroup>
    //                         <ListGroup.Item><InputArea name={commands![commandName].names.join(' ')} prefix="aaz" initEditing={false} onSubmit={onNameChange} /></ListGroup.Item>
    //                         <ListGroup.Item>Help: {commands![commandName].help.short}</ListGroup.Item>
    //                     </ListGroup>
    //                 </ListGroup.Item>
    //             })}
    //         </ListGroup>
    //     </div>) : <div></div>
    // )

    return (<div>
        <div>
            {/* <InputArea name={names.join(' ')} prefix="Name: aaz" initEditing={false} onSubmit={onNameChange} editable={false}/> */}
            Name: aaz {names.join(' ')}
            <InputArea value={shortHelp} prefix="Short Help: " initEditing={shortHelp === ""} onSubmit={onShortHelpChange} minRow={1} />
            <InputArea value={longHelp} prefix="Long Help: " initEditing={longHelp === ""} onSubmit={onLongHelpChange} minRow={3} />
        </div>
    </div>
    );



};
