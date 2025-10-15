import React from "react";
import { Box, ButtonBase, styled, Typography, TypographyProps } from "@mui/material";
import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";

interface ArgIdx {
  var: string;
  displayKey: string;
}

interface ArgNavBarProps {
  argIdxStack: ArgIdx[];
  onChangeArgIdStack: (end: number) => void;
}

const NavBarItemTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const NavBarItemHightLightedTypography = styled(NavBarItemTypography)<TypographyProps>(() => ({
  color: "#5d64cf",
}));

const ArgNavBar: React.FC<ArgNavBarProps> = ({ argIdxStack, onChangeArgIdStack }) => {
  return (
    <React.Fragment>
      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "flex-start",
          mt: 1,
          mb: 0.5,
          mr: 2,
        }}
      >
        <ButtonBase
          key="Back"
          onClick={() => {
            onChangeArgIdStack(0);
          }}
        >
          <ArrowBackIosIcon sx={{ fontSize: 14 }} />
        </ButtonBase>
        {argIdxStack.slice(0, -1).map((argIdx: ArgIdx, index: number) => (
          <ButtonBase
            key={`${index}`}
            onClick={() => {
              onChangeArgIdStack(index + 1);
            }}
          >
            <NavBarItemTypography sx={{ flexShrink: 0 }}>
              {index > 0 ? `.${argIdx.displayKey}` : argIdx.displayKey}
            </NavBarItemTypography>
          </ButtonBase>
        ))}
        <ButtonBase
          key={`${argIdxStack.length - 1}`}
          onClick={() => {
            onChangeArgIdStack(argIdxStack.length);
          }}
        >
          <NavBarItemHightLightedTypography sx={{ flexShrink: 0 }}>
            {argIdxStack.length > 1
              ? `.${argIdxStack[argIdxStack.length - 1].displayKey}`
              : argIdxStack[argIdxStack.length - 1].displayKey}
          </NavBarItemHightLightedTypography>
        </ButtonBase>
      </Box>
    </React.Fragment>
  );
};

export default ArgNavBar;
export type { ArgNavBarProps, ArgIdx };
