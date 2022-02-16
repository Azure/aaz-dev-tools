import React, { useRef, useState } from "react";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import styles from "./TreeView/CustomNode.module.css";
import { Row, Col, ListGroup } from "react-bootstrap"
import type { CommandGroup } from "./ConfigEditor"


type Props = {
    commandGroup: CommandGroup,
    onHelpChange: (name: string, help: string) => void
};

export const CommandGroupDetails: React.FC<Props> = (props) => {
    const { names, commands } = props.commandGroup;
    const onHelpChange = props.onHelpChange


    type NameInputAreaProps = {
        name: string,
        prefix: string,
        initEditing: boolean,
        onSubmit: (name: string, newName: string) => void
    }

    const NameInputArea: React.FC<NameInputAreaProps> = (props) => {
        const { name, prefix } = props;
        const [displayName, setDisplayName] = useState(name)
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
            props.onSubmit(name, changingName.trim())
        }

        const handleCancel = (event: any) => {
            setEditing(false)
            setChangingName(displayName)
        }



        return (
            <div >
                <Row onDoubleClick={handleDoubleClick} className="g-1 align-items-center">
                    <Col lg="auto"> {prefix}</Col>
                    {!editing ?
                        (<Col lg="auto"> {displayName}</Col>) :
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
    //                         <ListGroup.Item><NameInputArea name={commands![commandName].names.join(' ')} prefix="aaz" initEditing={false} onSubmit={onNameChange} /></ListGroup.Item>
    //                         <ListGroup.Item>Help: {commands![commandName].help.short}</ListGroup.Item>
    //                     </ListGroup>
    //                 </ListGroup.Item>
    //             })}
    //         </ListGroup>
    //     </div>) : <div></div>
    // )
    
    return (<div>
        <div>
            {/* <NameInputArea name={names.join(' ')} prefix="Name: aaz" initEditing={false} onSubmit={onNameChange} editable={false}/> */}
            Name: aaz {names.join(' ')}
            <NameInputArea name={""} prefix="Short Help: " initEditing={true} onSubmit={onHelpChange} />
        </div>
    </div>
    );



};
