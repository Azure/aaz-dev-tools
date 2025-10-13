import { Box, Autocomplete, createFilterOptions, TextField } from "@mui/material";
import * as React from "react";
import { workspaceApi, type Workspace as WorkspaceType } from "../../services";
import WorkspaceCreateDialog from "./WorkspaceCreateDialog";

interface WorkspaceSelectorProps {
  name: string;
}

interface WorkspaceSelectorState {
  options: any[];
  value: WorkspaceType | null;
  openDialog: boolean;
  newWorkspaceName: string;
}

interface InputType {
  inputValue: string;
  title: string;
}

const filter = createFilterOptions<WorkspaceType | InputType>();

class WorkspaceSelector extends React.Component<WorkspaceSelectorProps, WorkspaceSelectorState> {
  constructor(props: WorkspaceSelectorProps) {
    super(props);
    this.state = {
      options: [],
      value: null,
      openDialog: false,
      newWorkspaceName: "",
    };
  }

  componentDidMount() {
    this.loadWorkspaces();
  }

  loadWorkspaces = async () => {
    try {
      const options = await workspaceApi.getWorkspaces();
      this.setState({
        options: options,
      });
    } catch (err: any) {
      console.error(err);
    }
  };

  handleDialogClose = (value: any | null) => {
    this.setState({
      newWorkspaceName: "",
      openDialog: false,
    });
    if (value != null) {
      this.onValueUpdated(value);
    }
  };

  onValueUpdated = (value: any) => {
    this.setState({
      value: value,
    });
    if (value.url) {
      window.location.href = `/?#/workspace/${value.name}`;
    }
  };

  render() {
    const { options, value, openDialog, newWorkspaceName } = this.state;
    const { name } = this.props;
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
              // timeout to avoid instant validation of the dialog's form.
              setTimeout(() => {
                this.setState({
                  openDialog: true,
                  newWorkspaceName: newValue,
                });
              });
            } else if (newValue && newValue.inputValue) {
              this.setState({
                openDialog: true,
                newWorkspaceName: newValue.inputValue,
              });
            } else {
              this.onValueUpdated(newValue);
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
                autoComplete: "new-password", // disable autocomplete and autofill
              }}
            />
          )}
        />
        {openDialog && (
          <WorkspaceCreateDialog openDialog={openDialog} onClose={this.handleDialogClose} name={newWorkspaceName} />
        )}
      </React.Fragment>
    );
  }
}

export default WorkspaceSelector;
