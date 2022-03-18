import { Typography, TypographyProps } from '@mui/material';
import { styled } from '@mui/system';

const NameTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 32,
    fontWeight: 700,
}))

const ShortHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 24,
    fontWeight: 200,
}))

const ShortHelpPlaceHolderTypography = styled(ShortHelpTypography)<TypographyProps>(({ theme }) => ({
    color: '#5d64cf',
}))

const LongHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 18,
    fontWeight: 400,
}))

const StableTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: '#67b349',
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 20,
    fontWeight: 200,
}))

const PreviewTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    color: '#dba339',
}))

const ExperimentalTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    color: '#e05376',
}))

export {NameTypography, ShortHelpTypography, ShortHelpPlaceHolderTypography, LongHelpTypography, StableTypography, PreviewTypography, ExperimentalTypography};
