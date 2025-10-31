import React from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import type { UseAsyncOperationResult } from "../services/hooks";

interface AsyncOperationBannerProps {
  /**
   * The async operation result from useAsyncOperation hook
   */
  operation: UseAsyncOperationResult<any>;
  /**
   * Optional custom background color (defaults to light blue)
   */
  backgroundColor?: string;
  /**
   * Optional custom text color (defaults to text.primary)
   */
  textColor?: string;
  /**
   * Optional custom spinner color (defaults to primary)
   */
  spinnerColor?: "primary" | "secondary" | "error" | "info" | "success" | "warning" | "inherit";
  /**
   * Optional custom spinner size (defaults to 20)
   */
  spinnerSize?: number;
}

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
  backgroundColor = "lightblue",
  textColor = "text.primary",
  spinnerColor = "primary",
  spinnerSize = 20,
}) => {
  if (!operation.loading) {
    return null;
  }

  return (
    <Box
      sx={{
        p: 1.5,
        mb: 2,
        backgroundColor,
        color: textColor,
        borderRadius: 2,
        display: "flex",
        alignItems: "center",
        gap: 2,
      }}
    >
      <CircularProgress size={spinnerSize} color={spinnerColor} />
      <Typography variant="body2">{operation.loadingMessage}</Typography>
    </Box>
  );
};

export default AsyncOperationBanner;
