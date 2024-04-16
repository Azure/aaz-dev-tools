import { styled, Alert, Box, Button, Checkbox, ButtonBase, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, InputLabel, LinearProgress, Radio, RadioGroup, Switch, TextField, Typography, TypographyProps } from '@mui/material';
import axios from 'axios';
import React, { useState, useEffect } from 'react';
import { CardTitleTypography, ExperimentalTypography, LongHelpTypography, PreviewTypography, ShortHelpPlaceHolderTypography, ShortHelpTypography, SmallExperimentalTypography, SmallPreviewTypography, StableTypography, SubtitleTypography } from './WSEditorTheme';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import EditIcon from '@mui/icons-material/Edit';
import ImportExportIcon from '@mui/icons-material/ImportExport';
import CallSplitSharpIcon from '@mui/icons-material/CallSplitSharp';
import AddIcon from '@mui/icons-material/Add';
import WSECArgumentSimilarPicker, { ArgSimilarTree, BuildArgSimilarTree } from './argument/WSECArgumentSimilarPicker';
import pluralize from 'pluralize';


function WSEditorCommandArgumentsContent(props: {
    commandUrl: string,
    args: CMDArg[],
    clsArgDefineMap: ClsArgDefinitionMap,
    onReloadArgs: () => Promise<void>,
    onAddSubCommand: (argVar: string, subArgOptions: { var: string, options: string }[], argStackNames: string[]) => void,
}) {

    const [displayArgumentDialog, setDisplayArgumentDialog] = useState<boolean>(false);
    const [editArg, setEditArg] = useState<CMDArg | undefined>(undefined);
    const [, setEditArgIdxStack] = useState<ArgIdx[] | undefined>(undefined);
    const [displayFlattenDialog, setDisplayFlattenDialog] = useState<boolean>(false);
    const [displayUnwrapClsDialog, setDisplayUnwrapClsDialog] = useState<boolean>(false);

    const handleArgumentDialogClose = async (updated: boolean) => {
        if (updated) {
            props.onReloadArgs();
        }
        setDisplayArgumentDialog(false);
        setEditArg(undefined);
        setEditArgIdxStack(undefined);
    }

    const handleEditArgument = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
        setEditArg(arg)
        setEditArgIdxStack(argIdxStack)
        setDisplayArgumentDialog(true)
    }

    const handleFlattenDialogClose = async (flattened: boolean) => {
        if (flattened) {
            props.onReloadArgs()
        }
        setDisplayFlattenDialog(false);
        setEditArg(undefined);
        setEditArgIdxStack(undefined);
    }

    const handleArgumentFlatten = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
        setEditArg(arg)
        setEditArgIdxStack(argIdxStack)
        setDisplayFlattenDialog(true)
    }

    const handleUnwrapClsDialogClose = async (unwrapped: boolean) => {
        if (unwrapped) {
            props.onReloadArgs();
        }
        setDisplayUnwrapClsDialog(false);
        setEditArg(undefined);
        setEditArgIdxStack(undefined);
    }

    const handleUnwrapClsArgument = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
        setEditArg(arg)
        setEditArgIdxStack(argIdxStack)
        setDisplayUnwrapClsDialog(true)
    }

    const handleAddSubcommand = (arg: CMDArg, argIdxStack: ArgIdx[]) => {
        const argVar = arg.var;
        const argStackNames = argIdxStack.map(argIdx => {
            let name = argIdx.displayKey;
            while (name.startsWith('-')) {
                name = name.slice(1)
            }
            if (name.endsWith('[]') || name.endsWith('{}')) {
                name = name.slice(0, name.length - 2)
                name = pluralize.singular(name)
            }
            return name
        });
        let a: CMDArgBase | undefined = arg;
        if (a.type.startsWith('@')) {
            const clsName = (a as CMDClsArg).clsName;
            a = props.clsArgDefineMap[clsName];
        }
        if (a.type.startsWith("dict<")) {
            a = (a as CMDDictArgBase).item;
        } else if (a.type.startsWith("array<")) {
            a = (a as CMDArrayArgBase).item;
        }
        let subArgOptions: { var: string, options: string }[] = []
        if (a !== undefined) {
            let subArgs;
            if (a.type.startsWith('@')) {
                const clsName = (a as CMDClsArg).clsName;
                subArgs = (props.clsArgDefineMap[clsName] as CMDObjectArgBase).args
            } else {
                subArgs = (a as CMDObjectArg).args
            }
            subArgOptions = subArgs.map(value => {
                return {
                    var: value.var,
                    options: value.options.join(" "),
                };
            });
        }

        props.onAddSubCommand(argVar, subArgOptions, argStackNames);
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
                <ArgumentNavigation commandUrl={props.commandUrl} args={props.args} clsArgDefineMap={props.clsArgDefineMap} onEdit={handleEditArgument} onFlatten={handleArgumentFlatten} onUnwrap={handleUnwrapClsArgument} onAddSubcommand={handleAddSubcommand} />
            </CardContent>

            {displayArgumentDialog && <ArgumentDialog commandUrl={props.commandUrl} arg={editArg!} clsArgDefineMap={props.clsArgDefineMap} open={displayArgumentDialog} onClose={handleArgumentDialogClose} />}
            {displayFlattenDialog && <FlattenDialog commandUrl={props.commandUrl} arg={editArg!} clsArgDefineMap={props.clsArgDefineMap} open={displayFlattenDialog} onClose={handleFlattenDialogClose} />}
            {displayUnwrapClsDialog && <UnwrapClsDialog commandUrl={props.commandUrl} arg={editArg!} open={displayUnwrapClsDialog} onClose={handleUnwrapClsDialogClose} />}
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
    onEdit: (arg: CMDArg, argIdxStack: ArgIdx[]) => void,
    onFlatten: (arg: CMDArg, argIdxStack: ArgIdx[]) => void,
    onUnwrap: (arg: CMDArg, argIdxStack: ArgIdx[]) => void,
    onAddSubcommand: (arg: CMDArg, argIdxStack: ArgIdx[]) => void,
}) {
    const [argIdxStack, setArgIdxStack] = useState<ArgIdx[]>([]);

    const getArgProps = (selectedArgBase: CMDArgBase): { title: string, props: CMDArg[], flattenArgVar: string | undefined } | undefined => {
        if (selectedArgBase.type.startsWith('@')) {
            const clsArgDefine = props.clsArgDefineMap[(selectedArgBase as CMDClsArgBase).clsName];
            const clsArgProps = getArgProps(clsArgDefine);
            if (clsArgProps !== undefined && clsArgDefine.type === "object") {
                clsArgProps!.flattenArgVar = (selectedArgBase as CMDClsArg).var
            }
            return clsArgProps;
        }
        if (selectedArgBase.type === "object") {
            return {
                title: "Props",
                props: (selectedArgBase as CMDObjectArgBase).args,
                flattenArgVar: (selectedArgBase as CMDObjectArg).var,
            }
        } else if (selectedArgBase.type.startsWith("dict<")) {
            const item = (selectedArgBase as CMDDictArgBase).item
            const itemProps = item ? getArgProps(item) : undefined;
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
                    onEdit={() => { props.onEdit(selectedArg, argIdxStack) }}
                    onUnwrap={() => { props.onUnwrap(selectedArg, argIdxStack) }}
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
                onAddSubcommand={undefined}
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
                selectedArg={selectedArg!}
                onFlatten={canFlatten ? () => {
                    props.onFlatten(selectedArg!, argIdxStack)
                } : undefined}
                onAddSubcommand={() => { props.onAddSubcommand(selectedArg!, argIdxStack) }}
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

const NavBarItemHightLightedTypography = styled(NavBarItemTypography)<TypographyProps>(() => ({
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
    let optionsString = arg.options.map((option) => {
        if (depth === 0) {
            if (option.length === 1) {
                return '-' + option;
            } else {
                return '--' + option;
            }
        } else {
            return '.' + option;
        }
    }).join(" ");

    if ((arg as CMDArrayArg).singularOptions) {
        const singularOptionString = (arg as CMDArrayArg).singularOptions!.map((option) => {
            if (depth === 0) {
                if (option.length === 1) {
                    return '-' + option;
                } else {
                    return '--' + option;
                }
            } else {
                return '.' + option;
            }
        }).join(" ");
        optionsString += ` (${singularOptionString})`;
    } else if ((arg as CMDClsArg).singularOptions) {
        const singularOptionString = (arg as CMDArrayArg).singularOptions!.map((option) => {
            if (depth === 0) {
                if (option.length === 1) {
                    return '-' + option;
                } else {
                    return '--' + option;
                }
            } else {
                return '.' + option;
            }
        }).join(" ");
        optionsString += ` (${singularOptionString})`;
    }

    return optionsString;
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

const ArgRequiredTypography = styled(Typography)<TypographyProps>(() => ({
    color: '#fad105',
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 200,
}))

const ArgEditTypography = styled(Typography)<TypographyProps>(() => ({
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
    onUnwrap: () => void,
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

    const getUnwrapKeywords = () => {
        if (props.arg.type.startsWith("@")) {
            return "Unwrap"
        } else if (props.arg.type.startsWith("array")) {
            if ((props.arg as CMDArrayArg).item?.type.startsWith("@")) {
                return "Unwrap Element"
            }
        } else if (props.arg.type.startsWith("dict")) {
            if ((props.arg as CMDDictArg).item?.type.startsWith("@")) {
                return "Unwrap Element"
            }
        }
        return null;
    }

    const getDefaultValueToString = () => {
        if (props.arg.type === "object" || props.arg.type.startsWith("dict<") || props.arg.type.startsWith("array<") || props.arg.type.startsWith("@")) {
            if (props.arg.default !== undefined && props.arg.default !== null) {
                return JSON.stringify(props.arg.default.value);
            }
        } else {
            if (props.arg.default !== undefined && props.arg.default !== null) {
                return props.arg.default.value.toString();
            }
        }
        return ""
    }

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
                    startIcon={<EditIcon color="secondary" fontSize='small' />}
                    onClick={() => { props.onEdit() }}
                >
                    <ArgEditTypography>Edit</ArgEditTypography>
                </Button>
            </Box>

            <Box sx={{
                display: "flex",
                flexDirection: "row",
                justifyContent: "flex-start",
                alignItems: "stretch",
                ml: 6,
            }}>
                <Box sx={{
                    display: "flex",
                    flexDirection: "row",
                    justifyContent: "flex-start",
                    alignItems: "center"
                }}>
                    <ArgTypeTypography>{`/${props.arg.type}/`}</ArgTypeTypography>
                </Box>
                {getUnwrapKeywords() !== null && <Button sx={{ flexShrink: 0, ml: 1 }}
                    startIcon={<ImportExportIcon color="secondary" fontSize='small' />}
                    onClick={() => { props.onUnwrap() }}
                >
                    <ArgEditTypography>{getUnwrapKeywords()!}</ArgEditTypography>
                </Button>}
                <Box sx={{ flexGrow: 1 }} />
                {props.arg.required && <ArgRequiredTypography>[Required]</ArgRequiredTypography>}
            </Box>
            {(props.arg.default !== undefined || choices.length > 0 || props.arg.configurationKey !== undefined) && <Box
                sx={{
                    ml: 5,
                    mt: 0.5,
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                }}>
                {choices.length > 0 && <ArgChoicesTypography sx={{ ml: 1 }}>
                    {`Choices: ` + choices.join(', ')}
                </ArgChoicesTypography>}
                {props.arg.default !== undefined && <ArgChoicesTypography sx={{ ml: 1 }}>
                    {`Default: ${getDefaultValueToString()}`}
                </ArgChoicesTypography>
                }
                {props.arg.configurationKey !== undefined && <ArgChoicesTypography sx={{ ml: 1 }}>
                    {`ConfigurationKey: ${props.arg.configurationKey}`}
                </ArgChoicesTypography>
                }
            </Box>}
            {props.arg.help?.short && <ShortHelpTypography sx={{ ml: 6, mt: 1.5 }}> {props.arg.help?.short} </ShortHelpTypography>}
            {!(props.arg.help?.short) && <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>Please add argument short summary!</ShortHelpPlaceHolderTypography>}
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
    onClose: (updated: boolean) => Promise<void>,
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
    const [argSimilarTree, setArgSimilarTree] = useState<ArgSimilarTree | undefined>(undefined);
    const [argSimilarTreeExpandedIds, setArgSimilarTreeExpandedIds] = useState<string[]>([]);
    const [argSimilarTreeArgIdsUpdated, setArgSimilarTreeArgIdsUpdated] = useState<string[]>([]);
    const [hasDefault, setHasDefault] = useState<boolean | undefined>(false);
    const [defaultValue, setDefaultValue] = useState<any | undefined>(undefined);
    const [defaultValueInJson, setDefaultValueInJson] = useState<boolean>(false);
    const [hasPrompt, setHasPrompt] = useState<boolean | undefined>(false);
    const [promptMsg, setPromptMsg] = useState<string | undefined>(undefined);
    const [promptConfirm, setPromptConfirm] = useState<boolean | undefined>(undefined);
    const [configurationKey, setConfigurationKey] = useState<string>("");
    const [isClientArg, setIsClientArg] = useState<boolean>(false);

    const handleClose = () => {
        setInvalidText(undefined);
        props.onClose(false);
    }

    const verifyModification = () => {
        setInvalidText(undefined);
        const name = options.trim();
        const sName = singularOptions?.trim() ?? undefined;
        const sHelp = shortHelp.trim();
        const lHelp = longHelp.trim();
        const gName = group.trim();
        const cfgKey = configurationKey.trim();

        const names = name.split(' ').filter(n => n.length > 0);
        const sNames = sName?.split(' ').filter(n => n.length > 0) ?? undefined;

        if (names.length < 1) {
            setInvalidText(`Argument 'Option names' is required.`)
            return undefined
        }

        for (const idx in names) {
            const piece = names[idx];
            if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                setInvalidText(`Invalid 'Option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `)
                return undefined
            }
        }

        if (sNames) {
            for (const idx in sNames) {
                const piece = sNames[idx];
                if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                    setInvalidText(`Invalid 'Singular option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `)
                    return undefined
                }
            }
        }

        if (sHelp.length < 1 && names.find((n) => { return n === "subscription" || n === "resource-group" }) === undefined) {
            setInvalidText(`Field 'Short Summary' is required.`)
            return undefined
        }

        let lines: string[] | null = null;
        if (lHelp.length > 1) {
            lines = lHelp.split('\n').filter(l => l.length > 0);
        }

        let argCfgKey: string | null = null;
        if (cfgKey.length > 0) {
            argCfgKey = cfgKey;
        }

        let argDefault = undefined;
        if (hasDefault === false) {
            if (props.arg.default !== undefined) {
                argDefault = null;
            }
        } else if (hasDefault === true) {
            if (defaultValue === undefined) {
                setInvalidText(`Field 'Default Value' is undefined.`)
                return undefined;
            } else {
                try {
                    let argType = props.arg.type;
                    if (argType.startsWith("@")) {
                        argType = props.clsArgDefineMap[(props.arg as CMDClsArg).clsName].type
                    }
                    argDefault = {
                        value: convertArgDefaultText(defaultValue!, argType),
                    }
                } catch (err: any) {
                    setInvalidText(`Field 'Default Value' is invalid: ${err.message}.`)
                    return undefined;
                }
                if (props.arg.default !== undefined && props.arg.default.value === argDefault.value) {
                    argDefault = undefined;
                }
            }
        }

        let argPrompt = undefined;
        if (hasPrompt === false) {
            if (props.arg.prompt !== undefined) {
                argPrompt = null;
            }
        } else if (hasPrompt === true) {
            if (promptMsg === undefined) {
                setInvalidText(`Field 'Prompt Message' is undefined.`)
                return undefined;
            } else {
                const msg = promptMsg.trim();
                if (msg.length < 1) {
                    setInvalidText(`Field 'Prompt Message' is empty.`)
                    return undefined;
                }
                if (!msg.endsWith(':')) {
                    setInvalidText(`Field 'Prompt Message' must end with a colon.`)
                    return undefined;
                }
                argPrompt = {
                    msg: msg,
                    confirm: promptConfirm,
                }
            }
        }

        return {
            options: names,
            singularOptions: sNames,
            stage: stage,
            group: gName,
            hide: hide,
            help: {
                short: sHelp,
                lines: lines
            },
            default: argDefault,
            prompt: argPrompt,
            configurationKey: argCfgKey,
        }
    }

    const handleModify = async () => {
        const data = verifyModification();
        if (data === undefined) {
            return;
        }

        setUpdating(true);

        const argumentUrl = `${props.commandUrl}/Arguments/${props.arg.var}`

        try {
            await axios.patch(argumentUrl, {
                ...data,
            });
            setUpdating(false);
            await props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(
                    `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                );
            }
            setUpdating(false);
        }
    }

    const handleDisplaySimilar = () => {
        if (verifyModification() === undefined) {
            return;
        }

        setUpdating(true);

        const similarUrl = `${props.commandUrl}/Arguments/${props.arg.var}/FindSimilar`
        axios.post(similarUrl).then(res => {
            setUpdating(false);
            const { tree, expandedIds } = BuildArgSimilarTree(res);
            setArgSimilarTree(tree);
            setArgSimilarTreeExpandedIds(expandedIds);
            setArgSimilarTreeArgIdsUpdated([]);
        }).catch(err => {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(
                    `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                );
            }
            setUpdating(false);
        });
    }

    const handleDisableSimilar = () => {
        setArgSimilarTree(undefined);
        setArgSimilarTreeExpandedIds([]);
    }

    const onSimilarTreeUpdated = (newTree: ArgSimilarTree) => {
        setArgSimilarTree(newTree);
    }

    const onSimilarTreeExpandedIdsUpdated = (expandedIds: string[]) => {
        setArgSimilarTreeExpandedIds(expandedIds);
    }

    const handleModifySimilar = async () => {
        const data = verifyModification();
        if (data === undefined) {
            return;
        }

        setUpdating(true);
        let invalidText = "";
        const updatedIds: string[] = [...argSimilarTreeArgIdsUpdated]
        for (const idx in argSimilarTree!.selectedArgIds) {
            const argId = argSimilarTree!.selectedArgIds[idx];
            if (updatedIds.indexOf(argId) === -1) {
                try {
                    await axios.patch(argId, {
                        ...data
                    })
                    updatedIds.push(argId);
                    setArgSimilarTreeArgIdsUpdated([...updatedIds]);
                } catch (err: any) {
                    console.error(err.response);
                    if (err.response?.data?.message) {
                        const data = err.response!.data!;
                        invalidText += `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    }
                }
            }
        }

        if (invalidText.length > 0) {
            setInvalidText(invalidText);
            setUpdating(false);
        } else {
            setUpdating(false);
            await props.onClose(true);
        }
    }

    useEffect(() => {
        const { arg, clsArgDefineMap } = props;
        setIsClientArg(arg.var.startsWith('$Client.'));

        setOptions(arg.options.join(" "));
        if (arg.type.startsWith("array")) {
            setSingularOptions((arg as CMDArrayArg).singularOptions?.join(" ") ?? "")
        } else if (arg.type.startsWith('@') && clsArgDefineMap[(arg as CMDClsArg).clsName].type.startsWith("array")) {
            setSingularOptions((arg as CMDClsArg).singularOptions?.join(" ") ?? "")
        } else {
            setSingularOptions(undefined);
        }

        if (arg.type === "object" || arg.type.startsWith("dict<") || arg.type.startsWith("array<") || arg.type.startsWith("@")) {
            setHasPrompt(undefined);
        } else {
            setHasPrompt(arg.prompt !== undefined);
            if (arg.prompt !== undefined) {
                setPromptMsg(arg.prompt.msg);
                setPromptConfirm(undefined);
            }
        }
        if (arg.type === "password") {
            setPromptConfirm((arg as CMDPasswordArg).prompt?.confirm ?? false);
        }
        setStage(props.arg.stage);
        setGroup(props.arg.group);
        setHide(props.arg.hide);
        setShortHelp(props.arg.help?.short ?? "");
        setLongHelp(props.arg.help?.lines?.join("\n") ?? "");
        setConfigurationKey(props.arg.configurationKey ?? "");
        setUpdating(false);
        setArgSimilarTree(undefined);
        setArgSimilarTreeExpandedIds([]);

        if (arg.type === "object" || arg.type.startsWith("dict<") || arg.type.startsWith("array<") || arg.type.startsWith("@")) {
            setDefaultValueInJson(true);
            if (props.arg.default !== undefined && props.arg.default !== null) {
                setHasDefault(true);
                setDefaultValue(JSON.stringify(props.arg.default.value));
            } else {
                setHasDefault(false);
                setDefaultValue(undefined);
            }
        } else {
            setDefaultValueInJson(false);
            if (props.arg.default !== undefined && props.arg.default !== null) {
                setHasDefault(true);
                setDefaultValue(props.arg.default.value.toString());
            } else {
                setHasDefault(false);
                setDefaultValue(undefined);
            }
        }
    }, [props.arg]);

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
            sx={{ '& .MuiDialog-paper': { width: '80%' } }}
        >
            {!argSimilarTree && <>
                <DialogTitle>{isClientArg ? "Modify Client Argument" : "Modify Argument"}</DialogTitle>
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
                    {!isClientArg && <><TextField
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

                        {!props.arg.required && <>
                            <InputLabel shrink sx={{ font: "inherit" }}>Hide Argument</InputLabel>
                            <Switch sx={{ ml: 4 }}
                                checked={hide}
                                onChange={() => {
                                    setHide(!hide);
                                }}
                            />
                        </>}
                    </>}
                    {hasDefault !== undefined && <>
                        <InputLabel shrink sx={{ font: "inherit" }}>Default Value</InputLabel>
                        <Box sx={{
                            display: "flex",
                            flexDirection: "row",
                            alignItems: "center",
                            justifyContent: "flex-start",
                            ml: 4,
                        }}>
                            <Switch
                                checked={hasDefault}
                                onChange={() => {
                                    setHasDefault(!hasDefault);
                                    setDefaultValue(undefined);
                                }}
                            />
                            <TextField
                                id="defaultValue"
                                label="default Value"
                                hiddenLabel
                                type="text"
                                hidden={!hasDefault}
                                fullWidth
                                size="small"
                                value={defaultValue !== undefined ? defaultValue : ""}
                                onChange={(event: any) => {
                                    setDefaultValue(event.target.value);
                                }}
                                placeholder={defaultValueInJson ? "Default Value in json format" : "Default Value"}
                                margin="normal"
                                aria-controls=''
                                required
                            />
                        </Box>
                    </>}

                    {hasPrompt !== undefined && <>
                        <InputLabel shrink sx={{ font: "inherit" }}>Prompt Input</InputLabel>
                        <Box sx={{
                            display: "flex",
                            flexDirection: "row",
                            alignItems: "center",
                            justifyContent: "flex-start",
                            ml: 4,
                        }}>
                            <Switch
                                checked={hasPrompt}
                                onChange={() => {
                                    setHasPrompt(!hasPrompt);
                                    setPromptMsg(undefined);
                                }}
                            />
                            <Box sx={{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "stretch",
                                justifyContent: "flex-start",
                                flexGrow: 1,
                            }}>
                                <TextField
                                    id="SetPromptMsg"
                                    label="Prompt Message"
                                    hiddenLabel
                                    type="text"
                                    hidden={!hasPrompt}
                                    fullWidth
                                    size="small"
                                    value={promptMsg !== undefined ? promptMsg : ""}
                                    onChange={(event: any) => {
                                        setPromptMsg(event.target.value);
                                    }}
                                    placeholder="Please input the prompt hint end with a colon."
                                    margin="normal"
                                    aria-controls=''
                                    required
                                />
                                {promptConfirm !== undefined && <>
                                    <FormControlLabel control={
                                        <Checkbox
                                            size='small'
                                            checked={promptConfirm}
                                            onChange={() => {
                                                setPromptConfirm(!promptConfirm);
                                            }}
                                        />
                                    } label="Confirm input" />
                                </>}
                            </Box>
                        </Box>
                    </>}
                    {!isClientArg &&
                        <TextField
                            id="configurationKey"
                            label="Configuration Key"
                            helperText="The key to retrieve the default value from cli Configuration"
                            type='text'
                            fullWidth
                            variant='standard'
                            value={configurationKey}
                            onChange={(event: any) => {
                                setConfigurationKey(event.target.value);
                            }}
                            margin="normal"
                        />}

                    <TextField
                        id="shortSummary"
                        label="Short Summary"
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
                        id="longSummary"
                        label="Long Summary"
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
            </>}

            {argSimilarTree && <>
                <DialogTitle>Modify Similar Arguments</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <WSECArgumentSimilarPicker tree={argSimilarTree} expandedIds={argSimilarTreeExpandedIds} updatedIds={argSimilarTreeArgIdsUpdated} onTreeUpdated={onSimilarTreeUpdated} onToggle={onSimilarTreeExpandedIdsUpdated} />
                </DialogContent>
            </>}
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='secondary' />
                    </Box>
                }
                {!updating && !argSimilarTree && <>
                    <Button onClick={handleClose}>Cancel</Button>
                    {/* cls argument should flatten similar. Customer should unwrap cls argument before to modify it*/}
                    {!props.arg.var.startsWith("@") && <Button onClick={handleModify}>{isClientArg ? "Update Global" : "Update"}</Button>}
                    {/* TODO: support unwrap and update */}
                    {!isClientArg && <Button onClick={handleDisplaySimilar}>Update Similar</Button>}
                </>}
                {!updating && argSimilarTree && <>
                    <Button onClick={handleDisableSimilar}>Back</Button>
                    <Button onClick={handleModifySimilar} disabled={argSimilarTree.selectedArgIds.length === 0}>Update</Button>
                </>}
            </DialogActions>
        </Dialog>
    )
}

function FlattenDialog(props: {
    commandUrl: string,
    arg: CMDArg,
    clsArgDefineMap: ClsArgDefinitionMap,
    open: boolean,
    onClose: (flattened: boolean) => Promise<void>,
}) {
    const [updating, setUpdating] = useState<boolean>(false);
    const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
    const [subArgOptions, setSubArgOptions] = useState<{ var: string, options: string }[]>([]);
    const [argSimilarTree, setArgSimilarTree] = useState<ArgSimilarTree | undefined>(undefined);
    const [argSimilarTreeExpandedIds, setArgSimilarTreeExpandedIds] = useState<string[]>([]);
    const [argSimilarTreeArgIdsUpdated, setArgSimilarTreeArgIdsUpdated] = useState<string[]>([]);

    useEffect(() => {
        const { arg, clsArgDefineMap } = props;
        let subArgs;
        if (arg.type.startsWith('@')) {
            const clsName = (arg as CMDClsArg).clsName;
            subArgs = (clsArgDefineMap[clsName] as CMDObjectArgBase).args
        } else {
            subArgs = (arg as CMDObjectArg).args
        }
        const subArgOptions = subArgs.map(value => {
            return {
                var: value.var,
                options: value.options.join(" "),
            };
        });

        setSubArgOptions(subArgOptions);
        setArgSimilarTree(undefined);
        setArgSimilarTreeExpandedIds([]);
    }, [props.arg]);

    const handleClose = () => {
        setInvalidText(undefined);
        props.onClose(false);
    }

    const verifyFlatten = () => {
        setInvalidText(undefined);
        const argOptions: { [argVar: string]: string[] } = {};
        let invalidText: string | undefined = undefined;

        subArgOptions.forEach((arg, idx) => {
            const names = arg.options.split(' ').filter(n => n.length > 0);
            if (names.length < 1) {
                invalidText = `Prop ${idx + 1} option name is required.`
                return undefined
            }

            for (const idx in names) {
                const piece = names[idx];
                if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
                    invalidText = `Invalid 'Prop ${idx + 1} option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `
                    return undefined
                }
            }
            argOptions[arg.var] = names;
        });
        if (invalidText !== undefined) {
            setInvalidText(invalidText);
            return undefined
        }

        return {
            subArgsOptions: argOptions,
        }
    }

    const handleFlatten = async () => {
        const data = verifyFlatten();
        if (data === undefined) {
            return;
        }

        setUpdating(true);

        const flattenUrl = `${props.commandUrl}/Arguments/${props.arg.var}/Flatten`

        try {
            await axios.post(flattenUrl, {
                ...data
            });
            setUpdating(false);
            await props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(
                    `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                );
            }
            setUpdating(false);
        }
    }

    const handleDisplaySimilar = () => {
        if (verifyFlatten() === undefined) {
            return;
        }

        setUpdating(true);

        const similarUrl = `${props.commandUrl}/Arguments/${props.arg.var}/FindSimilar`
        axios.post(similarUrl).then(res => {
            setUpdating(false);
            const { tree, expandedIds } = BuildArgSimilarTree(res);
            setArgSimilarTree(tree);
            setArgSimilarTreeExpandedIds(expandedIds);
            setArgSimilarTreeArgIdsUpdated([]);
        }).catch(err => {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(
                    `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                );
            }
            setUpdating(false);
        });
    }

    const handleDisableSimilar = () => {
        setArgSimilarTree(undefined);
        setArgSimilarTreeExpandedIds([]);
    }

    const onSimilarTreeUpdated = (newTree: ArgSimilarTree) => {
        setArgSimilarTree(newTree);
    }

    const onSimilarTreeExpandedIdsUpdated = (expandedIds: string[]) => {
        setArgSimilarTreeExpandedIds(expandedIds);
    }

    const handleFlattenSimilar = async () => {
        const data = verifyFlatten();
        if (data === undefined) {
            return;
        }
        setUpdating(true);
        let invalidText = "";
        const updatedIds: string[] = [...argSimilarTreeArgIdsUpdated]
        for (const idx in argSimilarTree!.selectedArgIds) {
            const argId = argSimilarTree!.selectedArgIds[idx];
            if (updatedIds.indexOf(argId) === -1) {
                const flattenUrl = `${argId}/Flatten`
                try {
                    await axios.post(flattenUrl, {
                        ...data
                    })
                    updatedIds.push(argId);
                    setArgSimilarTreeArgIdsUpdated([...updatedIds]);
                } catch (err: any) {
                    console.error(err.response);
                    if (err.response?.data?.message) {
                        const data = err.response!.data!;
                        invalidText += `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    }
                }
            }
        }

        if (invalidText.length > 0) {
            setInvalidText(invalidText);
            setUpdating(false);
        } else {
            setUpdating(false);
            await props.onClose(true);
        }
    }

    const buildSubArgText = (arg: { var: string, options: string }, idx: number) => {
        return (<TextField
            id={`subArg-${arg.var}`}
            key={arg.var}
            label={`Prop ${idx + 1}`}
            helperText={idx === 0 ? "You can input multiple names separated by a space character" : undefined}
            type="text"
            fullWidth
            variant='standard'
            value={arg.options}
            onChange={(event: any) => {
                const options = subArgOptions.map(value => {
                    if (value.var === arg.var) {
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
            {!argSimilarTree && <>
                <DialogTitle>Flatten Props</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    {subArgOptions.map(buildSubArgText)}
                </DialogContent>
            </>}

            {argSimilarTree && <>
                <DialogTitle>Flatten Similar Argument Props</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <WSECArgumentSimilarPicker tree={argSimilarTree} expandedIds={argSimilarTreeExpandedIds} updatedIds={argSimilarTreeArgIdsUpdated} onTreeUpdated={onSimilarTreeUpdated} onToggle={onSimilarTreeExpandedIdsUpdated} />
                </DialogContent>
            </>}
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='secondary' />
                    </Box>
                }
                {!updating && !argSimilarTree && <>
                    <Button onClick={handleClose}>Cancel</Button>
                    {!props.arg.type.startsWith('@') && <Button onClick={handleFlatten}>Flatten</Button>}
                    {props.arg.type.startsWith('@') && <Button onClick={handleFlatten}>Unwrap & Flatten</Button>}
                    <Button onClick={handleDisplaySimilar}>Flatten Similar</Button>
                </>}
                {!updating && argSimilarTree && <>
                    <Button onClick={handleDisableSimilar}>Back</Button>
                    <Button onClick={handleFlattenSimilar} disabled={argSimilarTree.selectedArgIds.length === 0}>Update</Button>
                </>}
            </DialogActions>
        </Dialog>
    )
}

function UnwrapClsDialog(props: {
    commandUrl: string,
    arg: CMDArg,
    open: boolean,
    onClose: (unwrapped: boolean) => Promise<void>,
}) {
    const [updating, setUpdating] = useState<boolean>(false);
    const [invalidText, setInvalidText] = useState<string | undefined>(undefined);

    const handleClose = () => {
        setInvalidText(undefined);
        props.onClose(false);
    }

    const handleUnwrap = async () => {
        setUpdating(true);

        let argVar = props.arg.var;
        if (props.arg.type.startsWith("array")) {
            if ((props.arg as CMDArrayArg).item?.type.startsWith("@")) {
                argVar += "[]";
            }
        } else if (props.arg.type.startsWith("dict")) {
            if ((props.arg as CMDDictArg).item?.type.startsWith("@")) {
                argVar += "{}"
            }
        }

        const flattenUrl = `${props.commandUrl}/Arguments/${argVar}/UnwrapClass`

        try {
            await axios.post(flattenUrl);
            setUpdating(false);
            await props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(
                    `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                );
            }
            setUpdating(false);
        }
    }

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
            sx={{ '& .MuiDialog-paper': { width: '80%' } }}
        >
            <DialogTitle>Unwrap Class Type </DialogTitle>
            <DialogContent dividers={true}>
                {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                <ArgTypeTypography>{props.arg.type}</ArgTypeTypography>
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='secondary' />
                    </Box>
                }
                {!updating && <>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleUnwrap}>Unwrap Class</Button>
                </>}
            </DialogActions>
        </Dialog>
    )

}


const PropArgTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 10,
    fontWeight: 400,
}))

const PropRequiredTypography = styled(Typography)<TypographyProps>(() => ({
    color: '#dba339',
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 10,
    fontWeight: 400,
}))

const PropHiddenTypography = styled(Typography)<TypographyProps>(() => ({
    color: '#8888C3',
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

const PropHiddenArgOptionTypography = styled(Typography)<TypographyProps>(() => ({
    color: '#8888C3',
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 700,
}))

const PropArgShortSummaryTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
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
    onAddSubcommand?: () => void,
    selectedArg?: CMDArg,
    depth: number,
    onSelectSubArg: (subArgVar: string) => void,
}) {
    const groupArgs: { [name: string]: CMDArg[] } = {};
    if (props.args !== undefined) {
        props.args.forEach((arg) => {
            const groupName: string = arg.group.length > 0 ? arg.group : "";
            if (!(groupName in groupArgs)) {
                groupArgs[groupName] = []
            }
            groupArgs[groupName].push(arg)
        })
    }

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

    const checkCanAddSubcommand = () => {
        if (props.selectedArg && props.args.length > 0) {
            return true;
        }
        return false;
    }

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
                    {!arg.hide && <PropArgOptionTypography sx={{ flexShrink: 0 }}>{argOptionsString}</PropArgOptionTypography>}
                    {arg.hide && <PropHiddenArgOptionTypography sx={{ flexShrink: 0 }}>{argOptionsString}</PropHiddenArgOptionTypography>}
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
                    {arg.hide && <PropHiddenTypography>[Hidden]</PropHiddenTypography>}
                </Box>
                {arg.help && <Box sx={{
                    ml: 4
                }}>
                    <PropArgShortSummaryTypography>{arg.help.short}</PropArgShortSummaryTypography>
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

    if (groups.length === 0) {
        return (<></>)
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
                startIcon={<CallSplitSharpIcon color="secondary" fontSize='small' />}
                onClick={props.onFlatten}
            >
                <ArgEditTypography>Flatten</ArgEditTypography>
            </Button>}

            {/* {props.onUnflatten !== undefined && <Button sx={{ flexShrink: 0, ml: 3 }}
                startIcon={<CallMergeSharpIcon color="secondary" fontSize='small' />}
                onClick={props.onUnflatten}
            >
                <ArgEditTypography>Unflatten</ArgEditTypography>
            </Button>} */}

            {props.onAddSubcommand !== undefined && checkCanAddSubcommand() && <Button sx={{ flexShrink: 0, ml: 3 }}
                startIcon={<AddIcon color="secondary" fontSize='small' />}
                onClick={props.onAddSubcommand}
            >
                <ArgEditTypography>Subcommands</ArgEditTypography>
            </Button>}

        </Box>
        {groups.map(buildArgGroup)}
    </React.Fragment>)
}

interface ArgGroup {
    name: string,
    args: CMDArg[],
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

interface CMDArgPromptInput {
    msg: string
}

interface CMDPasswordArgPromptInput extends CMDArgPromptInput {
    confirm: boolean
}

interface CMDArgBase {
    type: string
    nullable: boolean
    blank?: CMDArgBlank<any>
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
    idPart?: string
    prompt?: CMDArgPromptInput
    configurationKey?: string
}

interface CMDArgBaseT<T> extends CMDArgBase {
    blank?: CMDArgBlank<T>
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
interface CMDStringArgBase extends CMDArgBaseT<string> {
    enum?: CMDArgEnum<string>
    // fmt?: CMDStringFormat
}

interface CMDStringArg extends CMDStringArgBase, CMDArgT<string> { }

// // type: byte
// interface CMDByteArgBase extends CMDStringArgBase { }

// // type: binary
// interface CMDBinaryArgBase extends CMDStringArgBase { }

// // type: duration
// interface CMDDurationArgBase extends CMDStringArgBase { }

// // type: date  As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
// interface CMDDateArgBase extends CMDStringArgBase { }

// // type: dateTime  As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
// interface CMDDateTimeArgBase extends CMDStringArgBase { }

// interface CMDTimeArgBase extends CMDStringArgBase { }

// // type: uuid 
// interface CMDUuidArgBase extends CMDStringArgBase { }

// type: password 
interface CMDPasswordArgBase extends CMDStringArgBase { }
interface CMDPasswordArg extends CMDPasswordArgBase, CMDStringArg {
    prompt?: CMDPasswordArgPromptInput
}

// // type: SubscriptionId
// interface CMDSubscriptionIdArgBase extends CMDStringArgBase { }

// // type: ResourceGroupName 
// interface CMDResourceGroupNameArgBase extends CMDStringArgBase { }

// // type: ResourceId 
// interface CMDResourceIdNameArgBase extends CMDStringArgBase { }

// // type: ResourceLocation
// interface CMDResourceLocationNameArgBase extends CMDStringArgBase { }


interface CMDNumberArgBase extends CMDArgBaseT<number> {
    enum?: CMDArgEnum<number>
    // fmt?: CMDIntegerFormat
}
interface CMDNumberArg extends CMDNumberArgBase, CMDArgT<number> { }

// // type: integer
// interface CMDIntegerArgBase extends CMDNumberArgBase { }

// // type: integer32
// interface CMDInteger32ArgBase extends CMDNumberArgBase { }

// // type: integer32
// interface CMDInteger64ArgBase extends CMDNumberArgBase { }

// // type: float
// interface CMDFloatArgBase extends CMDNumberArgBase { }

// // type: float32
// interface CMDFloat32ArgBase extends CMDNumberArgBase { }

// // type: float64
// interface CMDFloat64ArgBase extends CMDNumberArgBase { }

// // type: boolean
// interface CMDBooleanArgBase extends CMDArgBaseT<boolean> { }

// type: object
interface CMDObjectArgBase extends CMDArgBase {
    // fmt?: CMDObjectFormat
    args: CMDArg[]
}

interface CMDObjectArg extends CMDObjectArgBase, CMDArg { }
// type: dict
interface CMDDictArgBase extends CMDArgBase {
    item?: CMDArgBase
    anyType: boolean
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
    const argEnum: CMDArgEnum<T> = {
        items: response.items.map((item: any) => decodeArgEnumItem<T>(item))
    }
    return argEnum;
}

function decodeArgBlank<T>(response: any | undefined): CMDArgBlank<T> | undefined {
    if (response === undefined || response === null) {
        return undefined;
    }

    return {
        value: response.value as (T | null),
    }
}

function decodeArgDefault<T>(response: any | undefined): CMDArgDefault<T> | undefined {
    if (response === undefined || response === null) {
        return undefined;
    }

    return {
        value: response.value as (T | null),
    }
}

function decodeArgPromptInput(response: any): CMDArgPromptInput | undefined {
    if (response === undefined || response === null) {
        return undefined;
    }

    return {
        msg: response.msg as string,
    }
}

function decodePasswordArgPromptInput(response: any): CMDPasswordArgPromptInput | undefined {
    if (response === undefined || response === null) {
        return undefined;
    }

    return {
        msg: response.msg as string,
        confirm: (response.confirm ?? false) as boolean,
    }
}

function decodeArgBase(response: any): { argBase: CMDArgBase, clsDefineMap: ClsArgDefinitionMap } {
    let argBase: any = {
        type: response.type,
        nullable: (response.nullable ?? false) as boolean,
    }

    let clsDefineMap: ClsArgDefinitionMap = {};

    switch (response.type) {
        case "byte":
        case "binary":
        case "duration":
        case "date":
        case "dateTime":
        case "time":
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
            if (response.blank) {
                argBase = {
                    ...argBase,
                    blank: decodeArgBlank<string>(response.blank),
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
            if (response.blank) {
                argBase = {
                    ...argBase,
                    blank: decodeArgBlank<number>(response.blank),
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
            if (response.blank) {
                argBase = {
                    ...argBase,
                    blank: decodeArgBlank<number>(response.blank),
                }
            }
            break
        case "boolean":
            if (response.blank) {
                argBase = {
                    ...argBase,
                    blank: decodeArgBlank<boolean>(response.blank),
                }
            }
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
                const itemArgBaseParse = decodeArgBase(response.additionalProps.item);
                clsDefineMap = {
                    ...clsDefineMap,
                    ...itemArgBaseParse.clsDefineMap,
                }
                const argBaseType = `dict<string, ${itemArgBaseParse.argBase.type}>`
                argBase = {
                    ...argBase,
                    type: argBaseType,
                    item: itemArgBaseParse.argBase,
                    anyType: false
                }
            } else if (response.additionalProps && response.additionalProps.anyType) {
                const argBaseType = `dict<string, Any>`
                argBase = {
                    ...argBase,
                    type: argBaseType,
                    anyType: true
                }
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
                    const argBaseType = `array<${itemArgBaseParse.argBase.type}>`
                    argBase = {
                        ...argBase,
                        type: argBaseType,
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
    const { argBase, clsDefineMap } = decodeArgBase(response);
    const options = (response.options as string[]).sort((a, b) => a.length - b.length).reverse();
    const help = response.help ? decodeArgHelp(response.help) : undefined;
    const prompt = response.prompt ? decodeArgPromptInput(response.prompt) : undefined;

    let arg: any = {
        ...argBase,
        var: response.var as string,
        options: options,
        required: (response.required ?? false) as boolean,
        stage: (response.stage ?? "Stable") as ("Stable" | "Preview" | "Experimental"),
        hide: (response.hide ?? false) as boolean,
        group: (response.group ?? "") as string,
        help: help,
        idPart: response.idPart,
        prompt: prompt,
        configurationKey: response.configurationKey,
    }

    switch (argBase.type) {
        case "byte":
        case "binary":
        case "duration":
        case "date":
        case "dateTime":
        case "time":
        case "uuid":
        case "SubscriptionId":
        case "ResourceGroupName":
        case "ResourceId":
        case "ResourceLocation":
        case "string":
            if (response.default) {
                arg = {
                    ...arg,
                    default: decodeArgDefault<string>(response.default),
                }
            }
            break
        case "password":
            if (response.prompt) {
                arg = {
                    ...arg,
                    prompt: decodePasswordArgPromptInput(response.prompt),
                }
            }
            if (response.default) {
                arg = {
                    ...arg,
                    default: decodeArgDefault<string>(response.default),
                }
            }
            break
        case "integer32":
        case "integer64":
        case "integer":
            if (response.default) {
                arg = {
                    ...arg,
                    default: decodeArgDefault<number>(response.default),
                }
            }
            break
        case "float32":
        case "float64":
        case "float":
            if (response.default) {
                arg = {
                    ...arg,
                    default: decodeArgDefault<number>(response.default),
                }
            }
            break
        case "boolean":
            if (response.default) {
                arg = {
                    ...arg,
                    default: decodeArgDefault<boolean>(response.default),
                }
            }
            break
        case "object":
            if (response.default) {
                arg = {
                    ...arg,
                    default: decodeArgDefault<object>(response.default),
                }
            }
            break
        default:
            if (argBase.type.startsWith("dict<")) {
                // dict type
                if (response.default) {
                    arg = {
                        ...arg,
                        default: decodeArgDefault<object>(response.default),
                    }
                }
            } else if (argBase.type.startsWith("array<")) {
                // array type
                if (response.singularOptions) {
                    arg = {
                        ...arg,
                        singularOptions: response.singularOptions as string[],
                    }
                }
                if (response.default) {
                    arg = {
                        ...arg,
                        default: decodeArgDefault<Array<any>>(response.default),
                    }
                }
            } else if (argBase.type.startsWith("@")) {
                if (response.singularOptions) {
                    arg = {
                        ...arg,
                        singularOptions: response.singularOptions as string[],
                    }
                }
                if (response.default) {
                    arg = {
                        ...arg,
                        default: decodeArgDefault<any>(response.default),
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

function convertArgDefaultText(defaultText: string, argType: string): any {
    switch (argType) {
        case "byte":
        case "binary":
        case "duration":
        case "date":
        case "dateTime":
        case "time":
        case "uuid":
        case "password":
        case "SubscriptionId":
        case "ResourceGroupName":
        case "ResourceId":
        case "ResourceLocation":
        case "string":
            if (defaultText.trim().length === 0) {
                throw Error(`Not supported empty value: '${defaultText}'`);
            }
            return defaultText.trim();
        case "integer32":
        case "integer64":
        case "integer":
            if (Number.isNaN(parseInt(defaultText.trim()))) {
                throw Error(`Not supported default value for integer type: '${defaultText}'`)
            }
            return parseInt(defaultText.trim());
        case "float32":
        case "float64":
        case "float":
            if (Number.isNaN(parseFloat(defaultText.trim()))) {
                throw Error(`Not supported default value for float type: '${defaultText}'`)
            }
            return parseFloat(defaultText.trim());
        case "boolean":
            switch (defaultText.trim().toLowerCase()) {
                case 'true':
                case 'yes':
                    return true;
                case 'false':
                case 'no':
                    return false;
                default:
                    throw Error(`Not supported default value for boolean type: '${defaultText}'`)
            }
        case "object": {
            const de = JSON.parse(defaultText.trim());
            // TODO: verify object
            return de;
        }
        default:
            if (argType.startsWith("array")) {
                const de = JSON.parse(defaultText.trim());
                // TODO: verify array
                return de
            } else if (argType.startsWith("dict")) {
                const de = JSON.parse(defaultText.trim());
                // TODO: verify dict
                return de
            }
            throw Error(`Not supported type: ${argType}`)
    }
}

const DecodeArgs = (argGroups: any[]): { args: CMDArg[], clsArgDefineMap: ClsArgDefinitionMap } => {
    let clsDefineMap: ClsArgDefinitionMap = {};
    const args: CMDArg[] = [];
    argGroups.forEach((argGroup: any) => {
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
        clsArgDefineMap: clsDefineMap,
    }
}

export default WSEditorCommandArgumentsContent;
export { DecodeArgs }
export type { CMDArg, ClsArgDefinitionMap };
