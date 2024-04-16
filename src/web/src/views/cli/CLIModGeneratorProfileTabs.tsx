import * as React from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";

interface CLIModGeneratorProfileTabsProps {
    value: number;
    profiles: string[];
    onChange: (newValue: number) => void;
}


class CLIModGeneratorProfileTabs extends React.Component<CLIModGeneratorProfileTabsProps> {
    render() {
        const { value, profiles, onChange } = this.props;
        return (
            <Tabs
                orientation="vertical"
                variant="scrollable"
                value={value}
                onChange={(_event, newValue) => {
                    onChange(newValue)
                }}
                aria-label="Vertical tabs example"
                sx={{ borderRight: 1, borderColor: "divider" }}
            >
                {profiles.map((profile, idx) => {
                    return <Tab key={idx} label={profile} id={`vertical-tab-${idx}`}
                        aria-controls={`vertical-tabpanel-${idx}`} />;
                })}
            </Tabs>
        );
    }
}

export default CLIModGeneratorProfileTabs;
