import React from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";

interface CLIModGeneratorProfileTabsProps {
  value: string;
  profiles: string[];
  onChange: (newValue: string) => void;
}

const CLIModGeneratorProfileTabs: React.FC<CLIModGeneratorProfileTabsProps> = ({ value, profiles, onChange }) => {
  return (
    <Tabs
      orientation="vertical"
      variant="scrollable"
      value={value}
      onChange={(_event, newValue) => {
        onChange(newValue);
      }}
      aria-label="Vertical tabs example"
      sx={{ borderRight: 1, borderColor: "divider" }}
    >
      {profiles.map((profile) => (
        <Tab
          key={profile}
          label={profile}
          id={`vertical-tab-${profile}`}
          aria-controls={`vertical-tabpanel-${profile}`}
          value={profile}
        />
      ))}
    </Tabs>
  );
};

export default CLIModGeneratorProfileTabs;
