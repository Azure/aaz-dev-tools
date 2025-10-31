import React from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
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
    alignItems: "center",
    gap: theme.spacing(2),
  }),
);

/**
 * A reusable banner component that displays loading state for async operations.
 * Shows a rectangular banner of the specified colour with spinner and loading message when operation is loading.
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
  backgroundColor = "grey.200",
  textColor = "text.primary",
  spinnerColor = "primary",
  spinnerSize = 20,
}) => {
  if (!operation.loading) {
    return null;
  }

  return (
    <LoadingBanner backgroundColor={backgroundColor} textColor={textColor}>
      <CircularProgress size={spinnerSize} color={spinnerColor} />
      <Typography variant="body2">{operation.loadingMessage}</Typography>
    </LoadingBanner>
  );
};

export default AsyncOperationBanner;
