import yaml

def _update_config(config, yaml_content):
    for key, value in yaml_content.items():
        if key not in config:
            config[key] = value
            continue
        if isinstance(value, dict):
            _update_config(config[key], value)
        elif isinstance(value, list):
            config[key].extend(value)
        else:
            config[key] = value

def parse_readme_file(readme_path: str):
    """Parse the readme file title and combine basic config in the yaml section."""
    readme_config = {}
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    # content.append("```") # append a fake yaml section to make sure the last yaml section is ended
    readme_title = None
    in_yaml_section = False
    yaml_content = []
    for line in content:
        if not readme_title and line.strip().startswith("# ") and not in_yaml_section:
            readme_title = line.strip()[2:].strip()
        if line.strip().startswith("```") and 'yaml' in line:
            condition = line.split('yaml')[1].strip()
            # Do not parse the yaml section if it has the condition
            if not condition:
                in_yaml_section = True
        elif in_yaml_section:
            if line.strip().startswith("```"):
                try:
                    yaml_config = yaml.safe_load("\n".join(yaml_content))
                except Exception as e:
                    raise ValueError(f"Failed to parse autorest config: {e} for readme_file: {readme_path}")
                _update_config(readme_config, yaml_config)
                in_yaml_section = False
                yaml_content = []
            else:
                if line.strip():
                    yaml_content.append(line)
                else:
                    yaml_content.append("")

    return {
        "title": readme_title,
        "config": readme_config
    }
