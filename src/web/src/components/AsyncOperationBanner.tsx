import React from "react";
import { Box, LinearProgress, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import type { UseAsyncOperationResult } from "../services/hooks";

interface LoadingBannerProps {
  loading: boolean;
  message?: string;
  backgroundColor?: string;
  textColor?: string;
  spinnerColor?: "primary" | "secondary" | "error" | "info" | "success" | "warning" | "inherit";
}

interface AsyncOperationBannerProps {
  operation: UseAsyncOperationResult<any>;
  backgroundColor?: string;
  textColor?: string;
  spinnerColor?: "primary" | "secondary" | "error" | "info" | "success" | "warning" | "inherit";
  spinnerSize?: number;
}

const StyledLoadingBanner = styled(Box)<{ backgroundColor?: string; textColor?: string }>(
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
 * A generic loading banner component that displays a loading state with message and progress bar.
 * Can be used anywhere you need to show a loading state, not just with async operations.
 *
 * Returns null if !loading
 *
 * @example
 * ```tsx
 * const [loading, setLoading] = useState(false);
 *
 * return (
 *   <LoadingBanner loading={loading} message="Loading data..." />
 * );
 * ```
 */
export const LoadingBanner: React.FC<LoadingBannerProps> = ({
  loading,
  message,
  backgroundColor = "white",
  textColor,
  spinnerColor = "secondary",
}) => {
  if (!loading) {
    return null;
  }

  return (
    <StyledLoadingBanner backgroundColor={backgroundColor} textColor={textColor}>
      {message && <Typography variant="body1">{message}</Typography>}
      <LinearProgress color={spinnerColor} />
    </StyledLoadingBanner>
  );
};

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
  spinnerColor = "secondary",
}) => {
  return (
    <LoadingBanner
      loading={operation.loading}
      message={operation.loading ? operation.loadingMessage : undefined}
      backgroundColor={backgroundColor}
      textColor={textColor}
      spinnerColor={spinnerColor}
    />
  );
};

export default AsyncOperationBanner;
