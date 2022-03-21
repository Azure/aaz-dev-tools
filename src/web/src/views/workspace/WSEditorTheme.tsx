import { Typography, TypographyProps } from '@mui/material';
import { styled } from '@mui/system';

const CardTitleTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 18,
    fontWeight: 400,
}))

const NameTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 32,
    fontWeight: 700,
}))

const ShortHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 18,
    fontWeight: 400,
    fontStyle: "italic"
}))

const ShortHelpPlaceHolderTypography = styled(ShortHelpTypography)<TypographyProps>(({ theme }) => ({
    color: '#5d64cf',
}))

const LongHelpTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 16,
    fontWeight: 400,
}))

const StableTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: '#67b349',
    fontFamily: "'Work Sans', sans-serif",
    fontSize: 20,
    fontWeight: 200,
}))

const PreviewTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    color: '#d1b102',
}))

const ExperimentalTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    color: '#e05376',
}))

const SmallStableTypography = styled(StableTypography)<TypographyProps>(({ theme }) => ({
    fontSize: 12,
}))

const SmallPreviewTypography = styled(PreviewTypography)<TypographyProps>(({ theme }) => ({
    fontSize: 12,
}))

const SmallExperimentalTypography = styled(ExperimentalTypography)<TypographyProps>(({ theme }) => ({
    fontSize: 12,
}))

const SubtitleTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 700,
}))

export {CardTitleTypography, NameTypography,
     ShortHelpTypography, ShortHelpPlaceHolderTypography,
      LongHelpTypography, StableTypography,
       PreviewTypography, ExperimentalTypography,
        SubtitleTypography, SmallStableTypography, SmallPreviewTypography, SmallExperimentalTypography};
