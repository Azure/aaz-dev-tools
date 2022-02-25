import React, { useRef, useState } from "react";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import styles from "./TreeView/CustomNode.module.css";
import { NodeModel, useDragOver } from "@minoru/react-dnd-treeview";
import { Row, Col, ListGroup } from "react-bootstrap"
import type { CommandGroup } from "./ConfigEditor"


type Props = {
    commandGroup: CommandGroup,
    id: NodeModel["id"],
    onHelpChange: (id: NodeModel["id"], help: string) => void
};

export const CommandGroupDetails: React.FC<Props> = (props) => {
    const { names, help } = props.commandGroup;
    const onHelpChange = props.onHelpChange
    const id = Number(props.id)
    let shortHelp = ""
    if (help){
        shortHelp = help!.short
    }


    type InputAreaProps = {
        prefix: string,
        value: string,
        initEditing: boolean,
        onSubmit: (id: number, newName: string) => void
    }

    const InputArea: React.FC<InputAreaProps> = (props) => {
        const { value, prefix } = props;
        const [displayName, setDisplayName] = useState(value)
        const [changingName, setChangingName] = useState(displayName)
        const [editing, setEditing] = useState(props.initEditing)


        const handleDoubleClick = (event: React.MouseEvent) => {
            event.stopPropagation();
            if (!editing) {
                setEditing(true)
                setChangingName(displayName)
            }
        }

        const handleChangeName = (event: any) => {
            setChangingName(event.target.value)
        }

        const handleSubmit = (event: any) => {
            setEditing(false)
            setDisplayName(changingName.trim())
            props.onSubmit(id, changingName.trim())
        }

        const handleCancel = (event: any) => {
            setEditing(false)
            setChangingName(displayName)
        }



        return (
            <div >
                <Row className="g-1 align-items-center">
                    <Col lg="auto"> {prefix}</Col>
                    {!editing
                        ?
                        (<Col onDoubleClick={handleDoubleClick}> {displayName}</Col>)
                        :
                        (
                            <Col lg="auto" style={{ position: `relative`, top: `2px` }}>
                                <input style={{ width: `${Math.max(20, changingName.length)}ch` }}
                                    value={changingName}
                                    onChange={handleChangeName}
                                />
                                <IconButton
                                    onClick={handleSubmit}
                                    disabled={changingName === ""}
                                >
                                    <CheckIcon />
                                </IconButton>
                                <IconButton
                                    onClick={handleCancel}
                                    disabled={displayName === ""}
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
            <InputArea value={shortHelp} prefix="Short Help: " initEditing={shortHelp===""} onSubmit={onHelpChange} />
        </div>
    </div>
    );



};
