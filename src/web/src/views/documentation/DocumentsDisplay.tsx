import * as React from 'react';
import { AppAppBar } from '../../components/AppAppBar';
import { Typography, Box, Dialog, Slide, Drawer, Toolbar } from '@mui/material';
import DocumentsFolderTree from './DocumentsFolderTree'
import { CommandTreeNode, CommandTreeLeaf } from '../workspace/WSEditorCommandTree'
import axios from 'axios';
import ReactMarkdown from 'react-markdown'


import WSEditorToolBar from '../workspace/WSEditorToolBar';

const drawerWidth = 300;


interface DocumentsDisplayState {
    selected: string,

    fileMap: { [id: string]: string },
    folderMap: { [id: string]: string },
    documentTree: CommandTreeNode[],
    markDownContent: string,
}

interface PathMap {
    children?: { [name: string]: PathMap },
    names?: string[],
    curr?: string[],
}

export default class DocumentsDisplay extends React.Component<{}, DocumentsDisplayState> {

    constructor(props: any) {
        super(props);
        this.state = {
            selected: "",
            folderMap: {},
            fileMap: {},
            documentTree: [],
            markDownContent: ""
        }
    }

    componentDidMount() {
        this.loadDocuments()
    }

    parseFilePath = (pathMap: PathMap, file_path_split: string[], index: number) => {
        if (index >= file_path_split.length) {
            return
        }
        const curr = file_path_split[index]
        pathMap.names = file_path_split.slice(0, index)
        if (index === file_path_split.length - 1) {
            if (!pathMap.curr) {
                pathMap.curr = []
            }
            pathMap.curr.push(curr)
        } else {
            if (!pathMap.children) {
                pathMap.children = {}
            }
            if (!(curr in pathMap.children)) {
                pathMap.children[curr] = {}
            }
            this.parseFilePath(pathMap.children[curr], file_path_split, index + 1)
        }
    }

    parseMap = (pathMap: PathMap) => {
        const { names, curr, children } = pathMap

        let node: CommandTreeNode = {
            id: !names||(names.length===1 && names[0]==='.') ? "Docs" : names.join('/'),
            names: !names||(names.length===1 && names[0]==='.') ? ["Docs"] : names,
            canDelete: false
        };
        if (children) {
            node.nodes = Object.keys(children).map(childName => {
                let child = children[childName]
                return this.parseMap(child)
            })
        }
        if (curr) {
            node.leaves = curr.map(file => {
                let leaf: CommandTreeLeaf = {
                    id: names ? names.join('/') + `/${file}` : file,
                    names: names ? [...names, file] : [file]
                }
                return leaf
            })
        }
        return node
    }

    loadDocuments = async () => {
        try {
            const res = await axios.get('/Documentation/all')
            const pathMap = {}
            console.log(res.data)
            res.data.forEach((file_path: string) => {
                this.parseFilePath(pathMap, file_path.split('/'), 1)
            })
            console.log(pathMap)
            let treeData = this.parseMap(pathMap)
            this.setState({documentTree: [treeData]})

        } catch (err) {
            return console.log(err);
        }

    }

    handleTreeSelect = (nodeId: string) => {
        this.setState({selected:nodeId}, async ()=>{
            if (!nodeId.endsWith('.md')){
                return
            }
            try {
                console.log(nodeId)
                const res = await axios.get(`/Documentation/${nodeId}`)
                if (res.data){
                    console.log(res.data)
                    this.setState({markDownContent: res.data})
                }
            } catch (err) {
                return console.log(err);
            }
        })
        
    }

    render() {
        const { documentTree, selected } = this.state;
        return (
            <React.Fragment>
                <AppAppBar pageName={'Documents'} />
                <Box sx={{ display: 'flex'}}>
                    <Drawer
                        variant="permanent"
                        sx={{
                            width: drawerWidth,
                            flexShrink: 0,
                            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
                            zIndex: (theme) => theme.zIndex.appBar - 1 
                        }}
                    >
                        <Toolbar />
                        {selected != null &&
                            <DocumentsFolderTree
                                commandTreeNodes={documentTree}
                                onSelected={this.handleTreeSelect}
                                selected={selected}
                            />
                        }
                    </Drawer>

                    <Box component='main' sx={{
                        flexGrow: 1,
                        p: 1,
                    }}>
                        <Toolbar sx={{ flexShrink: 0 }}/>
                        <ReactMarkdown children={this.state.markDownContent}/> 
                    </Box>
                    
                </Box>

            </React.Fragment>

        )
    }
}
