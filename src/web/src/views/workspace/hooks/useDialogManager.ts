import { useState, useCallback } from "react";

interface DialogStates {
  showSwaggerResourcePicker: boolean;
  showSwaggerReloadDialog: boolean;
  showClientConfigDialog: boolean;
  showExportDialog: boolean;
  showDeleteDialog: boolean;
  showModifyDialog: boolean;
}

interface DialogActions {
  openSwaggerResourcePicker: () => void;
  openSwaggerReloadDialog: () => void;
  openClientConfigDialog: () => void;
  openExportDialog: () => void;
  openDeleteDialog: () => void;
  openModifyDialog: () => void;
  closeSwaggerResourcePicker: () => void;
  closeSwaggerReloadDialog: () => void;
  closeClientConfigDialog: () => void;
  closeExportDialog: () => void;
  closeDeleteDialog: () => void;
  closeModifyDialog: () => void;
}

export function useDialogManager(): DialogStates & DialogActions {
  const [dialogStates, setDialogStates] = useState<DialogStates>({
    showSwaggerResourcePicker: false,
    showSwaggerReloadDialog: false,
    showClientConfigDialog: false,
    showExportDialog: false,
    showDeleteDialog: false,
    showModifyDialog: false,
  });

  const openSwaggerResourcePicker = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showSwaggerResourcePicker: true }));
  }, []);

  const openSwaggerReloadDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showSwaggerReloadDialog: true }));
  }, []);

  const openClientConfigDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showClientConfigDialog: true }));
  }, []);

  const openExportDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showExportDialog: true }));
  }, []);

  const openDeleteDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showDeleteDialog: true }));
  }, []);

  const openModifyDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showModifyDialog: true }));
  }, []);

  const closeSwaggerResourcePicker = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showSwaggerResourcePicker: false }));
  }, []);

  const closeSwaggerReloadDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showSwaggerReloadDialog: false }));
  }, []);

  const closeClientConfigDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showClientConfigDialog: false }));
  }, []);

  const closeExportDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showExportDialog: false }));
  }, []);

  const closeDeleteDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showDeleteDialog: false }));
  }, []);

  const closeModifyDialog = useCallback(() => {
    setDialogStates((prev) => ({ ...prev, showModifyDialog: false }));
  }, []);

  return {
    ...dialogStates,
    openSwaggerResourcePicker,
    openSwaggerReloadDialog,
    openClientConfigDialog,
    openExportDialog,
    openDeleteDialog,
    openModifyDialog,
    closeSwaggerResourcePicker,
    closeSwaggerReloadDialog,
    closeClientConfigDialog,
    closeExportDialog,
    closeDeleteDialog,
    closeModifyDialog,
  };
}
