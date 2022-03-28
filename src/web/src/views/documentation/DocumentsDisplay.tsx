import * as React from 'react';
import { Box, Drawer, Toolbar, Container, Card, Typography, TypographyProps, styled, TableRow, TableCell, Table, TableContainer, TableHead, Link } from '@mui/material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown'

import { useParams } from 'react-router';
import DocumentsTree, { DecodeResponseDocumentTreeNode, DocumentTreeNode, ResponseDocumentTreeNode } from './DocumentsTree';
import { CodeProps, HeadingProps, UnorderedListProps } from 'react-markdown/lib/ast-to-react';
import { Prism } from 'react-syntax-highlighter'
import { okaidia as prismStyle } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';

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
                    <Box sx={{ pt: 4, pb: 20 }}>
                        {markDownContent && <ReactMarkdown
                            children={markDownContent}
                            remarkPlugins={[remarkGfm]}
                            components={{
                                p: (props) => {
                                    return (<Box sx={{ mt: 2 }}>
                                        <PComponent>{props.children}</PComponent>
                                    </Box>)
                                },
                                h1: (props: React.PropsWithChildren<HeadingProps>) => {
                                    return (<Box sx={{
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        mt: 2,
                                        mb: 2,
                                    }}>
                                        <H1Component>{props.children}</H1Component>
                                    </Box>)
                                },
                                h2: (props: React.PropsWithChildren<HeadingProps>) => {
                                    return (<Box sx={{ mt: 6, mb: 2 }}><H2Component>{props.children}</H2Component></Box>)
                                },
                                h3: (props: React.PropsWithChildren<HeadingProps>) => {
                                    return (<Box sx={{ mt: 4, mb: 4 }}><H3Component>{props.children}</H3Component></Box>)
                                },
                                ul: (props: React.PropsWithChildren<UnorderedListProps>) => {
                                    return (<Box sx={{ listStyleType: props.depth < 1 ? "disc" : "circle", p: 1, ml: 4 }}>{props.children}</Box>)
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
                                        return (
                                            <Card variant="outlined" sx={{ mt: 3, ml: 2, mr: 2, paddingLeft: 1, paddingRight: 1 }}>
                                                <Prism
                                                    style={prismStyle}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    children={props.children}
                                                />
                                            </Card>
                                        )
                                    } else {
                                        return (<code className={props.className} {...props} />)
                                    }
                                },
                                img: (props) => {
                                    return (
                                        <Box component='span' sx={{
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            mt: 2, mb: 2, ml: 2, p: 2,
                                        }}>
                                            <img alt={props.alt} src={props.src} title={props.title} style={{ maxWidth: "95%" }} />
                                        </Box>
                                    )
                                },
                                table: (props) => {
                                    return (
                                        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", p: 2 }}>
                                            <TableContainer component={Card} variant='outlined'>
                                                <Table sx={{ minWidth: 400 }}>{props.children}</Table>
                                            </TableContainer>
                                        </Box>
                                    )
                                },
                                thead: (props) => {
                                    return (<TableHead>
                                        {props.children}
                                    </TableHead>)
                                },
                                tr: (props) => {
                                    return (<TableRow sx={{ '&:last-child td': { border: 0 } }}>{props.children}</TableRow>)
                                },
                                th: (props) => {
                                    return (<TableCell>{props.children}</TableCell>)
                                },
                                td: (props) => {
                                    return (<TableCell>{props.children}</TableCell>)
                                },
                                a: (props) => {
                                    return (<Link href={props.href}>{props.children}</Link>)
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
    fontSize: 36,
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
