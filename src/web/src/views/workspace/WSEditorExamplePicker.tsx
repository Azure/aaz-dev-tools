import React from 'react';
import { Box, Autocomplete, TextField } from '@mui/material';

interface ExampleItemsSelectorProps {
    commonPrefix: string,
    options: string[],
    name: string,
    value: string | null,
    onValueUpdate: (value: string | null) => void
}


class ExampleItemSelector extends React.Component<ExampleItemsSelectorProps> {

    constructor(props: ExampleItemsSelectorProps) {
        super(props);
        this.state = {
            value: this.props.options.length === 1 ? this.props.options[0] : null,
        }
    }

    render() {
        const { name, options, commonPrefix, value } = this.props;
        return (
            <Autocomplete
                id={name}
                value={value}
                options={options}
                onInputChange={(event, newValue: any) => {
                    this.props.onValueUpdate(newValue);
                }}
                getOptionLabel={(option) => {
                    return option.replace(commonPrefix, '');
                }}
                renderOption={(props, option) => {
                    return (
                        <Box component='li'
                            {...props}
                        >
                            {option.replace(commonPrefix, '')}
                        </Box>
                    )
                }}
                selectOnFocus
                // clearOnBlur
                freeSolo
                renderInput={(params) => (
                    <TextField
                        {...params}
                        size='small'
                        // variant='filled'
                        label={name}
                        required
                    />
                )}
            />
        )
    }
}

export { ExampleItemSelector };
