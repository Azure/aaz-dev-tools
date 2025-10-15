import React, { useCallback } from "react";
import { Box, Autocomplete, TextField } from "@mui/material";

interface ExampleItemsSelectorProps {
  commonPrefix: string;
  options: string[];
  name: string;
  value: string | null;
  onValueUpdate: (value: string | null) => void;
}

const ExampleItemSelector: React.FC<ExampleItemsSelectorProps> = ({
  commonPrefix,
  options,
  name,
  value,
  onValueUpdate,
}) => {
  const getOptionLabel = useCallback(
    (option: string) => {
      return option.replace(commonPrefix, "");
    },
    [commonPrefix],
  );

  const renderOption = useCallback(
    (props: any, option: string) => {
      return (
        <Box component="li" {...props}>
          {option.replace(commonPrefix, "")}
        </Box>
      );
    },
    [commonPrefix],
  );

  return (
    <Autocomplete
      id={name}
      value={value}
      options={options}
      onInputChange={(_event, newValue: any) => {
        onValueUpdate(newValue);
      }}
      getOptionLabel={getOptionLabel}
      renderOption={renderOption}
      selectOnFocus
      freeSolo
      renderInput={(params) => <TextField {...params} size="small" label={name} required />}
    />
  );
};

export { ExampleItemSelector };
