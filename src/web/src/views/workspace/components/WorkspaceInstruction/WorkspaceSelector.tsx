import { Box, Autocomplete, createFilterOptions, TextField } from "@mui/material";
import * as React from "react";
import { workspaceApi, type Workspace as WorkspaceType } from "../../../../services";
import { WorkspaceCreateDialog } from ".";

interface WorkspaceSelectorProps {
  name: string;
}

interface InputType {
  inputValue: string;
  title: string;
}

const filter = createFilterOptions<WorkspaceType | InputType>();

const WorkspaceSelector: React.FC<WorkspaceSelectorProps> = ({ name }) => {
  const [options, setOptions] = React.useState<any[]>([]);
  const [value, setValue] = React.useState<WorkspaceType | null>(null);
  const [openDialog, setOpenDialog] = React.useState<boolean>(false);
  const [newWorkspaceName, setNewWorkspaceName] = React.useState<string>("");

  React.useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const workspaces = await workspaceApi.getWorkspaces();
      setOptions(workspaces);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleDialogClose = (value: any | null) => {
    setNewWorkspaceName("");
    setOpenDialog(false);
    if (value != null) {
      onValueUpdated(value);
    }
  };

  const onValueUpdated = (value: any) => {
    setValue(value);
    if (value.url) {
      window.location.href = `/?#/workspace/${value.name}`;
    }
  };

  return (
    <React.Fragment>
      <Autocomplete
        id="workspace-select"
        value={value}
        sx={{ width: 280 }}
        options={options}
        autoHighlight
        onChange={(_event, newValue: any) => {
          if (typeof newValue === "string") {
            setTimeout(() => {
              setOpenDialog(true);
              setNewWorkspaceName(newValue);
            });
          } else if (newValue && newValue.inputValue) {
            setOpenDialog(true);
            setNewWorkspaceName(newValue.inputValue);
          } else {
            onValueUpdated(newValue);
          }
        }}
        filterOptions={(options, params: any) => {
          const filtered = filter(options, params);
          if (params.inputValue !== "" && -1 === options.findIndex((e) => e.name === params.inputValue)) {
            filtered.push({
              inputValue: params.inputValue,
              title: `Create "${params.inputValue}"`,
            });
          }
          return filtered;
        }}
        getOptionLabel={(option) => {
          if (typeof option === "string") {
            return option;
          }
          if (option.title) {
            return option.title;
          }
          return option.name;
        }}
        renderOption={(props, option) => {
          const labelName = option && option.title ? option.title : option.name;
          return (
            <Box component="li" {...props}>
              {labelName}
            </Box>
          );
        }}
        selectOnFocus
        clearOnBlur
        renderInput={(params) => (
          <TextField
            {...params}
            label={name}
            inputProps={{
              ...params.inputProps,
              autoComplete: "new-password",
            }}
          />
        )}
      />
      {openDialog && (
        <WorkspaceCreateDialog openDialog={openDialog} onClose={handleDialogClose} name={newWorkspaceName} />
      )}
    </React.Fragment>
  );
};

export default WorkspaceSelector;
