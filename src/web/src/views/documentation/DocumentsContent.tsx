import * as React from 'react';
import { AppAppBar } from '../../components/AppAppBar';
import { Typography, Box, Dialog, Slide, Drawer, Toolbar } from '@mui/material';
import DocumentsFolderTree from './DocumentsFolderTree'
import {CommandTreeNode} from '../workspace/WSEditorCommandTree'
import axios from 'axios';
import { rawListeners } from 'process';

const drawerWidth = 300;


interface DocumentsContentState {
    selected: string,

    fileMap: {[id: string]: string},
    folderMap: {[id: string]: string},
    documentTree: CommandTreeNode[],
}

interface PathMap {
    children?: {[name: string]: PathMap},
    names?: string[],
    curr?: string,
}

export default class DocumentsContent extends React.Component<{}, DocumentsContentState> {

    constructor(props: any) {
        super(props);
        this.state = {
            selected: "",
            folderMap: {},
            fileMap: {},
            documentTree: [],
        }
    }

    componentDidMount() {
        this.loadDocuments()
    }

    parseFilePath = (pathMap: PathMap, file_path_split: string[], index: number) => {
        const curr = file_path_split[index]
        pathMap.names = file_path_split.slice(0, index)
        if (index===file_path_split.length-1){
            pathMap.curr = curr
        } else {   
            if (!pathMap.children){
                pathMap.children = {}
            }
            if (!(curr in pathMap.children)){
                pathMap.children[curr] = {}
            }
            this.parseFilePath(pathMap.children[curr], file_path_split, index+1)
        }
    }

    loadDocuments = async () => {
        try {
            const res = await axios.get('/Documentation/all')
            const pathMap = {}

            res.data.forEach((file_path:string)=>{
                this.parseFilePath(pathMap, file_path.split('/'), 0)
            })
            console.log(pathMap)
        } catch (err) {
            return console.log(err);
        }
        
    }

    handleTreeSelect = (nodeId: string) => {
        // if (nodeId.startsWith('command:')) {
        //     this.setState(preState => {
        //         const selected = preState.folderMap[nodeId];
        //         return {
        //             ...preState,
        //             selected: selected,
        //         }
        //     })
        // } else if (nodeId.startsWith('group:')) {
        //     this.setState(preState => {
        //         const selected = preState.fileMap[nodeId];
        //         return {
        //             ...preState,
        //             selected: selected,
        //         }
        //     })
        // }
    }
    
    render() {
        const { documentTree, selected} = this.state;
        return (
            <React.Fragment>
                <AppAppBar pageName={'Documents'} />
                <Box sx={{display: 'flex'}}>
                    <Drawer
                        variant="permanent"
                        sx={{
                            width: drawerWidth,
                            flexShrink: 0,
                            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
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
                </Box>

            </React.Fragment>

        )
    }
}
