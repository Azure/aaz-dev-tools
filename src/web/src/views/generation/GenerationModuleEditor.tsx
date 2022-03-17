import * as React from 'react';
import {Typography, Box, Link } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useParams } from 'react-router';
import GenerationModuleEditorToolBar from "./GenerationModuleEditorToolBar";

const TopPadding = styled(Box)(({ theme }) => ({
    [theme.breakpoints.up('sm')]: {
        height: '12vh',
    },
}));

const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '6vh'
}));

interface GenerationModuleEditorProps {
    params: {
        repoName: string,
        moduleName: string,
    }
}

interface GenerationModuleEditorState {
    moduleName: string,
}


class GenerationModuleEditor extends React.Component<GenerationModuleEditorProps, GenerationModuleEditorState> {
    
    constructor(props: GenerationModuleEditorProps) {
        super(props);
        this.state = {
            moduleName: this.props.params.moduleName,
        }
    }

    handleBackToHomepage = () => {
        window.location.href = `/?#/workspace`
    }

    handleGenerate = () => {

    }

    render() {
        const { moduleName} = this.state
        return (
            <React.Fragment>
                <GenerationModuleEditorToolBar moduleName={moduleName} onHomePage={this.handleBackToHomepage} onGenerate={this.handleGenerate}>

                </GenerationModuleEditorToolBar>
            </React.Fragment>
        )
    }
}


const GenerationModuleEditorWrapper = (props: any) => {
    const params = useParams()
    return <GenerationModuleEditor params={params} {...props} />
}

export { GenerationModuleEditorWrapper as GenerationModuleEditor };
