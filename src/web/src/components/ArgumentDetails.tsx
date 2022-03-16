import React, { useState, useEffect, Component } from "react";
import IconButton from "@mui/material/IconButton";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import TextareaAutosize from '@mui/base/TextareaAutosize';
import { Tree, NodeModel, DragLayerMonitorProps } from "@minoru/react-dnd-treeview";
import { Row, Col } from "react-bootstrap"
import type { ArgGroups, TreeDataType, TreeNode, Argument } from "./ConfigEditor"
import styles from "./TreeView/App.module.css";


import { CustomData } from "./TreeView/types";
import { CustomNode } from "./TreeView/CustomNode";
import { CustomDragPreview } from "./TreeView/CustomDragPreview";


type Props = {
    argGroups: ArgGroups,
    id: NodeModel["id"],
    onNameChange: (id: NodeModel["id"], name: string) => void
};

const ArgumentsTree = (
    props: {
        treeData: any,
        selectedIndex: any,
        onClick: any,
        onSubmit: any,
        onDrop: any
    }
) => {
    console.log(props.treeData)
    return <div className={styles.app}>
        <Tree
            tree={props.treeData}
            rootId={0}
            render={(node: NodeModel<CustomData>, { depth, isOpen, onToggle }) => (
                <CustomNode node={node} depth={depth} isOpen={isOpen} isSelected={node.id === props.selectedIndex}
                    onToggle={onToggle} onClick={props.onClick} onSubmit={props.onSubmit} editable={false} />
            )}
            dragPreviewRender={(
                monitorProps: DragLayerMonitorProps<CustomData>
            ) => <CustomDragPreview monitorProps={monitorProps} />}
            onDrop={props.onDrop}
            canDrag={() => { return false }}
            classes={{
                root: styles.treeRoot,
                draggingSource: styles.draggingSource,
                dropTarget: styles.dropTarget,
            }}
            initialOpen={true}
        />
    </div>
}


export const ArgumentDetails: React.FC<Props> = (props) => {
    let initTreeData: TreeDataType = [];
    let treeData: TreeDataType = [];
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
        args.forEach(arg => {
            let text = ""
            arg.options?.forEach((option, index) => {
                if (index > 0) {
                    text += ' '
                }
                if (option.length > 1) {
                    text += '--'
                } else {
                    text += '-'
                }
                text += option
            })
            text += arg.required ? "(*)" : ""

            const hasChildren = (arg.args || arg.type === 'array<object>') ? true : false
            let treeNode: TreeNode = {
                id: currentIndex,
                parent: parentIndex,
                text: text,
                droppable: hasChildren,
                data: { hasChildren: hasChildren, type: hasChildren ? 'CommandGroup' : 'Command', allowDelete: false }
            }
            indexToArgument[currentIndex] = arg
            const nextParentIndex = currentIndex
            currentIndex += 1
            initTreeData.push(treeNode)
            if (arg.args) {
                parseArguments(nextParentIndex, arg.args)
            }
            if (arg.item) {
                parseArguments(nextParentIndex, arg.item.args)
            }
        })
    }

    const parseArgGroups = (parentIndex: number, argGroups: ArgGroups) => {
        if (!argGroups) {
            return
        }
        argGroups.forEach(argGroup => {
            if (!argGroup.name) {
                if (argGroup.args) {
                    parseArguments(parentIndex, argGroup.args)
                }
            } else {
                const hasChildren = argGroup.args ? true : false
                let treeNode: TreeNode = {
                    id: currentIndex,
                    parent: parentIndex,
                    text: argGroup.name,
                    droppable: hasChildren,
                    data: { hasChildren: hasChildren, type: 'CommandGroup', allowDelete: false }
                }
                indexToArgument[currentIndex] = argGroup
                const nextParentIndex = currentIndex
                currentIndex += 1
                initTreeData.push(treeNode)
                if (argGroup.args) {
                    parseArguments(nextParentIndex, argGroup.args)
                }
            }
        })
    }

    const load = () => {
        if (props.argGroups.length > 1) {
            parseArgGroups(0, props.argGroups)
        } else {
            parseArguments(0, props.argGroups[0].args)
        }
        treeData = initTreeData
        // console.log(indexToArgument)
        // console.log(initTreeData)

    }

    load()

    const handleClick = (id: NodeModel["id"]) => {
        setSelectedIndex(Number(id))
        console.log(indexToArgument[Number(id)])
    }
    const handleNameChange = () => { }
    const handleDrop = () => { }




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
        if (!indexToArgument[selectedIndex]) {
            return <div />
        }
        if (!indexToArgument[selectedIndex].options) {
            return <div />
        }
        const helpText = indexToArgument[selectedIndex].help?.short ? indexToArgument[selectedIndex].help?.short! : ""
        // const checked = indexToArgument[selectedIndex].required? indexToArgument[selectedIndex].required! : false

        return (<div>
            {/* <InputArea value={initTreeData[selectedIndex - 1].text} prefix="Option List: " initEditing={initTreeData[selectedIndex - 1].text === ""} editable={false} onSubmit={handleNameChange} minRow={1} width="35em" placeholder="" /> */}
            <InputArea value={indexToArgument[selectedIndex].type!} prefix="Type: " initEditing={indexToArgument[selectedIndex].type === ""} editable={false} onSubmit={handleNameChange} minRow={1} width="35em" placeholder="" />
            <InputArea value={helpText} prefix="Help: " initEditing={false} editable={false} onSubmit={handleNameChange} minRow={1} width="35em" placeholder="" />
            {/* <Row>
                <Col xxl='2'>
                    <h6>Required?:</h6>
                </Col>
                <Col xxl='10'>
                    <input type="checkbox" checked={indexToArgument[selectedIndex].required ? indexToArgument[selectedIndex].required! : false} onChange={handleNameChange} />
                </Col>
            </Row> */}
        </div>
        )
    }

    return (<div>
        <h5>Arguments: </h5>
        <h6> Required (*)</h6>
        <Row>
            <Col xxl='4'>
                {treeData && treeData.length > 0 && <ArgumentsTree treeData={treeData} selectedIndex={selectedIndex} onDrop={handleDrop} onClick={handleClick} onSubmit={handleNameChange} />}
            </Col>
            <Col xxl='8'>
                <ArgumentsEdit />
            </Col>
        </Row>

    </div>
    );
};