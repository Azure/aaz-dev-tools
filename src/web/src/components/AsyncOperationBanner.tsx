import React from "react";
import { Box, LinearProgress, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import type { UseAsyncOperationResult } from "../services/hooks";

interface AsyncOperationBannerProps {
  operation: UseAsyncOperationResult<any>;
  backgroundColor?: string;
  textColor?: string;
  spinnerColor?: "primary" | "secondary" | "error" | "info" | "success" | "warning" | "inherit";
  spinnerSize?: number;
}

const LoadingBanner = styled(Box)<{ backgroundColor?: string; textColor?: string }>(
  ({ theme, backgroundColor, textColor }) => ({
    padding: theme.spacing(1.5),
    marginBottom: theme.spacing(2),
    backgroundColor: backgroundColor || theme.palette.grey[200],
    color: textColor || theme.palette.text.primary,
    borderRadius: theme.spacing(1),
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(1),
  }),
);

/**
 * A reusable banner component that displays loading state for async operations.
 * Designed to be used with the UseAsyncOperationResult interface.
 *
 * Returns null if !loading
 *
 * @example
 * ```tsx
 * const modulesLoader = useAsyncOperation(specsApi.getModulesForPlane);
 *
 * return (
 *   <AsyncOperationBanner operation={modulesLoader} />
 * );
 * ```
 */
export const AsyncOperationBanner: React.FC<AsyncOperationBannerProps> = ({
  operation,
  backgroundColor = "white",
  textColor,
}) => {
  if (!operation.loading) {
    return null;
  }

  return (
    <LoadingBanner backgroundColor={backgroundColor} textColor={textColor}>
      <Typography variant="body1">{operation.loadingMessage}</Typography>
      <LinearProgress color="secondary" />
    </LoadingBanner>
  );
};

export default AsyncOperationBanner;
