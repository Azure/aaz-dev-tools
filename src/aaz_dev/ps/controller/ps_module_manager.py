import logging
import os
import yaml

from utils.config import Config

logger = logging.getLogger('backend')


class PSModuleManager:

    def __init__(self):
        module_folder = self._find_module_folder()
        self.folder = module_folder

    def _find_module_folder(self):
        powershell_folder = Config.POWERSHELL_PATH
        if not os.path.exists(powershell_folder) or not os.path.isdir(powershell_folder):
            raise ValueError(f"Invalid PowerShell folder: '{powershell_folder}'")
        module_folder = os.path.join(powershell_folder, "src")
        if not os.path.exists(module_folder):
            raise ValueError(f"Invalid PowerShell folder: cannot find modules in: '{module_folder}'")
        return module_folder

    def list_modules(self):
        modules = []
        for folder_name in os.listdir(self.folder):
            path = os.path.join(self.folder, folder_name)
            if os.path.isdir(path):
                for sub_folder in os.listdir(path):
                    if os.path.isdir(os.path.join(path, sub_folder)) and sub_folder.endswith(".Autorest"):
                        name = f"{folder_name}/{sub_folder}"
                        modules.append({
                            "name": name,
                            "folder": os.path.join(path, sub_folder)
                        })
        return sorted(modules, key=lambda a: a['name'])

    def create_new_mod(self, module_names):
        if isinstance(module_names, str):
            module_names = module_names.split('/')
        folder = os.path.join(self.folder, *module_names)
        os.makedirs(folder, exist_ok=True)

    def load_module(self, module_names):
        if isinstance(module_names, str):
            module_names = module_names.split('/')
        folder = os.path.join(self.folder, *module_names)
        if not os.path.exists(folder):
            raise ValueError(f"Module folder not found: '{folder}'")
        autorest_config = self.load_autorest_config(module_names)
        return {
            **autorest_config,
            "name": "/".join(module_names),
            "folder": folder
        }

    def load_autorest_config(self, module_names):
        if isinstance(module_names, str):
            module_names = module_names.split('/')
        folder = os.path.join(self.folder, *module_names)
        readme_file = os.path.join(folder, "README.md")
        if not os.path.exists(readme_file):
            raise ValueError(f"README.md not found in: '{readme_file}'")
        with open(readme_file, "r") as f:
            content = f.readlines()
        autorest_config = []
        in_autorest_config_section = False
        in_yaml_section = False
        for line in content:
            if line.strip().startswith("### AutoRest Configuration"):
                in_autorest_config_section = True
            elif in_autorest_config_section:
                if line.strip().startswith("###"):
                    break
                if line.strip().startswith("```") and 'yaml' in line:
                    in_yaml_section = True
                elif in_yaml_section:
                    if line.strip().startswith("```"):
                        in_yaml_section = False
                    else:
                        if line.strip():
                            autorest_config.append(line)
                        else:
                            autorest_config.append("")
        autorest_config_raw = "\n".join(autorest_config)
        try:
            yaml_config = yaml.load(autorest_config_raw, Loader=yaml.FullLoader)
        except Exception as e:
            raise ValueError(f"Failed to parse autorest config: {e} for readme_file: {readme_file}")
        return {
            "autorest_config": yaml_config,
            # "raw": autorest_config_raw  # can be used for directive merging
        }
