import * as React from "react";
import { Typography, Box, Link, Tabs, Tab } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useParams } from "react-router";
import GenerationModuleEditorToolBar from "./GenerationModuleEditorToolBar";
import ModuleProfileSelector from "./ModuleProfileSelector";
import axios from "axios";
import EditorPageLayout from "../../components/EditorPageLayout";

const TopPadding = styled(Box)(({ theme }) => ({
  [theme.breakpoints.up("sm")]: {
    height: "12vh",
  },
}));

const MiddlePadding = styled(Box)(({ theme }) => ({
  height: "6vh",
}));

type RegisterType = {
  stage: string;
};

type ResourceType = {
  id: string;
  plane: string;
  version: string;
};

type ExampleTye = {
  commands: string[];
  name: string;
};

type HelpType = {
  short: string;
  examples?: ExampleTye[];
};

type LeafType = {
  help: HelpType;
  names: string[];
  registerInfo: RegisterType;
  resources: ResourceType[];
  stage: string;
  version: string;
};

type Leaves = {
  [name: string]: LeafType;
};

type NodeType = {
  help: HelpType;
  names: string[];
  registerInfo: RegisterType;
  commandGroups?: Nodes;
  commands?: Leaves;
};

type Nodes = {
  [name: string]: NodeType;
};

interface GenerationModuleEditorProps {
  params: {
    repoName: string;
    moduleName: string;
  };
}

interface GenerationModuleEditorState {
  repoName: string;
  moduleName: string;
  toBeGenerated: Nodes;
  profileIndex: number;
  profiles: string[];
}

class GenerationModuleEditor extends React.Component<
  GenerationModuleEditorProps,
  GenerationModuleEditorState
> {
  constructor(props: GenerationModuleEditorProps) {
    super(props);
    this.state = {
      repoName: this.props.params.repoName,
      moduleName: this.props.params.moduleName,
      toBeGenerated: {},
      profileIndex: 0,
      profiles: [],
    };
  }

  componentDidMount() {
    this.loadProfiles();
    this.loadCommandsModels();
    this.loadLocalCommands();
  }

  loadProfiles = () => {
    axios
      .get("/CLI/Az/Profiles")
      .then((res) => {
        this.setState({ profiles: res.data });
      })
      .catch((err) => {
        console.error(err.response);
      });
  };

  loadCommandsModels = () => {};

  loadLocalCommands = () => {
    axios
      .get(`/CLI/Az/Main/Modules/${this.state.moduleName}`)
      .then((res) => {
        this.setState({ toBeGenerated: res.data["profiles"] });
      })
      .catch((err) => {
        console.error(err.response);
      });
  };

  handleBackToHomepage = () => {
    window.location.href = `/?#/generation`;
  };

  handleGenerate = () => {
    axios
      .put(`/CLI/Az/${this.state.repoName}/Modules/${this.state.moduleName}`, {
        profiles: this.state.toBeGenerated,
      })
      .then(() => {})
      .catch((err) => {
        console.error(err.response);
      });
  };

  handleProfileChange = (event: React.SyntheticEvent, newValue: number) => {
    this.setState({ profileIndex: newValue });
  };

  render() {
    const { moduleName } = this.state;
    return (
      <React.Fragment>
        <GenerationModuleEditorToolBar
          moduleName={moduleName}
          onHomePage={this.handleBackToHomepage}
          onGenerate={this.handleGenerate}
        >

        </GenerationModuleEditorToolBar>
        <EditorPageLayout>
          <Box
            sx={{
              flexShrink: 0,
              width: 250,
              flexDirection: "column",
              display: "flex",
              alignItems: "stretch",
              justifyContent: "flex-start",
              marginRight: "3vh",
            }}
          >
            <ModuleProfileSelector
                value={this.state.profileIndex}
              profiles={this.state.profiles}
              onChange={this.handleProfileChange}
            >

            </ModuleProfileSelector>
          </Box>
        </EditorPageLayout>
      </React.Fragment>
    );
  }
}

const GenerationModuleEditorWrapper = (props: any) => {
  const params = useParams();
  return <GenerationModuleEditor params={params} {...props} />;
};

export { GenerationModuleEditorWrapper as GenerationModuleEditor };
