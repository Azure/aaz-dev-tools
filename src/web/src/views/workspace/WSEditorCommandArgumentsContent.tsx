import { Alert, Box, Button, ButtonBase, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, InputLabel, LinearProgress, Radio, RadioGroup, TextField, Typography, TypographyProps } from '@mui/material';
import { styled } from '@mui/system';
import axios from 'axios';
import React, { useState, useEffect } from 'react';
import { CardTitleTypography, ExperimentalTypography, LongHelpTypography, PreviewTypography, ShortHelpPlaceHolderTypography, ShortHelpTypography, SmallExperimentalTypography, SmallPreviewTypography, StableTypography, SubtitleTypography } from './WSEditorTheme';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import EditIcon from '@mui/icons-material/Edit';
import CallSplitSharpIcon from '@mui/icons-material/CallSplitSharp';
// import CallMergeSharpIcon from '@mui/icons-material/CallMergeSharp';


function WSEditorCommandArgumentsContent(props: {
    commandUrl: string,
}) {

    const [args, setArgs] = useState<CMDArg[]>([]);
    const [displayArgumentDialog, setDisplayArgumentDialog] = useState<boolean>(false);
    const [editArg, setEditArg] = useState<CMDArg | undefined>(undefined);
    const [displayFlattenDialog, setDisplayFlattenDialog] = useState<boolean>(false);
    const [clsArgDefineMap, setClsArgDefineMap] = useState<ClsArgDefinitionMap>({});

    const refreshData = () => {
        axios.get(props.commandUrl)
            .then(res => {
                const { args, clsDefineMap } = decodeResponse(res.data);
                setArgs(args);
                setClsArgDefineMap(clsDefineMap);
            }).catch(err => console.error(err));
    }

    useEffect(() => {
        refreshData();
    }, [props.commandUrl]);

    const handleArgumentDialogClose = (newArg?: CMDArg) => {
        setDisplayArgumentDialog(false);
        setEditArg(undefined);
        if (newArg) {
            refreshData();
        }
    }

    const handleEditArgument = (arg: CMDArg) => {
        setEditArg(arg)
        setDisplayArgumentDialog(true)
    }

    const handleFlattenDialogClose = (flattened: boolean) => {
        setDisplayFlattenDialog(false)
        setEditArg(undefined);
        if (flattened) {
            refreshData();
        }
    }

    const handleArgumentFlatten = (arg: CMDArg) => {
        setEditArg(arg)
        setDisplayFlattenDialog(true)
    }

    return (
        <React.Fragment>
            <CardContent sx={{
                flex: '1 0 auto',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'stretch',
            }}>
                <Box sx={{
                    mb: 2,
                    display: 'flex',
                    flexDirection: 'row',
                    alignItems: "center"
                }}>
                    <CardTitleTypography sx={{ flexShrink: 0 }}>
                        [ ARGUMENT ]
                    </CardTitleTypography>
                </Box>
                <ArgumentNavigation commandUrl={props.commandUrl} args={args} clsArgDefineMap={clsArgDefineMap} onEdit={handleEditArgument} onFlatten={handleArgumentFlatten} />
            </CardContent>

            {displayArgumentDialog && <ArgumentDialog commandUrl={props.commandUrl} arg={editArg!} clsArgDefineMap={clsArgDefineMap} open={displayArgumentDialog} onClose={handleArgumentDialogClose} />}
            {displayFlattenDialog && <FlattenDialog commandUrl={props.commandUrl} arg={editArg! as CMDObjectArg} clsArgDefineMap={clsArgDefineMap} open={displayFlattenDialog} onClose={handleFlattenDialogClose} />}
        </React.Fragment>
    )
}


interface ArgIdx {
    var: string,
    displayKey: string,
}

function ArgumentNavigation(props: {
    commandUrl: string,
    args: CMDArg[],
    clsArgDefineMap: ClsArgDefinitionMap,
    onEdit: (arg: CMDArg) => void,
    onFlatten: (arg: CMDArg) => void,
}) {
    const [argIdxStack, setArgIdxStack] = useState<ArgIdx[]>([]);

    const getArgProps = (selectedArgBase: CMDArgBase): { title: string, props: CMDArg[], flattenArgVar: string | undefined } | undefined => {
        if (selectedArgBase.type.startsWith('@')) {
            return getArgProps(props.clsArgDefineMap[(selectedArgBase as CMDClsArgBase).clsName]);
        }
        if (selectedArgBase.type === "object") {
            return {
                title: "Props",
                props: (selectedArgBase as CMDObjectArgBase).args,
                flattenArgVar: (selectedArgBase as CMDObjectArg).var,
            }
        } else if (selectedArgBase.type.startsWith("dict<")) {
            const itemProps = getArgProps((selectedArgBase as CMDDictArgBase).item);
            if (!itemProps) {
                return undefined;
            }
            return {
                title: "Dict Element Props",
                props: itemProps.props,
                flattenArgVar: undefined,
            }
        } else if (selectedArgBase.type.startsWith("array<")) {
            const itemProps = getArgProps((selectedArgBase as CMDArrayArgBase).item);
            if (!itemProps) {
                return undefined;
            }
            return {
                title: "Array Element Props",
                props: itemProps.props,
                flattenArgVar: undefined,
            }
        } else {
            return undefined;
        }
    }

    const getSelectedArg = (stack: ArgIdx[]): CMDArg | undefined => {
        if (stack.length === 0) {
            return undefined;
        } else {
            let args: CMDArg[] = [...props.args]
            let selectedArg: CMDArg | undefined = undefined;
            for (const i in stack) {
                const argVar = stack[i].var;
                selectedArg = args.find(arg => arg.var === argVar)
                if (!selectedArg) {
                    break
                }
                args = getArgProps(selectedArg)?.props ?? [];
            }
            return selectedArg
        }
    }

    useEffect(() => {
        setArgIdxStack([]);
    }, [props.commandUrl]);

    useEffect(() => {
        // update argument idx stack 
        const stack = [...argIdxStack];
        while (stack.length > 0 && !getSelectedArg(stack)) {
            stack.pop()
        }
        setArgIdxStack(stack);
    }, [props.args, props.clsArgDefineMap])

    const handleSelectSubArg = (subArgVar: string) => {
        let subArg
        if (argIdxStack.length > 0) {
            const arg = getSelectedArg(argIdxStack);
            if (!arg) {
                return
            }
            subArg = getArgProps(arg)?.props.find(a => a.var === subArgVar)
        } else {
            subArg = props.args.find(a => a.var === subArgVar)
        }

        if (!subArg) {
            return
        }
        const argIdx: ArgIdx = {
            var: subArg.var,
            displayKey: subArg.options[0],
        }
        if (argIdxStack.length === 0) {
            if (argIdx.displayKey.length === 1) {
                argIdx.displayKey = `-${argIdx.displayKey}`
            } else {
                argIdx.displayKey = `--${argIdx.displayKey}`
            }
        }

        let argType = subArg.type;
        if (argType.startsWith("@")) {
            argType = props.clsArgDefineMap[(subArg as CMDClsArg).clsName].type
        }
        if (argType.startsWith("dict<")) {
            argIdx.displayKey += "{}"
        } else if (argType.startsWith("array<")) {
            argIdx.displayKey += "[]"
        }

        setArgIdxStack([...argIdxStack, argIdx]);
    }

    const handleChangeArgIdStack = (end: number) => {
        setArgIdxStack(argIdxStack.slice(0, end));
    }

    const buildArgumentReviewer = () => {
        const selectedArg = getSelectedArg(argIdxStack)
        if (!selectedArg) {
            return (<></>)
        }

        const stage = selectedArg.stage

        return (
            <React.Fragment>
                <Box sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "flex-start",
                    justifyContent: "flex-start"
                }}>
                    <ArgNavBar argIdxStack={argIdxStack} onChangeArgIdStack={handleChangeArgIdStack} />
                    {stage === "Stable" && <StableTypography
                        sx={{ flexShrink: 0 }}
                    >
                        {stage}
                    </StableTypography>}
                    {stage === "Preview" && <PreviewTypography
                        sx={{ flexShrink: 0 }}
                    >
                        {stage}
                    </PreviewTypography>}
                    {stage === "Experimental" && <ExperimentalTypography
                        sx={{ flexShrink: 0 }}
                    >
                        {stage}
                    </ExperimentalTypography>}
                </Box>
                <ArgumentReviewer
                    arg={selectedArg}
                    depth={argIdxStack.length}
                    onEdit={() => { props.onEdit(selectedArg) }}
                />
            </React.Fragment>
        )
    }

    const buildArgumentPropsReviewer = () => {
        if (argIdxStack.length === 0) {
            if (props.args.length === 0) {
                return (<></>)
            }
            return (<ArgumentPropsReviewer
                title={"Argument Groups"}
                args={props.args}
                onFlatten={undefined}
                depth={argIdxStack.length}
                onSelectSubArg={handleSelectSubArg}
            />)
        } else {
            const selectedArg = getSelectedArg(argIdxStack)
            if (!selectedArg) {
                return (<></>)
            }
            const argProps = getArgProps(selectedArg)
            if (!argProps) {
                return (<></>)
            }
            const canFlatten = argProps.flattenArgVar !== undefined
            return (<ArgumentPropsReviewer
                title={argProps.title}
                args={argProps.props}
                depth={argIdxStack.length}
                onFlatten={canFlatten ? () => {
                    props.onFlatten(selectedArg!)
                } : undefined}
                onSelectSubArg={handleSelectSubArg}
            />)
        }
    }

    return (<React.Fragment>
        {argIdxStack.length > 0 && <React.Fragment>
            {buildArgumentReviewer()}
        </React.Fragment>}
        <React.Fragment>
            {buildArgumentPropsReviewer()}
        </React.Fragment>
    </React.Fragment>)
}


const NavBarItemTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}))

const NavBarItemHightLightedTypography = styled(NavBarItemTypography)<TypographyProps>(({ theme }) => ({
    color: '#5d64cf',
}))

function ArgNavBar(props: {
    argIdxStack: ArgIdx[],
    onChangeArgIdStack: (end: number) => void,
}) {

    return (
        <React.Fragment>
            <Box
                sx={{
                    flexGrow: 1,
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    justifyContent: "flex-start",
                    mt: 1, mb: 0.5, mr: 2,
                }}>
                <ButtonBase key="Back" onClick={() => {
                    props.onChangeArgIdStack(0)
                }}>
                    <ArrowBackIosIcon sx={{ fontSize: 14 }} />
                </ButtonBase>
                {props.argIdxStack.slice(0, -1).map((argIdx, index) => (
                    <ButtonBase
                        key={`${index}`}
                        onClick={() => {
                            props.onChangeArgIdStack(index + 1)
                        }}
                    >
                        <NavBarItemTypography sx={{ flexShrink: 0 }} >{index > 0 ? `.${argIdx.displayKey}` : argIdx.displayKey}</NavBarItemTypography>
                    </ButtonBase>
                ))}
                <ButtonBase
                    key={`${props.argIdxStack.length - 1}`}
                    onClick={() => {
                        props.onChangeArgIdStack(props.argIdxStack.length)
                    }}
                >
                    <NavBarItemHightLightedTypography sx={{ flexShrink: 0 }} >{props.argIdxStack.length > 1 ? `.${props.argIdxStack[props.argIdxStack.length - 1].displayKey}` : props.argIdxStack[props.argIdxStack.length - 1].displayKey}</NavBarItemHightLightedTypography>
                </ButtonBase>
            </Box>
        </React.Fragment>
    )
}

const spliceArgOptionsString = (arg: CMDArg, depth: number) => {
    return arg.options.map((option) => {
        if (depth === 0) {
            if (option.length === 1) {
                return '-' + option;
            } else {
                return '--' + option;
            }
        } else {
            return '.' + option;
        }
    }).join(" ")
}


const ArgNameTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 26,
    fontWeight: 700,
}))

const ArgTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 700,
}))

const ArgRequiredTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: '#fad105',
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 200,
}))

const ArgEditTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: "#5d64cf",
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}));

const ArgChoicesTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 14,
    fontWeight: 700,
}))

function ArgumentReviewer(props: {
    arg: CMDArg,
    depth: number,
    onEdit: () => void,
}) {
    const [choices, setChoices] = useState<string[]>([]);

    const buildArgOptionsString = () => {
        const argOptionsString = spliceArgOptionsString(props.arg, props.depth - 1);
        return (<ArgNameTypography>{argOptionsString}</ArgNameTypography>)
    }

    useEffect(() => {
        const newChoices: string[] = [];
        if ((props.arg as CMDStringArg).enum) {
            const items = (props.arg as CMDStringArg).enum!.items;
            for (const idx in items) {
                const enumItem = items[idx];
                newChoices.push(enumItem.name);
            }
        } else if ((props.arg as CMDNumberArg).enum) {
            const items = (props.arg as CMDNumberArg).enum!.items;
            for (const idx in items) {
                const enumItem = items[idx];
                newChoices.push(enumItem.name);
            }
        }
        setChoices(newChoices);
    }, [props.arg]);


    return (<React.Fragment>
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                justifyContent: "flex-start",
                mt: 1,
                mb: 2
            }}>
            <Box sx={{
                flexGrow: 1,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
            }}>
                {buildArgOptionsString()}
                <Button sx={{ flexShrink: 0, ml: 3 }}
                    startIcon={<EditIcon color="info" fontSize='small' />}
                    onClick={() => { props.onEdit() }}
                >
                    <ArgEditTypography>Edit</ArgEditTypography>
                </Button>
            </Box>

            <Box sx={{
                display: "flex",
                flexDirection: "row",
                justifyContent: "flex-start",
                ml: 6,
            }}>
                <ArgTypeTypography>{`/${props.arg.type}/`}</ArgTypeTypography>
                <Box sx={{ flexGrow: 1 }} />
                {props.arg.required && <ArgRequiredTypography>[Required]</ArgRequiredTypography>}
            </Box>
            {choices.length > 0 && <ArgChoicesTypography sx={{ ml: 6, mt:0.5}}>
                {`Choices: ` + choices.join(', ')}
                </ArgChoicesTypography>}
            {props.arg.help?.short && <ShortHelpTypography sx={{ ml: 6, mt: 1.5 }}> {props.arg.help?.short} </ShortHelpTypography>}
            {!(props.arg.help?.short) && <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>Please add argument short summery!</ShortHelpPlaceHolderTypography>}
            {props.arg.help?.lines && <Box sx={{ ml: 6, mt: 1, mb: 1 }}>
                {props.arg.help.lines.map((line, idx) => (<LongHelpTypography key={idx}>{line}</LongHelpTypography>))}
            </Box>}
        </Box>
    </React.Fragment>)
}

function ArgumentDialog(props: {
    commandUrl: string,
    arg: CMDArg,
    clsArgDefineMap: ClsArgDefinitionMap,
    open: boolean,
    onClose: (newArg?: CMDArg) => void,
}) {
    const [updating, setUpdating] = useState<boolean>(false);
    const [stage, setStage] = useState<string>("");
    const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
    const [options, setOptions] = useState<string>("");
    const [singularOptions, setSingularOptions] = useState<string | undefined>(undefined);
    const [group, setGroup] = useState<string>("")
    const [hide, setHide] = useState<boolean>(false);
    const [shortHelp, setShortHelp] = useState<string>("");
    const [longHelp, setLongHelp] = useState<string>("");

    const handleClose = () => {
        setInvalidText(undefined);
        props.onClose();
    }

    const handleModify = (event: any) => {
        let name = options.trim();
        let sName = singularOptions?.trim() ?? undefined;
        let sHelp = shortHelp.trim();
        let lHelp = longHelp.trim();
        let gName = group.trim();

        const names = name.split(' ').filter(n => n.length > 0);
        const sNames = sName?.split(' ').filter(n => n.length > 0) ?? undefined;

        setInvalidText(undefined);

        if (names.length < 1) {
            setInvalidText(`Argument 'Option names' is required.`)
            return
        }

        for (const idx in names) {
            const piece = names[idx];
            if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                setInvalidText( `Invalid 'Option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `)
                return
            }
        }

        if (sNames) {
            for (const idx in sNames) {
                const piece = sNames[idx];
                if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                    setInvalidText( `Invalid 'Singular option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `)
                    return
                }
            }
        }

        if (sHelp.length < 1) {
            setInvalidText(`Field 'Short Summery' is required.`)
            return
        }

        let lines: string[] | null = null;
        if (lHelp.length > 1) {
            lines = lHelp.split('\n').filter(l => l.length > 0);
        }

        setUpdating(true);

        const argumentUrl = `${props.commandUrl}/Arguments/${props.arg.var}`

        axios.patch(argumentUrl, {
            options: names,
            singularOptions: sNames,
            stage: stage,
            group: gName.length > 0 ? gName : null,
            hide: hide,
            help: {
                short: sHelp,
                lines: lines
            }
        }).then(res => {
            let newArg = decodeArg(res.data).arg;
            setUpdating(false);
            props.onClose(newArg);
        }).catch(err => {
            console.error(err.response);
            if (err.response?.data?.message) {
                setInvalidText(`ResponseError: ${err.response!.data!.message!}`);
            }
            setUpdating(false);
        });
    }

    useEffect(() => {
        let {arg, clsArgDefineMap} = props;

        setOptions(arg.options.join(" "));
        
        if (arg.type.startsWith("array")) {
            setSingularOptions((arg as CMDArrayArg).singularOptions?.join(" ") ?? "")
        } else if (arg.type.startsWith('@') && clsArgDefineMap[(arg as CMDClsArg).clsName].type.startsWith("array")) {
            setSingularOptions((arg as CMDClsArg).singularOptions?.join(" ") ?? "")
        } else {
            setSingularOptions(undefined);
        }
        setStage(props.arg.stage);
        setGroup(props.arg.group);
        setHide(props.arg.hide);
        setShortHelp(props.arg.help?.short ?? "");
        setLongHelp(props.arg.help?.lines?.join("\n") ?? "");
        setUpdating(false);
    }, [props.arg]);

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
            sx={{ '& .MuiDialog-paper': { width: '80%' } }}
        >
            <DialogTitle>Modify Argument</DialogTitle>
            <DialogContent dividers={true}>
                {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                <TextField
                    id="options"
                    label="Option names"
                    helperText="You can input multiple names separated by a space character"
                    type="text"
                    fullWidth
                    variant='standard'
                    value={options}
                    onChange={(event: any) => {
                        setOptions(event.target.value)
                    }}
                    margin="normal"
                    required
                />
                {singularOptions !== undefined && <TextField
                    id="singularOptions"
                    label="Singular option names"
                    type="text"
                    fullWidth
                    variant='standard'
                    value={singularOptions}
                    onChange={(event: any) => {
                        setSingularOptions(event.target.value)
                    }}
                    margin="normal"
                />}
                <TextField
                    id="group"
                    label="Argument Group"
                    type="text"
                    fullWidth
                    variant='standard'
                    value={group}
                    onChange={(event: any) => {
                        setGroup(event.target.value)
                    }}
                    margin="normal"
                />
                <InputLabel required shrink sx={{ font: "inherit" }}>Stage</InputLabel>
                <RadioGroup
                    row
                    value={stage}
                    name="stage"
                    onChange={(event: any) => {
                        setStage(event.target.value);
                    }}
                >
                    <FormControlLabel value="Stable" control={<Radio />} label="Stable" sx={{ ml: 4 }} />
                    <FormControlLabel value="Preview" control={<Radio />} label="Preview" sx={{ ml: 4 }} />
                    <FormControlLabel value="Experimental" control={<Radio />} label="Experimental" sx={{ ml: 4 }} />
                </RadioGroup>
                {/* TODO: support hide argument */}
                {/* {!props.arg.required && <React.Fragment>
                    <InputLabel shrink sx={{ font: "inherit" }}>Hide Argument</InputLabel>
                    <Switch sx={{ ml: 4 }}
                        checked={hide}
                        onChange={(event: any) => {
                            setHide(!hide);
                        }}
                    />
                </React.Fragment>} */}
                <TextField
                    id="shortSummery"
                    label="Short Summery"
                    type="text"
                    fullWidth
                    variant='standard'
                    value={shortHelp}
                    onChange={(event: any) => {
                        setShortHelp(event.target.value);
                    }}
                    margin="normal"
                    required
                />
                <TextField
                    id="longSummery"
                    label="Long Summery"
                    helperText="Please add long summer in lines."
                    type="text"
                    fullWidth
                    multiline
                    variant='standard'
                    value={longHelp}
                    onChange={(event: any) => {
                        setLongHelp(event.target.value);
                    }}
                    margin="normal"
                />
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='info' />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleModify}>Save</Button>
                </React.Fragment>}
            </DialogActions>
        </Dialog>
    )
}

function FlattenDialog(props: {
    commandUrl: string,
    arg: CMDObjectArg,
    clsArgDefineMap: ClsArgDefinitionMap,
    open: boolean,
    onClose: (flattened: boolean) => void,
}) {
    const [updating, setUpdating] = useState<boolean>(false);
    const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
    const [subArgOptions, setSubArgOptions] = useState<{var: string, options: string}[]>([]);

    useEffect(() => {
        let {arg} = props;
        const subArgOptions = arg.args.map(value => {
            return {
                var: value.var,
                options: value.options.join(" "),
            };
        });
        
        setSubArgOptions(subArgOptions);
    }, [props.arg]);

    const handleClose = () => {
        setInvalidText(undefined);
        props.onClose(false);
    }

    const handleFlatten = () => {
        setInvalidText(undefined);

        const argOptions: {[argVar:string]: string[]} = {};
        let invalidText: string | undefined = undefined;

        subArgOptions.forEach((arg, idx) => {
            const names = arg.options.split(' ').filter(n => n.length > 0);
            if (names.length < 1) {
                invalidText = `Prop ${idx+1} option name is required.`
                return
            }
            
            for (const idx in names) {
                const piece = names[idx];
                if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                    invalidText = `Invalid 'Prop ${idx+1} option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `
                    return
                }
            }
            argOptions[arg.var] = names;
        });
        if (invalidText !== undefined) {
            setInvalidText(invalidText);
            return
        }

        setUpdating(true);

        const flattenUrl = `${props.commandUrl}/Arguments/${props.arg.var}/Flatten`

        axios.post(flattenUrl, {
            subArgsOptions: argOptions,
        }).then(res => {
            setUpdating(false);
            props.onClose(true);
        }).catch(err => {
            console.error(err.response);
            if (err.response?.data?.message) {
                setInvalidText(`ResponseError: ${err.response!.data!.message!}`);
            }
            setUpdating(false);
        });
    }

    const buildSubArgText = (arg: {var: string, options: string}, idx: number) => {
        return (<TextField
            id={`subArg-${arg.var}`}
            key={arg.var}
            label={`Prop ${idx+1}`}
            helperText={ idx === 0 ? "You can input multiple names separated by a space character" : undefined}
            type="text"
            fullWidth
            variant='standard'
            value={arg.options}
            onChange={(event: any) => {
                const options = subArgOptions.map(value => {
                    if (value.var == arg.var) {
                        return {
                            ...value,
                            options: event.target.value,
                        }
                    } else {
                        return value
                    }
                });
                setSubArgOptions(options)
            }}
            margin="normal"
            required
        />)
    }

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
            sx={{ '& .MuiDialog-paper': { width: '80%' } }}
        >
            <DialogTitle>Flatten Props</DialogTitle>
            <DialogContent dividers={true}>
                {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                {subArgOptions.map(buildSubArgText)}
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='info' />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleFlatten}>Flatten</Button>
                </React.Fragment>}
            </DialogActions>
        </Dialog>
    )
}

interface ArgGroup {
    name: string,
    args: CMDArg[],
}

const PropArgTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 10,
    fontWeight: 400,
}))

const PropRequiredTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: '#dba339',
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 10,
    fontWeight: 400,
}))

const ArgGroupTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 18,
    fontWeight: 200,
}))

const PropArgOptionTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 700,
}))

const PropArgShortSummeryTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 14,
    fontStyle: "italic",
    fontWeight: 400,
}))

function ArgumentPropsReviewer(props: {
    title: string,
    args: CMDArg[],
    onFlatten?: () => void,
    // onUnflatten?: () => void,
    depth: number,
    onSelectSubArg: (subArgVar: string) => void,
}) {
    const groupArgs: { [name: string]: CMDArg[] } = {};
    props.args.forEach((arg) => {
        const groupName: string = arg.group.length > 0 ? arg.group : "";
        if (!(groupName in groupArgs)) {
            groupArgs[groupName] = []
        }
        groupArgs[groupName].push(arg)
    })
    const groups: ArgGroup[] = []

    for (const groupName in groupArgs) {
        groupArgs[groupName].sort((a, b) => {
            if (a.required && !b.required) {
                return -1
            } else if (!a.required && b.required) {
                return 1
            }
            return a.options[0].localeCompare(b.options[0])
        });
        groups.push({
            name: groupName,
            args: groupArgs[groupName],
        })
    }
    groups.sort((a, b) => a.name.localeCompare(b.name));

    const buildArg = (arg: CMDArg, idx: number) => {
        const argOptionsString = spliceArgOptionsString(arg, props.depth);
        return (<Box key={`group-arg-${idx}`}
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                justifyContent: "flex-start",
                mb: 2
            }}>
            <Box sx={{
                display: "flex",
                flexDirection: "row",
                alignItems: "flex-end",
                justifyContent: "flex-start",
            }}>
                <ButtonBase onClick={() => {
                    props.onSelectSubArg(arg.var)
                }}>
                    <PropArgOptionTypography sx={{ flexShrink: 0 }}>{argOptionsString}</PropArgOptionTypography>

                </ButtonBase>
                <Box sx={{ flexGrow: 1 }} />
                {arg.stage === "Preview" && <SmallPreviewTypography
                    sx={{ flexShrink: 0 }}
                >
                    {arg.stage}
                </SmallPreviewTypography>}
                {arg.stage === "Experimental" && <SmallExperimentalTypography
                    sx={{ flexShrink: 0 }}
                >
                    {arg.stage}
                </SmallExperimentalTypography>}
            </Box>
            <Box sx={{
                display: "flex",
                flexDirection: "row",
                alignItems: "flex-start",
                justifyContent: "flex-start"
            }}>
                <Box sx={{
                    width: 300,
                    flexShrink: 0,
                    flexDirection: "row",
                    display: "flex",
                    alignItems: "center",
                }}>
                    <PropArgTypeTypography sx={{
                        flexShrink: 0,
                    }}>{`/${arg.type}/`}</PropArgTypeTypography>
                    <Box sx={{ flexGrow: 1 }} />
                    {arg.required && <PropRequiredTypography>[Required]</PropRequiredTypography>}
                </Box>
                {arg.help && <Box sx={{
                    ml: 4
                }}>
                    <PropArgShortSummeryTypography>{arg.help.short}</PropArgShortSummeryTypography>
                </Box>}
            </Box>

        </Box>)
    }

    const buildArgGroup = (group: ArgGroup, idx: number) => {
        return (
            <Box
                key={`group-${idx}`}
                sx={{
                    flexGrow: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "stretch",
                    justifyContent: "flex-start",
                    ml: 2, mr: 2, mb: 1
                }}
            >
                <Box sx={{ flexShrink: 0, ml: 2, p: 1 }} >
                    <ArgGroupTypography id={`argGroup-${idx}-header`}>
                        {group.name.length > 0 ? `${group.name} Group` : "Default Group"}
                    </ArgGroupTypography>
                </Box>
                <Box sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'stretch',
                    justifyContent: 'flex-start',
                    ml: 3,
                    mr: 3,
                }}>
                    {group.args.map(buildArg)}
                </Box>
            </Box>)
    }

    return (<React.Fragment>
        <Box sx={{
            p: 2,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
        }}>
            <SubtitleTypography>{props.title}</SubtitleTypography>
            {props.onFlatten !== undefined && <Button sx={{ flexShrink: 0, ml: 3 }}
                    startIcon={<CallSplitSharpIcon color="info" fontSize='small' />}
                    onClick={props.onFlatten}
                >
                    <ArgEditTypography>Flatten</ArgEditTypography>
            </Button>}

            {/* {props.onUnflatten !== undefined && <Button sx={{ flexShrink: 0, ml: 3 }}
                    startIcon={<CallMergeSharpIcon color="info" fontSize='small' />}
                    onClick={props.onUnflatten}
                >
                    <ArgEditTypography>Unflatten</ArgEditTypography>
            </Button>} */}
        </Box>
        {groups.map(buildArgGroup)}
    </React.Fragment>)
}

type CMDArgHelp = {
    short: string
    lines?: string[]
    refCommands?: string[]
}

type CMDArgDefault<T> = {
    value: T | null
}

type CMDArgBlank<T> = {
    value: T | null
}

type CMDArgEnumItem<T> = {
    name: string
    hide: boolean
    value: T
}

type CMDArgEnum<T> = {
    items: CMDArgEnumItem<T>[]
}

interface CMDArgBase {
    type: string
}

interface CMDArg extends CMDArgBase {
    var: string
    options: string[]

    required: boolean
    stage: "Stable" | "Preview" | "Experimental"
    hide: boolean
    group: string
    help?: CMDArgHelp

    default?: CMDArgDefault<any>
    blank?: CMDArgBlank<any>
    idPart?: string
}

interface CMDArgT<T> extends CMDArg {
    default?: CMDArgDefault<T>
    blank?: CMDArgBlank<T>
}

// type: starts with "@"
interface CMDClsArgBase extends CMDArgBase {
    clsName: string
}

interface CMDClsArg extends CMDClsArgBase, CMDArg {
    singularOptions?: string[]  // for list use only
}

// type: string
interface CMDStringArgBase extends CMDArgBase {
    enum?: CMDArgEnum<string>
    // fmt?: CMDStringFormat
}

interface CMDStringArg extends CMDStringArgBase, CMDArgT<string> { }

// type: byte
interface CMDByteArgBase extends CMDStringArgBase { }
interface CMDByteArg extends CMDByteArgBase, CMDStringArg { }

// type: binary
interface CMDBinaryArgBase extends CMDStringArgBase { }
interface CMDBinaryArg extends CMDBinaryArgBase, CMDStringArg { }

// type: duration
interface CMDDurationArgBase extends CMDStringArgBase { }
interface CMDDurationArg extends CMDDurationArgBase, CMDStringArg { }

// type: date  As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
interface CMDDateArgBase extends CMDStringArgBase { }
interface CMDDateArg extends CMDDateArgBase, CMDStringArg { }

// type: dateTime  As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
interface CMDDateTimeArgBase extends CMDStringArgBase { }
interface CMDDateTimeArg extends CMDDateTimeArgBase, CMDStringArg { }

// type: uuid 
interface CMDUuidArgBase extends CMDStringArgBase { }
interface CMDUuidArg extends CMDUuidArgBase, CMDStringArg { }

// type: password 
interface CMDPasswordArgBase extends CMDStringArgBase { }
interface CMDPasswordArg extends CMDPasswordArgBase, CMDStringArg { }

// type: SubscriptionId
interface CMDSubscriptionIdArgBase extends CMDStringArgBase { }
interface CMDSubscriptionIdArg extends CMDSubscriptionIdArgBase, CMDStringArg { }

// type: ResourceGroupName 
interface CMDResourceGroupNameArgBase extends CMDStringArgBase { }
interface CMDResourceGroupNameArg extends CMDResourceGroupNameArgBase, CMDStringArg { }

// type: ResourceId 
interface CMDResourceIdNameArgBase extends CMDStringArgBase { }
interface CMDResourceIdNameArg extends CMDResourceIdNameArgBase, CMDStringArg { }

// type: ResourceLocation
interface CMDResourceLocationNameArgBase extends CMDStringArgBase { }
interface CMDResourceLocationNameArg extends CMDResourceLocationNameArgBase, CMDStringArg { }


interface CMDNumberArgBase extends CMDArgBase {
    enum?: CMDArgEnum<number>
    // fmt?: CMDIntegerFormat
}
interface CMDNumberArg extends CMDNumberArgBase, CMDArgT<number> { }

// type: integer
interface CMDIntegerArgBase extends CMDNumberArgBase { }
interface CMDIntegerArg extends CMDIntegerArgBase, CMDNumberArg { }

// type: integer32
interface CMDInteger32ArgBase extends CMDNumberArgBase { }
interface CMDInteger32Arg extends CMDInteger32ArgBase, CMDNumberArg { }

// type: integer32
interface CMDInteger64ArgBase extends CMDNumberArgBase { }
interface CMDInteger64Arg extends CMDInteger64ArgBase, CMDNumberArg { }

// type: float
interface CMDFloatArgBase extends CMDNumberArgBase { }
interface CMDFloatArg extends CMDFloatArgBase, CMDNumberArg { }

// type: float32
interface CMDFloat32ArgBase extends CMDNumberArgBase { }
interface CMDFloat32Arg extends CMDFloat32ArgBase, CMDNumberArg { }

// type: float64
interface CMDFloat64ArgBase extends CMDNumberArgBase { }
interface CMDFloat64Arg extends CMDFloat64ArgBase, CMDNumberArg { }

// type: boolean
interface CMDBooleanArgBase extends CMDArgBase { }
interface CMDBooleanArg extends CMDBooleanArgBase, CMDArgT<boolean> { }

// type: object
interface CMDObjectArgBase extends CMDArgBase {
    // fmt?: CMDObjectFormat
    args: CMDArg[]
}

interface CMDObjectArg extends CMDObjectArgBase, CMDArg { }
// type: dict
interface CMDDictArgBase extends CMDArgBase {
    // fmt?: CMDDictFormat
    item: CMDArgBase
}
interface CMDDictArg extends CMDDictArgBase, CMDArg { }

// type: array
interface CMDArrayArgBase extends CMDArgBase {
    // fmt?: CMDArrayFormat
    item: CMDArgBase
}

interface CMDArrayArg extends CMDArrayArgBase, CMDArg {
    singularOptions?: string[]
}

type ClsArgDefinitionMap = {
    [clsName: string]: CMDArgBase
}

function decodeArgEnumItem<T>(response: any): CMDArgEnumItem<T> {
    return {
        name: response.name,
        hide: response.hide ?? false,
        value: response.value as T,
    }
}

function decodeArgEnum<T>(response: any): CMDArgEnum<T> {
    let argEnum: CMDArgEnum<T> = {
        items: response.items.map((item: any) => decodeArgEnumItem<T>(item))
    }
    return argEnum;
}

function decodeArgBase(response: any): { argBase: CMDArgBase, clsDefineMap: ClsArgDefinitionMap } {
    let argBase: any = {
        type: response.type
    }

    let clsDefineMap: ClsArgDefinitionMap = {};

    switch (response.type) {
        case "byte":
        case "binary":
        case "duration":
        case "date":
        case "dateTime":
        case "uuid":
        case "password":
        case "SubscriptionId":
        case "ResourceGroupName":
        case "ResourceId":
        case "ResourceLocation":
        case "string":
            if (response.enum) {
                argBase = {
                    ...argBase,
                    enum: decodeArgEnum<string>(response.enum),
                }
            }
            break
        case "integer32":
        case "integer64":
        case "integer":
            if (response.enum) {
                argBase = {
                    ...argBase,
                    enum: decodeArgEnum<number>(response.enum),
                }
            }
            break
        case "float32":
        case "float64":
        case "float":
            if (response.enum) {
                argBase = {
                    ...argBase,
                    enum: decodeArgEnum<number>(response.enum),
                }
            }
            break
        case "boolean":
            break
        case "object":
            if (response.args && Array.isArray(response.args) && response.args.length > 0) {
                const args: CMDArg[] = response.args.map((resSubArg: any) => {
                    const subArgParse = decodeArg(resSubArg);
                    clsDefineMap = {
                        ...clsDefineMap,
                        ...subArgParse.clsDefineMap,
                    }
                    return subArgParse.arg
                })
                argBase = {
                    ...argBase,
                    args: args,
                }
            } else if (response.additionalProps && response.additionalProps.item) {
                // Convert additionalProps to dict argBaseType
                // TODO: split it on service side
                const itemArgBaseParse = decodeArgBase(response.additionalProps.item);
                clsDefineMap = {
                    ...clsDefineMap,
                    ...itemArgBaseParse.clsDefineMap,
                }
                const argBaseType = `dict<string, ${itemArgBaseParse.argBase.type}>`
                argBase = {
                    ...argBase,
                    type: argBaseType,
                    item: itemArgBaseParse.argBase
                }
            } else {
                throw Error("Invalid object arguments, neither args nor additionalProps exist")
            }

            if (response.cls) {
                const clsName = response.cls;
                clsDefineMap[clsName] = argBase;
                argBase = {
                    type: `@${response.cls}`,
                    clsName: clsName
                }
            }
            break
        default:
            if (response.type.startsWith("array<")) {
                if (response.item) {
                    const itemArgBaseParse = decodeArgBase(response.item);
                    clsDefineMap = {
                        ...clsDefineMap,
                        ...itemArgBaseParse.clsDefineMap,
                    }
                    argBase = {
                        ...argBase,
                        item: itemArgBaseParse.argBase,
                    }
                } else {
                    throw Error("Invalid array object. Item is not defined");
                }

                if (response.cls) {
                    const clsName = response.cls;
                    clsDefineMap[clsName] = argBase;
                    argBase = {
                        type: `@${response.cls}`,
                        clsName: clsName
                    }
                }
            } else if (response.type.startsWith("@")) {
                argBase["clsName"] = response.type.slice(1);
            } else {
                console.error(`Unknown type '${response.type}'`)
                throw Error(`Unknown type '${response.type}'`)
            }
    }

    return {
        argBase: argBase,
        clsDefineMap: clsDefineMap,
    };
}

function decodeArgHelp(response: any): CMDArgHelp {
    return {
        short: response.short,
        lines: response.lines,
        refCommands: response.refCommands,
    }
}

function decodeArg(response: any): { arg: CMDArg, clsDefineMap: ClsArgDefinitionMap } {
    let { argBase, clsDefineMap } = decodeArgBase(response);
    const options = (response.options as string[]).sort((a, b) => a.length - b.length).reverse();
    const help = response.help ? decodeArgHelp(response.help) : undefined;
    let arg: any = {
        ...argBase,
        var: response.var as string,
        options: options,
        required: (response.required ?? false) as boolean,
        stage: (response.stage ?? "Stable") as ("Stable" | "Preview" | "Experimental"),
        hide: (response.hide ?? false) as boolean,
        group: (response.group ?? "") as string,
        help: help,
        default: response.default,
        blank: response.blank,
        idPart: response.idPart,
    }

    switch (argBase.type) {
        case "byte":
        case "binary":
        case "duration":
        case "date":
        case "dateTime":
        case "uuid":
        case "password":
        case "SubscriptionId":
        case "ResourceGroupName":
        case "ResourceId":
        case "ResourceLocation":
        case "string":
            break
        case "integer32":
        case "integer64":
        case "integer":
            break
        case "float32":
        case "float64":
        case "float":
            break
        case "boolean":
            break
        case "object":
            break
        default:
            if (argBase.type.startsWith("dict<")) {
                // dict type
            } else if (argBase.type.startsWith("array<")) {
                // array type
                if (response.singularOptions) {
                    arg = {
                        ...arg,
                        singularOptions: response.singularOptions as string[],
                    }
                }
            } else if (argBase.type.startsWith("@")) {
                if (response.singularOptions) {
                    arg = {
                        ...arg,
                        singularOptions: response.singularOptions as string[],
                    }
                }
            } else {
                console.error(`Unknown type '${argBase.type}'`)
                throw Error(`Unknown type '${argBase.type}'`)
            }
    }

    return {
        arg: arg,
        clsDefineMap: clsDefineMap,
    }
}

function decodeResponse(responseCommand: any): { args: CMDArg[], clsDefineMap: ClsArgDefinitionMap } {
    let clsDefineMap: ClsArgDefinitionMap = {};
    const args: CMDArg[] = [];
    responseCommand.argGroups.forEach((argGroup: any) => {
        args.push(...argGroup.args.map((resArg: any) => {
            const argDecode = decodeArg(resArg);
            clsDefineMap = {
                ...clsDefineMap,
                ...argDecode.clsDefineMap
            }
            return argDecode.arg;
        }))
    })
    return {
        args: args,
        clsDefineMap: clsDefineMap,
    }
}

export default WSEditorCommandArgumentsContent;
