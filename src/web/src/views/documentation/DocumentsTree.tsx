import * as React from 'react';
import TreeView from '@mui/lab/TreeView';
import TreeItem from '@mui/lab/TreeItem';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';


interface DocumentTreeNode {
    id: string
    title: string
    file?: string
    nodes?: DocumentTreeNode[]
}

interface ResponseDocumentTreeNode {
    id: string
    title: string
    file?: string
    pages?: ResponseDocumentTreeNode[]
}

interface DocumentsTreeProps {
    nodes: DocumentTreeNode[]
    expanded: string[]
    selected: string
    onSelected: (docId: string) => void
}

class DocumentsTree extends React.Component<DocumentsTreeProps> {
    onNodeSelected = (event: React.SyntheticEvent, nodeIds: string[] | string) => {
        if (typeof nodeIds === 'string') {
            this.props.onSelected(nodeIds);
        }
    }

    render() {

        const renderNode = (node: DocumentTreeNode) => {
            const title = node.title;
            return (
                <TreeItem key={node.id} nodeId={node.id} label={title} color='inherit'>
                    {Array.isArray(node.nodes) ? node.nodes.map((subNode) => renderNode(subNode)) : null}
                </TreeItem>
            )
        }

        return (<TreeView
            defaultCollapseIcon={<ExpandMoreIcon />}
            defaultExpandIcon={<ChevronRightIcon />}
            onNodeSelect={this.onNodeSelected}
            selected={this.props.selected}
            expanded={this.props.expanded}
            sx={{
                flexGrow: 1,
                overflowY: 'auto',
                p: 3
            }}
        >
            {this.props.nodes.map((node) => renderNode(node))}
        </TreeView>
        )
    }
}

const DecodeResponseDocumentTreeNode = (node: ResponseDocumentTreeNode): DocumentTreeNode => {
    return {
        id: node.id,
        title: node.title,
        file: node.file,
        nodes: node.pages?.map(e => DecodeResponseDocumentTreeNode(e)),
    }
}

export default DocumentsTree;

export type {DocumentTreeNode, ResponseDocumentTreeNode};

export {DecodeResponseDocumentTreeNode};
