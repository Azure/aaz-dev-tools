import React, { useCallback } from "react";
import { Box, Autocomplete, TextField } from "@mui/material";

interface SwaggerItemsSelectorProps {
  commonPrefix: string;
  options: string[];
  name: string;
  value: string | null;
  onValueUpdate: (value: string | null) => void;
}

const SwaggerItemSelector: React.FC<SwaggerItemsSelectorProps> = ({
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
      onChange={(_event, newValue: any) => {
        onValueUpdate(newValue);
      }}
      getOptionLabel={getOptionLabel}
      renderOption={renderOption}
      selectOnFocus
      clearOnBlur
      renderInput={(params) => (
        <TextField
          {...params}
          size="small"
          // variant='filled'
          label={name}
          required
        />
      )}
    />
  );
};

export default SwaggerItemSelector;
export type { SwaggerItemsSelectorProps };
