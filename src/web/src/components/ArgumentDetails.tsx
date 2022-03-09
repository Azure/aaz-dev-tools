import React, { useState } from "react";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import TextareaAutosize from '@mui/base/TextareaAutosize';
import { Tree, NodeModel, DragLayerMonitorProps, DropOptions } from "@minoru/react-dnd-treeview";
import { Row, Col, ListGroup, Form, Button } from "react-bootstrap"
import type { CommandGroup, HelpType, ExampleType, ArgGroups, TreeDataType, TreeNode, Argument } from "./ConfigEditor"
import styles from "./TreeView/App.module.css";


import { CustomData } from "./TreeView/types";
import { CustomNode } from "./TreeView/CustomNode";
import { CustomDragPreview } from "./TreeView/CustomDragPreview";


type Props = {
    argGroups: ArgGroups,
    id: NodeModel["id"],
    onNameChange: (id: NodeModel["id"], name: string) => void
};

export const ArgumentDetails: React.FC<Props> = (props) => {
    let initTreeData: TreeDataType = [];
    // const [treeData, setTreeData] = useState(initTreeData)
    // console.log(props.argGroups)
    let currentIndex = 1
    const [selectedIndex, setSelectedIndex] = useState(-1)

    type NumberToArgument = {
        [index: number]: Argument
    }

    const indexToArgument: NumberToArgument = {}
    const parseArguments = (parentIndex: number, args: Argument[]) => {
        if (!args) {
            return
        }
        args.map(arg => {
            let treeNode: TreeNode = {
                id: currentIndex,
                parent: parentIndex,
                text: `--${arg.options.join(' --')}`,
                droppable: false,
                data: { hasChildren: false, type: 'Command' }
            }
            indexToArgument[currentIndex] = arg
            currentIndex += 1
            initTreeData.push(treeNode)
        })
    }

    const parseArgGroups = (parentIndex: number, argGroups: ArgGroups) => {
        if (!argGroups) {
            return
        }
        argGroups.map(argGroup => {
            let treeNode: TreeNode = {
                id: currentIndex,
                parent: parentIndex,
                text: argGroup.name,
                droppable: false,
                data: { hasChildren: false, type: 'Command' }
            }
            currentIndex += 1
            initTreeData.push(treeNode)
            if (argGroup.args) {
                parseArguments(currentIndex, argGroup.args)
            }
        })
    }

    if (props.argGroups.length > 1) {
        parseArgGroups(0, props.argGroups)
    } else {
        parseArguments(0, props.argGroups[0].args)
    }

    // console.log(initTreeData)


    const handleClick = (id: NodeModel["id"]) => {
        setSelectedIndex(Number(id))
        // console.log(selectedIndex)
    }
    const handleNameChange = () => { }
    const handleDrop = () => { }
    const testing = []

    const ArgumentsTree = () => {
        return <div className={styles.app}>
            <Tree
                tree={initTreeData}
                rootId={0}
                render={(node: NodeModel<CustomData>, { depth, isOpen, onToggle }) => (
                    <CustomNode node={node} depth={depth} isOpen={isOpen} isSelected={node.id === selectedIndex} onToggle={onToggle} onClick={handleClick} onSubmit={handleNameChange} />
                )}
                dragPreviewRender={(
                    monitorProps: DragLayerMonitorProps<CustomData>
                ) => <CustomDragPreview monitorProps={monitorProps} />}
                onDrop={handleDrop}
                canDrag={() => { return false }}
                classes={{
                    root: styles.treeRoot,
                    draggingSource: styles.draggingSource,
                    dropTarget: styles.dropTarget,
                }}
            />
        </div>
    }


    type InputAreaProps = {
        prefix: string,
        value: string,
        width: string,
        placeholder: string,
        initEditing: boolean,
        minRow: number,
        onSubmit: (value: string) => void
    }

    const InputArea: React.FC<InputAreaProps> = (props) => {
        const { value, prefix, width, placeholder } = props;
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
                <Row className="align-items-top ">
                    <Col xxl="2">
                        <h6>{prefix}</h6>
                    </Col>
                    {!editing
                        ?
                        (<Col onDoubleClick={handleDoubleClick} xxl="10">
                            {displayValue.split('\n').map((line, index) => {
                                return <div key={index}>
                                    {line}
                                </div>
                            })}
                        </Col>)
                        :
                        (
                            <Col xxl="10">
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

    const ArgumentsEdit = () => {
        if (!initTreeData[selectedIndex - 1]) {
            return <div />
        }
        const helpText = indexToArgument[selectedIndex].help?.short ? indexToArgument[selectedIndex].help?.short! : ""
        // const checked = indexToArgument[selectedIndex].required? indexToArgument[selectedIndex].required! : false

        return (<div>
            <InputArea value={initTreeData[selectedIndex - 1].text} prefix="Option List: " initEditing={initTreeData[selectedIndex - 1].text === ""} onSubmit={handleNameChange} minRow={1} width="35em" placeholder="" />
            <InputArea value={indexToArgument[selectedIndex].type} prefix="Type: " initEditing={indexToArgument[selectedIndex].type === ""} onSubmit={handleNameChange} minRow={1} width="35em" placeholder="" />
            <InputArea value={helpText} prefix="Help: " initEditing={false} onSubmit={handleNameChange} minRow={1} width="35em" placeholder="" />
            <Row>
                <Col xxl='2'>
                    <h6>Required?:</h6>
                </Col>
                <Col xxl='10'>
                    <input type="checkbox" checked={indexToArgument[selectedIndex].required ? indexToArgument[selectedIndex].required! : false} onChange={handleNameChange} />
                </Col>
            </Row>
        </div>
        )
    }

    return (<div>
        <h5>Arguments: </h5>
        <Row>
            <Col xxl='3'>
                <ArgumentsTree />
            </Col>
            <Col xxl='9'>
                <ArgumentsEdit />
            </Col>
        </Row>

    </div>
    );
};