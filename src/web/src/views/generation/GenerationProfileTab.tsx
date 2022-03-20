import * as React from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";

interface GenerationProfileTabProps {
  value: number;
  profiles: string[];
  onChange: (event: React.SyntheticEvent, newValue: number) => void;
}

function a11yProps(index: number) {
  return {
    id: `vertical-tab-${index}`,
    "aria-controls": `vertical-tabpanel-${index}`,
  };
}

class GenerationProfileTab extends React.Component<GenerationProfileTabProps> {
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

export default GenerationProfileTab;
