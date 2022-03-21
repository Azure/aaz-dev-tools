import * as React from 'react';
import TreeView from '@mui/lab/TreeView';
import TreeItem from '@mui/lab/TreeItem';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import {CommandTreeLeaf, CommandTreeNode} from '../workspace/WSEditorCommandTree'

interface DocumentsFolderTreeProps {
    commandTreeNodes: CommandTreeNode[]
    selected: string
    onSelected: (nodeId: string) => void
}


class DocumentsFolderTree extends React.Component<DocumentsFolderTreeProps> {

    onNodeSelected = (event: React.SyntheticEvent, nodeIds: string[] | string) => {
        if (typeof nodeIds === 'string') {
            this.props.onSelected(nodeIds);
        }
    }

    render() {
        const { commandTreeNodes, selected } = this.props;

        const renderLeaf = (leaf: CommandTreeLeaf) => {
            // const leafId = 'command:' +  leaf.names.join('/');
            const leafName = leaf.names[leaf.names.length - 1];
            return (
                <TreeItem key={leaf.id} nodeId={leaf.id} label={leafName} color='inherit' />
            )
        }

        const renderNode = (node: CommandTreeNode) => {
            // const nodeId = 'group:' +  node.names.join('/');
            const nodeName = node.names[node.names.length - 1];
            return (
                <TreeItem key={node.id} nodeId={node.id} label={nodeName} color='inherit'>
                    {Array.isArray(node.leaves) ? node.leaves.map((leaf) => renderLeaf(leaf)) : null}
                    {Array.isArray(node.nodes) ? node.nodes.map((subNode) => renderNode(subNode)) : null}
                </TreeItem>
            )
        }

        return (
            <TreeView
                defaultCollapseIcon={<ExpandMoreIcon />}
                defaultExpandIcon={<ChevronRightIcon />}
                onNodeSelect={this.onNodeSelected}
                selected={selected}
                sx={{
                    flexGrow: 1,
                    overflowY: 'auto',
                    p: 3
                }}
            >
                {commandTreeNodes.map((node) => renderNode(node))}
            </TreeView>
        )
    }

}

export default DocumentsFolderTree;
