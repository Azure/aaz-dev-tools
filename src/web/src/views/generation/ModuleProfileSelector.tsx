import * as React from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";

function a11yProps(index: number) {
  return {
    id: `vertical-tab-${index}`,
    "aria-controls": `vertical-tabpanel-${index}`,
  };
}

interface ModuleProfileSelectorProps {
  value: number;
  profiles: string[];
  onChange: (event: React.SyntheticEvent, newValue: number) => void;
}

class ModuleProfileSelector extends React.Component<ModuleProfileSelectorProps> {
  render() {
    const { value, profiles, onChange } = this.props;
    return (
        <Tabs
          orientation="vertical"
          variant="scrollable"
          value={value}
          onChange={onChange}
          aria-label="Vertical tabs example"
          sx={{ borderRight: 1, borderColor: "divider" }}
        >
          {profiles.map((profile, idx) => {
            return <Tab key={idx} label={profile} {...a11yProps(idx)} />;
          })}
        </Tabs>
    );
  }
}

export default ModuleProfileSelector;
