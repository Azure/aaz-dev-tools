import logging
import os

from utils.config import Config
from utils.plane import PlaneEnum
from utils.readme_helper import parse_readme_file
from utils.exceptions import InvalidAPIUsage, VerificationError
from ps.model import PSModuleConfig
from swagger.controller.specs_manager import SwaggerSpecsManager
from command.controller.specs_manager import AAZSpecsManager
from swagger.model.specs import OpenAPIResourceProvider
from swagger.utils.tools import resolve_path_to_uri
logger = logging.getLogger('backend')


class PSModuleManager:

    def __init__(self):
        module_folder = self._find_module_folder()
        self.folder = module_folder
        self._aaz_specs = None
        self._swagger_specs = None

    @property
    def aaz_specs(self):
        if not self._aaz_specs:
            self._aaz_specs = AAZSpecsManager()
        return self._aaz_specs

    @property
    def swagger_specs(self):
        if not self._swagger_specs:
            self._swagger_specs = SwaggerSpecsManager()
        return self._swagger_specs

    def _find_module_folder(self):
        powershell_folder = Config.POWERSHELL_PATH
        if not os.path.exists(powershell_folder) or not os.path.isdir(powershell_folder):
            raise VerificationError(f"Invalid PowerShell folder: '{powershell_folder}'")
        module_folder = os.path.join(powershell_folder, "src")
        if not os.path.exists(module_folder):
            raise VerificationError(f"Invalid PowerShell folder: cannot find modules in: '{module_folder}'")
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
            raise VerificationError(f"Module folder not found: '{folder}'")
        config = self.load_module_config(module_names)
        return config

    def load_autorest_config(self, module_names):
        if isinstance(module_names, str):
            module_names = module_names.split('/')
        folder = os.path.join(self.folder, *module_names)
        readme_file = os.path.join(folder, "README.md")
        if not os.path.exists(readme_file):
            raise VerificationError(f"README.md not found in: '{readme_file}'")
        content = parse_readme_file(readme_file)
        return content['config'], content['title']

    def load_module_config(self, module_names):
        # TODO: support multiple resource providers
        try:
            autorest_config, readme_title = self.load_autorest_config(module_names)
        except:
            logger.error(f"Failed to load autorest config for module: {module_names}, error: {e}")
            raise
        
        config = PSModuleConfig()
        config.name = "/".join(module_names)
        config.folder = self.folder
        if not autorest_config:
            raise VerificationError(f"autorest config not found in README.md for module: {config.name}")

        # config.swagger = autorest_config
        repo = autorest_config.get('repo', "https://github.com/Azure/azure-rest-api-specs/blob/$(commit)")
        if commit := autorest_config.get('commit'):
            repo = repo.replace("$(commit)", commit)
        if "$(commit)" in repo:
            # make sure the repo is valid https link or valid folder path
            raise VerificationError(f"commit is not defined in autorest config for module: {config.name}")
        config.repo = repo

        readme_files = set()
        for required_file in autorest_config['require']:
            if required_file.startswith('$(repo)/') and required_file.endswith('/readme.md'):
                readme_file = required_file.replace('$(repo)/', '')
                readme_files.add(readme_file)

        if not readme_files:
            # search all the readme.md files from the input files
            for input_file in autorest_config.get('input-file', []):
                if "/specification/" in input_file:
                    readme_file = None
                    folder_names = input_file.split("/specification/")[1].split("/")[:-1]
                    path = os.path.join(self.swagger_specs.specs.spec_folder_path, *folder_names)
                    while path != self.swagger_specs.specs.spec_folder_path:
                        if os.path.exists(os.path.join(path, "readme.md")):
                            readme_file = os.path.join(path, "readme.md")
                            break
                        path = os.path.dirname(path)
                    if readme_file:
                        readme_file = resolve_path_to_uri(readme_file)
                        readme_files.add(readme_file)
        if not readme_files:
            raise VerificationError(f"swagger readme.md not defined in autorest config for module: {config.name}")
        
        # use the local swagger specs to find the resource provider even the repo is in remote
        # we can always suppose the local swagger specs will always be newer than the used commit in submitted azure.powershell code
        rps = []
        for readme_file in readme_files:
            rp = None
            readme_config = None
            plane = PlaneEnum.Mgmt if "resource-manager" in readme_file else PlaneEnum._Data
            for module in self.swagger_specs.get_modules(plane):
                module_relative_path = resolve_path_to_uri(module.folder_path) + "/"
                if readme_file.startswith(module_relative_path):
                    for resource_provider in module.get_resource_providers():
                        if not isinstance(resource_provider, OpenAPIResourceProvider):
                            continue
                        readme_config = resource_provider.load_readme_config(readme_file)
                        if readme_config:
                            rp = resource_provider
                            break
                    if rp:
                        break
            if not rp:
                raise VerificationError(f"Resource provider not found in autorest config for module: {config.name} with readme file: {readme_file}")
            rps.append(rp)
        config.rps = rps
        # config.swagger = str(rp)

        if tag := autorest_config.get('tag'):
            config.tag = tag
        if input_files := autorest_config.get('input-file'):
            config.input_files = []
            for input_file in input_files:
                if '/specification/' in input_file:
                    file_path = input_file.split('/specification/')[1]
                    file_path = os.path.join(self.swagger_specs.specs.spec_folder_path, *file_path.split('/'))
                    if not os.path.exists(file_path):
                        raise VerificationError(f"Input file not found for module: {config.name}, input file: {file_path}")
                    config.input_files.append(file_path)
        if not config.input_files and not config.tag:
            # using the tag from swagger readme config
            config.tag = readme_config.get('tag', None)
        if config.tag and len(rps) > 1:
            raise VerificationError(f"Multiple resource providers found for module: {config.name} with tag: {config.tag}")
        if config.tag and config.tag not in rps[0].tags:
            raise VerificationError(f"Tag not found in resource provider for module: {config.name} with tag: {config.tag}")
        if not config.input_files and config.tag:
            config.input_files = list(rps[0].tags[config.tag])
        
        if not config.input_files:
            raise VerificationError(f"Input file not found in autorest config for module: {config.name}")

        if readme_title.startswith("Az."):
            config.service_name = readme_title.split(".")[1]
        if title := autorest_config.get('title'):
            config.title = title
        else:
            # get title from swagger readme
            config.title = readme_config.get('title', None)

        if not config.title:
            # TODO: get title from swagger json file
            raise VerificationError(f"Title not found in autorest config or swagger readme for module: {config.name}")

        return config
