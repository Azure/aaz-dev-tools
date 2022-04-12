import { Accordion, AccordionDetails, AccordionSummaryProps, Box, Button, ButtonBase, CardActions, CardContent, CircularProgress, Typography, TypographyProps } from '@mui/material';
import { styled } from '@mui/system';
import axios from 'axios';
import React, { useState, useEffect } from 'react';
import { CardTitleTypography, ExperimentalTypography, LongHelpTypography, PreviewTypography, ShortHelpPlaceHolderTypography, ShortHelpTypography, SmallExperimentalTypography, SmallPreviewTypography, SmallStableTypography, StableTypography, SubtitleTypography } from './WSEditorTheme';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';


function WSEditorCommandArgumentsContent(props: {
    commandUrl: string,
}) {

    const [args, setArgs] = useState<CMDArg[]>([]);
    const [clsArgDefineMap, setClsArgDefineMap] = useState<ClsArgDefinitionMap>({});

    useEffect(() => {
        axios.get(props.commandUrl)
            .then(res => {
                const { args, clsDefineMap } = decodeResponse(res.data);
                setArgs(args);
                setClsArgDefineMap(clsDefineMap);
            }).catch(err => console.error(err.response));
    }, [props.commandUrl]);

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
                <ArgumentNavigation commandUrl={props.commandUrl} args={args} clsArgDefineMap={clsArgDefineMap} />
            </CardContent>
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
}) {
    const [argIdxStack, setArgIdxStack] = useState<ArgIdx[]>([]);

    const getArgProps = (selectedArgBase: CMDArgBase): { title: string, props: CMDArg[] } | undefined => {
        if (selectedArgBase.type.startsWith('@')) {
            return getArgProps(props.clsArgDefineMap[(selectedArgBase as CMDClsArgBase).clsName]);
        }
        if (selectedArgBase.type === "object") {
            return {
                title: "Props",
                props: (selectedArgBase as CMDObjectArgBase).args,
            }
        } else if (selectedArgBase.type.startsWith("dict<")) {
            const itemProps = getArgProps((selectedArgBase as CMDDictArgBase).item);
            if (!itemProps) {
                return undefined;
            }
            return {
                title: "Dict Element Props",
                props: itemProps.props,
            }
        } else if (selectedArgBase.type.startsWith("array<")) {
            const itemProps = getArgProps((selectedArgBase as CMDArrayArgBase).item);
            if (!itemProps) {
                return undefined;
            }
            return {
                title: "Array Element Props",
                props: itemProps.props,
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

                <ArgumentReviewer arg={selectedArg} depth={argIdxStack.length} />
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
            return (<ArgumentPropsReviewer
                title={argProps.title}
                args={argProps.props}
                depth={argIdxStack.length}
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
                        key={`${props.argIdxStack.length-1}`}
                        onClick={() => {
                            props.onChangeArgIdStack(props.argIdxStack.length)
                        }}
                    >
                        <NavBarItemHightLightedTypography sx={{ flexShrink: 0 }} >{props.argIdxStack.length > 1 ? `.${props.argIdxStack[props.argIdxStack.length-1].displayKey}` : props.argIdxStack[props.argIdxStack.length-1].displayKey}</NavBarItemHightLightedTypography>
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

function ArgumentReviewer(props: {
    arg: CMDArg,
    depth: number,
}) {
    const buildArgOptionsString = () => {
        const argOptionsString = spliceArgOptionsString(props.arg, props.depth - 1);
        return (<ArgNameTypography>{argOptionsString}</ArgNameTypography>)
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
            {buildArgOptionsString()}
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
            {props.arg.help?.short && <ShortHelpTypography sx={{ ml: 6, mt: 1.5 }}> {props.arg.help?.short} </ShortHelpTypography>}
            {!(props.arg.help?.short) && <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>Please add argument short summery!</ShortHelpPlaceHolderTypography>}
            {props.arg.help?.lines && <Box sx={{ ml: 6, mt: 1, mb: 1 }}>
                {props.arg.help.lines.map((line, idx) => (<LongHelpTypography key={idx}>{line}</LongHelpTypography>))}
            </Box>}
        </Box>
    </React.Fragment>)
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
            p: 2
        }}>
            <SubtitleTypography>{props.title}</SubtitleTypography>
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

// type: date-time  As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
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
        case "date-time":
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
        case "date-time":
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
