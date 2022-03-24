import * as React from 'react';
import { Box, Drawer, Toolbar, Container, Typography, TypographyProps, styled } from '@mui/material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown'

import { useParams } from 'react-router';
import DocumentsTree, { DecodeResponseDocumentTreeNode, DocumentTreeNode, ResponseDocumentTreeNode } from './DocumentsTree';
import { CodeProps, HeadingProps, UnorderedListProps } from 'react-markdown/lib/ast-to-react';
import { Prism} from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const drawerWidth = 300;

function DocumentsDisplay(props: {
    params: {
        docId?: string
    }
}) {
    const [selected, setSelected] = React.useState<string | undefined>(undefined);
    const [documentTree, setDocumentTree] = React.useState<DocumentTreeNode[]>([]);
    const [markDownContent, setMarkDownContent] = React.useState<string | undefined>(undefined);
    const [expanded, setExpanded] = React.useState<string[]>([]);

    const loadDocument = (nodeId: string) => {
        axios.get(`/Docs/Index/${nodeId}`)
            .then(res => {
                if (res.status === 204) {
                    return
                }
                const content = res.data;
                setMarkDownContent(content);
            }).catch(err => console.error(err.response));
    }

    const handleTreeSelect = (nodeId: string) => {
        setSelected(nodeId);
        loadDocument(nodeId);
    }

    React.useEffect(() => {
        if (props.params.docId) {
            handleTreeSelect(props.params.docId);
        }
    }, [props.params.docId])

    
    const loadDocumentIndex = async () => {
        try {
            const res = await axios.get('/Docs/Index');
            const pages: ResponseDocumentTreeNode[] = res.data;
            const dt: DocumentTreeNode[] = pages.map(e => DecodeResponseDocumentTreeNode(e));
            return dt
        } catch (err) {
            console.error(err);
        }
    }

    React.useEffect(() => {
        loadDocumentIndex().then((dt) => {
            if (dt) {
                const expandedIds: string[] = [];
                const iterNode = (node: DocumentTreeNode) => {
                    if (node.nodes) {
                        expandedIds.push(node.id);
                        node.nodes.forEach(subNode => iterNode(subNode));
                    }
                }
                dt.forEach(subNode => iterNode(subNode));
                setDocumentTree(dt);
                setExpanded(expandedIds);
                if (!props.params.docId && dt.length > 0) {
                    handleTreeSelect(dt[0].id);
                }
            }
        })
    }, [])

    return (
        <React.Fragment>
            <Box sx={{ display: 'flex' }}>
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
                    {selected && documentTree.length > 0 && <DocumentsTree
                        nodes={documentTree}
                        selected={selected}
                        onSelected={handleTreeSelect}
                        expanded={expanded}
                    />}
                </Drawer>

                <Container sx={{
                    flexGrow: 1,
                }}>
                    <Toolbar sx={{ flexShrink: 0 }} />
                    <Box sx={{ pt: 2 }}>
                        {markDownContent && <ReactMarkdown
                            children={markDownContent}
                            components={{
                                p: (props) => {
                                    return (<PComponent>{props.children}</PComponent>)
                                },
                                h1: (props: React.PropsWithChildren<HeadingProps>) => {
                                    return (<H1Component>{props.children}</H1Component>)
                                },
                                h2: (props: React.PropsWithChildren<HeadingProps>) => {
                                    return (<H2Component>{props.children}</H2Component>)
                                },
                                h3: (props: React.PropsWithChildren<HeadingProps>) => {
                                    return (<H3Component>{props.children}</H3Component>)
                                },
                                ul: (props: React.PropsWithChildren<UnorderedListProps>) => {
                                    return (<Box sx={{listStyleType: props.depth < 1 ? "disc" : "circle", p: 1, ml: 1}}>{props.children}</Box>)
                                },
                                li: (props) => {
                                    return (<Typography component="li"
                                     fontSize={15}
                                      fontWeight={600}                                      
                                      >{props.children}</Typography>)
                                },
                                code: (props: React.PropsWithChildren<CodeProps>) => {
                                    const match = /language-(\w+)/.exec(props.className || '')
                                    if (!props.inline && match) {
                                        return (<Prism
                                            style={vscDarkPlus}
                                            language={match[1]}
                                            PreTag="div"
                                            showLineNumbers={true}
                                            children={props.children}
                                        />)
                                    } else {
                                        return (<code className={props.className} {...props} />)
                                    }
                                }
                            }}
                        />}
                    </Box>
                </Container>
            </Box>
        </React.Fragment>
    )
}

const H1Component = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 32,
    fontWeight: 600,
}))

const H2Component = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 20,
    fontWeight: 600,
    marginTop: 16,
}))

const H3Component = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 18,
    fontWeight: 600,
}))

const PComponent = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 16,
    fontWeight: 400,
}))



const DocumentsDisplayWrapper = (props: any) => {
    const params = useParams()
    return <DocumentsDisplay params={params} {...props} />
}

export { DocumentsDisplayWrapper as DocumentsDisplay };
