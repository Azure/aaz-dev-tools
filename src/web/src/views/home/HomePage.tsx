import * as React from 'react';
import { Typography, Box, Link, Stepper, Step, StepButton, StepLabel, StepContent, TypographyProps } from '@mui/material';
import { styled } from '@mui/material/styles';

import withRoot from '../../withRoot';
import { AppAppBar } from '../../components/AppAppBar';
import PageLayout from '../../components/PageLayout';


const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '6vh'
}));


const StepperHeaderTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 24,
    fontWeight: 600,
}))

const StepContentTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 14,
    fontWeight: 400,
}))


function HomePage() {
    const [activeStep, setActiveStep] = React.useState(0);

    const handleStep = (step: number) => () => {
        setActiveStep(step);
    }


    return (
        <React.Fragment>
            <AppAppBar pageName={'HomePage'} />
            <PageLayout>
                <Box sx={{
                    display: 'flex',
                    alignItems: 'center',
                    flexDirection: 'column',
                    justifyContent: 'center',
                }}>
                    <Box sx={{ flexGrow: 3 }} />
                    <Box sx={{
                        flexGrow: 3,
                        flexShrink: 0,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexDirection: 'column'
                    }}>
                        <Typography variant='h2' gutterBottom>
                            Welcome to
                        </Typography>
                        <Typography variant='h2' gutterBottom>
                            AAZ Development Tool
                        </Typography>
                        <MiddlePadding />

                        <Box sx={{
                            display: "flex",
                            flexDirection: "row",
                            alignItems: "flex-start",
                            justifyContent: "center"
                        }}>
                            <Box sx={{
                                width: 350,
                                display: "flex",
                                flexDirection: "row-reverse",
                                mr: 3
                            }}>

                                <StepperHeaderTypography gutterBottom>
                                    Getting Started
                                </StepperHeaderTypography>
                            </Box>

                            <Box sx={{ width: 450, ml: 3 }}>
                                <Stepper nonLinear activeStep={activeStep} orientation="vertical">
                                    <Step>
                                        <StepButton color="inherit" onClick={handleStep(0)}>
                                            {"Introduce"}
                                        </StepButton>
                                        <StepContent>
                                            <StepContentTypography>
                                                {"AAZDev is a tool that helps Azure CLI developers generate Atomic CLI commands from REST API Specifications."}
                                            </StepContentTypography>
                                            <StepContentTypography>
                                                {"Go to "}
                                                <Link
                                                    href="/?#/Documents"
                                                    // align="center"
                                                    underline="always"
                                                    target="_blank"
                                                >Introduction</Link>
                                                {" for more details."}
                                            </StepContentTypography>
                                        </StepContent>
                                    </Step>
                                    <Step>
                                        <StepButton color="inherit" onClick={handleStep(1)}>
                                            {"Prepare Swagger"}
                                        </StepButton>
                                        <StepContent>
                                            <StepContentTypography>
                                                {"The definition of API in swagger is required before using AAZDev tool."}
                                            </StepContentTypography>
                                            <StepContentTypography>
                                                {"Please make sure the API specs has been defined in "}
                                            </StepContentTypography>
                                            <StepContentTypography>
                                                <Link
                                                    href="https://github.com/Azure/azure-rest-api-specs"
                                                    // align="center"
                                                    underline="always"
                                                    target="_blank"
                                                >azure-rest-api-specs</Link>
                                                {" repo or "}
                                                <Link
                                                    href="https://github.com/Azure/azure-rest-api-specs-pr"
                                                    // align="center"
                                                    underline="always"
                                                    target="_blank"
                                                >azure-rest-api-specs-pr</Link>
                                                {" repo."}
                                            </StepContentTypography>
                                        </StepContent>
                                    </Step>
                                    <Step>
                                        <StepButton color="inherit" onClick={handleStep(2)}>
                                            {"Build Command Models"}
                                        </StepButton>
                                        <StepContent>
                                            <StepContentTypography>
                                                {"Model editors can help you build command models."}
                                            </StepContentTypography>
                                            <StepContentTypography>
                                                {"To build command models from swagger,"}
                                            </StepContentTypography>
                                            <StepContentTypography>
                                                {"please use "}
                                                <Link
                                                    href="/?#/Workspace"
                                                    align="center"
                                                    underline="always"
                                                >Workspace</Link>
                                                {" editor."}
                                            </StepContentTypography>
                                        </StepContent>
                                    </Step>
                                    <Step>
                                        <StepButton color="inherit" onClick={handleStep(3)}>
                                            {"Generate CLI Code"}
                                        </StepButton>
                                        <StepContent>
                                            <StepContentTypography>
                                                {"To convert command models to CLI code,"}
                                            </StepContentTypography>
                                            <StepContentTypography>
                                                {"please use "}
                                                <Link
                                                    href="/?#/Generation"
                                                    align="center"
                                                    underline="always"
                                                >CLI</Link>
                                                {" generators."}
                                            </StepContentTypography>
                                        </StepContent>
                                    </Step>
                                </Stepper>
                            </Box>
                        </Box>
                    </Box>
                    <Box sx={{ flexGrow: 5 }} />
                </Box>
            </PageLayout>
        </React.Fragment>
    )
}

export default withRoot(HomePage);
