import React, { useState } from "react";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import TextareaAutosize from '@mui/base/TextareaAutosize';
import { NodeModel } from "@minoru/react-dnd-treeview";
import { Row, Col } from "react-bootstrap"
import type { CommandGroup, HelpType, ExampleType } from "./ConfigEditor"



type Props = {
    commandGroup: CommandGroup,
    id: NodeModel["id"],
    isCommand: boolean,
    onHelpChange: (id: NodeModel["id"], help: HelpType) => void,
    onExampleChange: (id: NodeModel["id"], examples: ExampleType[]) => void
};


export const CommandGroupDetails: React.FC<Props> = (props) => {
    const { names, help } = props.commandGroup;
    let { examples } = props.commandGroup
    const id = Number(props.id)
    const isCommand = props.isCommand
    let shortHelp = ""
    let longHelp = ""
    const [creatingExample, setCreatingExample] = useState(false)


    const shortHelpPlaceholder = "Create a new resource group"
    const longHelpPlaceholder = "Create a new resource group\nShow details of the new resource group"

    const exampleNamePlaceholder = "Create a new example"
    const exampleContentPlaceholder = "az group create\naz group list"

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
        if (help && help.lines) {
            helpObj.lines = help.lines
        }
        props.onHelpChange(id, helpObj)
    }

    const onLongHelpChange = (longHelp: string) => {
        let helpObj: HelpType = {
            short: "",
            lines: longHelp.split("\n")
        }
        helpObj.short = (help && help.short) ? shortHelp : ""
        props.onHelpChange(id, helpObj)
    }

    const onExampleNameChange = (exampleName: string, index: number) => {
        let exampleObj: ExampleType = {
            name: exampleName,
            commands: examples![index].commands
        }
        examples![index] = exampleObj
        props.onExampleChange(id, examples!)
    }

    const onExampleContentChange = (exampleContent: string, index: number) => {
        let exampleObj: ExampleType = {
            name: examples![index].name,
            commands: exampleContent.split('\n')
        }
        examples![index] = exampleObj
        props.onExampleChange(id, examples!)
    }

    const onExampleCreate = (example: ExampleType) => {
        if (!examples) {
            examples = []
        }
        examples.push(example)
        props.onExampleChange(id, examples!)
    }

    const onExampleDelete = (index: number) => {
        examples?.splice(index, 1)
        props.onExampleChange(id, examples!)
    }


    type InputAreaProps = {
        prefix: string,
        value: string,
        width: string,
        placeholder: string,
        initEditing: boolean,
        minRow: number,
        editable: boolean,
        onSubmit: (value: string) => void
    }

    const InputArea: React.FC<InputAreaProps> = (props) => {
        const { value, prefix, width, placeholder } = props;
        const [displayValue, setDisplayValue] = useState(value)
        const [changingValue, setChangingValue] = useState(displayValue)
        const [editing, setEditing] = useState(props.initEditing)


        const handleDoubleClick = (event: React.MouseEvent) => {
            if (!props.editable) {
                return
            }
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
                <Row className="align-items-top">
                    <Col xxl="2">
                        <h6>{prefix}</h6>
                    </Col>
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
                            <Col>
                                <TextareaAutosize
                                    minRows={props.minRow}
                                    style={{ width: width }}
                                    placeholder={placeholder}
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


    const ExampleList = () => {
        return examples ? (<div>
            {examples.map((example, index) => {
                const name = example.name
                const content = example.commands.join('\n')
                return <div key={index}>
                    <Row>
                        <Col>
                            <InputArea value={name} prefix="Name: " initEditing={name === ""} editable={true} onSubmit={(exampleName: string) => { onExampleNameChange(exampleName, index) }} minRow={1} width="35em" placeholder={exampleNamePlaceholder} />
                            <InputArea value={content} prefix="Commands:" initEditing={content === ""} editable={true} onSubmit={(exampleContent: string) => { onExampleContentChange(exampleContent, index) }} minRow={3} width="35em" placeholder={exampleContentPlaceholder} />
                        </Col>
                        <Col xxl='3'>
                            <IconButton onClick={() => { onExampleDelete(index) }}>
                                <RemoveIcon />
                            </IconButton>
                        </Col>
                    </Row>
                </div>
            })}
        </div>) : <></>
    }

    const CreateNewExample = () => {
        const [name, setName] = useState("")
        const [commands, setCommands] = useState("")

        const handleSubmitExample = () => {
            // console.log(name)
            // console.log(commands)
            setCreatingExample(false)
            onExampleCreate({
                name: name,
                commands: commands.split('\n')
            })
        }

        const handleCancelExample = () => {
            setCreatingExample(false)
        }

        return <div>
            <Row>
                <Col xxl='2'>
                    <h6>Name:</h6>
                </Col>
                <Col>
                    <TextareaAutosize minRows={1} style={{ width: `35em` }} value={name} onChange={e => setName(e.target.value)} placeholder={exampleNamePlaceholder} />
                </Col>
            </Row>
            <Row>
                <Col xxl='2'>
                    <h6>Commands:</h6>
                </Col>
                <Col>
                    <TextareaAutosize minRows={3} style={{ width: `35em` }} value={commands} onChange={e => setCommands(e.target.value)} placeholder={exampleContentPlaceholder} />
                    <IconButton onClick={handleSubmitExample} disabled={name === "" || commands === ""}>
                        <CheckIcon />
                    </IconButton>
                    <IconButton onClick={handleCancelExample}>
                        <CloseIcon />
                    </IconButton>
                </Col>
            </Row>


        </div>
    }


    return (<div>
        <div>
            {/* <InputArea name={names.join(' ')} prefix="Name: aaz" initEditing={false} onSubmit={onNameChange} editable={false}/> */}
            <h5>Name: az {names.join(' ')}</h5>
            <InputArea value={shortHelp} prefix="Short Help: " initEditing={shortHelp === ""} editable={true} onSubmit={onShortHelpChange} minRow={1} width="35em" placeholder={shortHelpPlaceholder} />
            <InputArea value={longHelp} prefix="Long Help: " initEditing={longHelp === ""} editable={true} onSubmit={onLongHelpChange} minRow={3} width="35em" placeholder={longHelpPlaceholder} />
            {isCommand &&
                <div>
                    <h5>Examples:</h5>
                    <ExampleList></ExampleList>
                    {!creatingExample && <IconButton onClick={() => { setCreatingExample(true) }}>
                        <AddIcon></AddIcon>
                    </IconButton>}
                    {creatingExample && <CreateNewExample></CreateNewExample>}
                </div>
            }

        </div>
    </div>
    );



};