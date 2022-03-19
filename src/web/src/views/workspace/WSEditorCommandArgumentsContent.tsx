import { Box, CardContent, CircularProgress } from '@mui/material';
import axios from 'axios';
import React, { useState, useEffect } from 'react';


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

interface CMDCls extends CMDClsArgBase, CMDArg {
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

interface CMDObjectArgAdditionalProperties {
    item: CMDArgBase
}
// type: object
interface CMDObjectArgBase extends CMDArgBase {
    // fmt?: CMDObjectFormat
    args?: CMDArg[]
    additionalProps?: CMDObjectArgAdditionalProperties
}

interface CMDObjectArg extends CMDObjectArgBase, CMDArg { }

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
        case "integer32":
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
            }

            if (response.additionalProps && response.additionalProps.item) {
                const itemArgBaseParse = decodeArgBase(response.additionalProps.item);
                clsDefineMap = {
                    ...clsDefineMap,
                    ...itemArgBaseParse.clsDefineMap,
                }
                const additionalProps: CMDObjectArgAdditionalProperties = {
                    item: itemArgBaseParse.argBase,
                }
                argBase = {
                    ...argBase,
                    additionalProps: additionalProps,
                }
            }
            if (!argBase.args && !argBase.additionalProps) {
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
                console.log(`Unknown type '${response.type}'`)
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

    let arg: any = {
        ...argBase,
        required: (response.required ?? false) as boolean,
        stage: (response.stage ?? "Stable") as ("Stable" | "Preview" | "Experimental"),
        hide: (response.hide ?? false) as boolean,
        group: (response.group ?? "") as string,
        default: response.default,
        blank: response.blank,
        idPart: response.idPart,
    }
    if (response.help) {
        arg = {
            ...arg,
            help: decodeArgHelp(response.help),
        }
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
        case "integer32":
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
            if (argBase.type.startsWith("array<")) {
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
                console.log(`Unknown type '${argBase.type}'`)
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
            console.log(argDecode);
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


interface WSEditorCommandArgumentsContentProps {
    commandUrl: string,
}

function WSEditorCommandArgumentsContent(props: WSEditorCommandArgumentsContentProps) {

    const [args, setArgs] = useState<CMDArg[]>([]);
    const [clsArgDefineMap, setClsArgDefineMap] = useState<ClsArgDefinitionMap>({});

    useEffect(() => {
        axios.get(props.commandUrl)
            .then(res => {
                const { args, clsDefineMap } = decodeResponse(res.data);
                console.log(args);
                console.log(clsDefineMap);
                setArgs(args);
                setClsArgDefineMap(clsDefineMap);
            }).catch(err => console.log(err.response));
    }, [props.commandUrl]);

    return (
        <React.Fragment>
            <CardContent sx={{
                flex: '1 0 auto',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'stretch',
            }}>
                <ArgumentReviewer args={args} clsArgDefineMap={clsArgDefineMap} />
            </CardContent>
        </React.Fragment>
    )
}

interface ArgumentReviewerProps {
    args: CMDArg[],
    clsArgDefineMap: ClsArgDefinitionMap,
}

interface ArgumentReviewerState {

}

class ArgumentReviewer extends React.Component<ArgumentReviewerProps, ArgumentReviewerState> {

    constructor(props: ArgumentReviewerProps) {
        super(props);
    }

    render() {
        return (<React.Fragment>


        </React.Fragment>)
    }

}


export default WSEditorCommandArgumentsContent;
