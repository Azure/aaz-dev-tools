from command.model.configuration import CMDCommand, CMDHttpOperation
from command.model.specs import CMDSpecsCommand, CMDSpecsCommandVersion
from utils import exceptions, portal_file_schema
from utils.config import Config
import os, json, re, logging
import jsonschema


class PortalCliGenerator:
    COMMAND_ROOT_NAME = "az"
    DOC_ROOT_NAME = "https://docs.microsoft.com/cli/azure"

    # az change-analysis list --star-ttime bbb --endtime aaa -g aaa
    PARA_REG_PATTERN = re.compile(r" --?([a-zA-Z0-9\-]+) ?")

    # /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}...
    # /providers/Microsoft.Network/dnsResolvers/{dnsResolverName}/inboundEndpoints/{inboundEndpointName}
    RESOURCE_PATH_PATTERN = re.compile(r"/([a-zA-Z0-9\-]+)/?")

    # /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}...
    # /providers/Microsoft.OperationalInsights/workspaces/{workspaceName}...
    # /providers/Microsoft.SecurityInsights/incidents/{incidentId}

    def __init__(self):
        pass

    def fill_resource_type(self, cmd_portal_info, cmd_cfg, leaf):
        """
        path: ....Microsoft.Network/dnsForwardingRulesets/{dnsForwardingRulesetName}/forwardingRules/{forwardingRuleName}
        resource_type: dnsForwardingRulesets/forwardingRules
        path: ....Microsoft.Network/dnsForwardingRulesets/{dnsForwardingRulesetName}/forwardingRules -> list cmd
        resource_type: dnsForwardingRulesets
        """
        if cmd_cfg.resources is None:
            raise exceptions.ResourceNotFind("Resource not exist")
        resource = cmd_cfg.resources[-1]
        if resource.rp_name is None:
            raise exceptions.ResourceNotFind("Resource rp_name not exist")
        if resource.swagger_path is None:
            raise exceptions.ResourceNotFind("Resource swagger_path not exist")
        rp_name = resource.rp_name
        swagger_path = resource.swagger_path
        cmd_portal_info['rp_name'] = rp_name
        swagger_provider_ind = swagger_path.lower().rfind(rp_name.lower())
        if swagger_provider_ind == -1:
            logging.warning("please check cmd " + " ".join(leaf.names) + " resource id: " + swagger_path)
            return
        folder_end_ind = swagger_path.rfind("{", swagger_provider_ind)
        resource_paths = re.finditer(self.RESOURCE_PATH_PATTERN, swagger_path[swagger_provider_ind:folder_end_ind])
        resource_type = ""
        for resource_match in resource_paths:
            resource_folder = resource_match.group(1)
            if len(resource_type) == 0:
                resource_type += resource_folder
            else:
                resource_type += "/" + resource_folder
        cmd_portal_info['resourceType'] = resource_type

    def fill_api_version(self, cmd_portal_info, target_version):
        if target_version.name is None:
            raise exceptions.ResourceNotFind("version name not exist")
        cmd_portal_info['apiVersion'] = target_version.name

    def generate_base_learn_more(self, cmd_portal_info, leaf):
        """
        cmd: az xx yy zz
        leaf.names: [xx, yy, zz]
        help link: https://learn.microsoft.com/cli/azure/xx/yy
        """
        base_help_url = self.DOC_ROOT_NAME + "/" + "/".join(leaf.names[:-1])
        cmd_portal_info['learnMore'] = {'url': base_help_url}

    def generate_cmd_learn_more(self, help_info, leaf):
        """
        cmd name: az xx yy zz
        leaf.names: [xx, yy, zz]
        help link: https://learn.microsoft.com/cli/azure/xx/yy#az-xx-yy-zz
        """
        cmd_help_url = self.DOC_ROOT_NAME + "/" + "/".join(leaf.names[:-1]) + "#" + \
                       "-".join([self.COMMAND_ROOT_NAME] + leaf.names)
        help_info['learnMore'] = {'url' : cmd_help_url}

    def fill_cmd_name(self, cmd_info, leaf):
        cmd_name = " ".join([self.COMMAND_ROOT_NAME] + leaf.names)
        cmd_info['name'] = cmd_name

    def fill_cmd_desc(self, cmd_info, leaf):
        cmd_info['description'] = leaf.help.to_primitive()['short']

    def fill_cmd_path(self, cmd_info, cmd_cfg):
        if cmd_cfg.resources is None:
            raise exceptions.ResourceNotFind("Resource not exist")
        resource = cmd_cfg.resources[-1]
        cmd_info['path'] = resource.swagger_path

    def fill_cmd_confirmation(self, cmd_info, cmd_cfg):
        if cmd_cfg.confirmation:
            cmd_info['confirmation'] = True
        else:
            cmd_info['confirmation'] = False

    def fill_cmd_help(self, cmd_info, cmd_cfg, leaf):
        help_info = {}
        self.generate_cmd_learn_more(help_info, leaf)
        option_list = []
        for arg_group in cmd_cfg.arg_groups:
            for arg in arg_group.args:
                assert arg.options is not None
                if len(arg.options) > 0:
                    # parameter set ignore 1 character option
                    option_list += filter(lambda opt: len(opt) > 1, arg.options)
        parameters_list = [ "[--" + param_name + "]" for param_name in option_list]
        help_info['parameterSets'] = [{'parameters': parameters_list}]
        cmd_info['help'] = help_info

    def generate_default_example(self, cmd_info, leaf, var_option_list):
        parameters = []
        for (para_var, raw_options, is_required, is_in_path) in var_option_list:
            if not is_required:
                continue
            pick_options = list(filter(lambda opt: len(opt) > 1, raw_options))
            pick_option = pick_options[0]
            parameters.append({
                'name': ("-" if len(pick_option) == 1 else "--") + pick_option,
                'value': "[" + para_var.replace("$Path", "path") + "]"
            })
        if len(parameters) > 0:
            cmd_info['examples'] = [{
                'description': leaf.help.to_primitive()['short'],
                'parameters': parameters
            }]

    def find_para_var(self, para, var_option_list):
        for (var, options, is_required, is_in_path) in var_option_list:
            if para in options:
                return (var, options, is_required, is_in_path)
        return (None, None, None, None)

    def fill_cmd_examples(self, cmd_info, cmd_cfg, leaf, target_version):
        var_option_list = []
        var_required = set()
        sub_id_required = False
        for arg_group in cmd_cfg.arg_groups:
            for arg in arg_group.args:
                assert arg.options is not None
                if len(arg.options) == 0: continue
                is_required = arg.required
                var_name = arg.var
                if arg.required and var_name.find("subscriptionId") == -1:
                    # for user input cmd example, ignore subscriptionId
                    var_required.add(var_name)
                if arg.required and var_name == "$Path.subscriptionId":
                    sub_id_required = True
                if cmd_info['path'].find("/resourceGroups/{") != -1 and var_name == "$Path.resourceGroupName":
                    var_required.add(var_name)
                    is_required = True
                var_option_list.append((var_name, arg.options,
                                        is_required,
                                        var_name.find('$Path') != -1))

        if not target_version.examples:
            self.generate_default_example(cmd_info, leaf, var_option_list)
            return
        find_example = False
        for example in target_version.examples:
            if find_example: break
            assert example.name is not None
            assert example.commands is not None
            for command_str in example.commands:
                if find_example: break
                param_verify = True
                para_list = []
                para_groups = re.finditer(self.PARA_REG_PATTERN, command_str)
                if not para_groups:
                    continue
                cmd_para = set()
                # 1. check if all parameters in example command str is in path, if not ignore
                for para_match in para_groups:
                    para_name = para_match.group(1)
                    var, raw_options, is_required, is_in_path = self.find_para_var(para_name, var_option_list)
                    # var not found, drop this command_str
                    if not var or not is_in_path:
                        param_verify = False
                        break
                    pick_options = list(filter(lambda opt: len(opt) > 1, raw_options))
                    para_list.append((var, pick_options[0]))
                    cmd_para.add(var)

                # 2. check if all required parameters is in example command str
                # if not, drop this example command str
                if not var_required.issubset(cmd_para):
                    param_verify = False
                if not param_verify: continue
                parameters = []
                sub_id_added = False
                for (var, pick_option) in para_list:
                    if var == "$Path.subscriptionId":
                        sub_id_added = True
                    parameters.append({
                        'name': "--" + pick_option,
                        'value': "[" + var.replace("$Path", "path") + "]"
                    })
                if not sub_id_added and sub_id_required:
                    parameters.append({
                        'name': "--subscription",
                        'value': "[path.subscriptionId]"
                    })

                cmd_info['examples'] = [{
                    'description': example.name,
                    'parameters': parameters
                }]
                find_example = True
        if not find_example:
            self.generate_default_example(cmd_info, leaf, var_option_list)

    def __check_cmd_examples(self, cmd_cfg):
        parameter_verified = True
        for arg_group in cmd_cfg.arg_groups:
            for arg in arg_group.args:
                assert arg.options is not None
                if len(arg.options) == 0: continue
                var_name = arg.var
                if arg.required and var_name.find('$Path') == -1:
                    parameter_verified = False
                    break
        if cmd_cfg.operations:
            for opt in cmd_cfg.operations:
                if isinstance(opt, CMDHttpOperation) \
                        and opt.http.request is not None \
                        and opt.http.request.body is not None:
                    parameter_verified = False
                    break
        return parameter_verified

    def generate_cmd_info(self, cmd_info, cmd_cfg, leaf, target_version):
        self.fill_cmd_name(cmd_info, leaf)
        self.fill_cmd_desc(cmd_info, leaf)
        self.fill_cmd_path(cmd_info, cmd_cfg)
        self.fill_cmd_confirmation(cmd_info, cmd_cfg)
        self.fill_cmd_help(cmd_info, cmd_cfg, leaf)
        if self.__check_cmd_examples(cmd_cfg):
            self.fill_cmd_examples(cmd_info, cmd_cfg, leaf, target_version)

    def generator_command_portal(self, cmd_cfg, leaf, target_version):
        if not isinstance(cmd_cfg, CMDCommand) or \
                not isinstance(leaf, CMDSpecsCommand) or \
                not isinstance(target_version, CMDSpecsCommandVersion):
            return None
        if cmd_cfg.arg_groups is None:
            logging.info("{0} cmd has no arg_group".format(" ".join(leaf.names)))
            return None
        cmd_portal_info = {}
        self.fill_resource_type(cmd_portal_info, cmd_cfg, leaf)
        self.fill_api_version(cmd_portal_info, target_version)
        self.generate_base_learn_more(cmd_portal_info, leaf)
        cmd_info = {}
        self.generate_cmd_info(cmd_info, cmd_cfg, leaf, target_version)
        cmd_portal_info['commands'] = [cmd_info]
        return cmd_portal_info

    def generate_command_portal_raw(self, cmd_cfg, leaf, target_version):
        if not isinstance(cmd_cfg, CMDCommand) or \
                not isinstance(leaf, CMDSpecsCommand) or \
                not isinstance(target_version, CMDSpecsCommandVersion):
            return None
        if cmd_cfg.arg_groups is None:
            logging.info("{0} cmd has no arg_group".format(" ".join(leaf.names)))
            return None
        if not self.__check_cmd_examples(cmd_cfg):
            logging.info("{0} cmd do not has examples".format(" ".join(leaf.names)))
            return None
        cmd_portal_info = {}
        self.fill_resource_type(cmd_portal_info, cmd_cfg, leaf)
        self.fill_api_version(cmd_portal_info, target_version)
        self.generate_base_learn_more(cmd_portal_info, leaf)
        self.generate_cmd_info(cmd_portal_info, cmd_cfg, leaf, target_version)
        return cmd_portal_info

    def get_portal_file_path(self):
        cli_folder = Config.CLI_PATH
        if not os.path.exists(cli_folder) or not os.path.isdir(cli_folder):
            raise ValueError(f"Invalid Cli Main Repo folder: '{cli_folder}'")
        data_model_folder = os.path.join(cli_folder, "data-model-for-portal")
        return data_model_folder

    def valid_portal_json_format(self, portal_data):
        try:
            jsonschema.validate(instance=portal_data, schema=portal_file_schema.PORTAL_FILE_SCHEMA)
        except jsonschema.exceptions.ValidationError as err:
            #print(err)
            return False
        return True

    def generate_portal_file(self, portal_dict):
        data_model_folder = self.get_portal_file_path()
        for rp_name, resource_infos in portal_dict.items():
            for resource_type, resource_info in resource_infos.items():
                resource_paths = [rp_name] + resource_type.split("/")
                resource_file_path = data_model_folder + "/" + "/".join(resource_paths[:-1]) + "/" + \
                                     resource_paths[-1] + ".json"
                resource_file_folder = os.path.dirname(resource_file_path)
                if not os.path.exists(resource_file_folder):
                    os.makedirs(resource_file_folder)
                if not self.valid_portal_json_format(resource_info):
                    logging.info("json format error")
                    continue
                with open(resource_file_path, "w", encoding="utf-8") as f_out:
                    f_out.write(json.dumps(resource_info, indent=4))

    def generate_cmds_portal_file(self, cmd_portal_list):
        portal_dict = {}
        cmd_dedup = set()
        for cmd_portal_info in cmd_portal_list:
            if ('rp_name' not in cmd_portal_info or 'resourceType' not in cmd_portal_info or
                    'apiVersion' not in cmd_portal_info or 'name' not in cmd_portal_info):
                continue

            cmd_name = cmd_portal_info['name']
            if cmd_name in cmd_dedup:
                logging.info("{0} cmd has repeated from versions {1}".format(cmd_name, cmd_portal_info['apiVersion']))
                continue
            cmd_dedup.add(cmd_name)
            rp_name = cmd_portal_info['rp_name']
            rescoure_type = cmd_portal_info['resourceType']
            api_version = cmd_portal_info['apiVersion']
            learn_more = cmd_portal_info['learnMore']

            del cmd_portal_info['rp_name'], cmd_portal_info['resourceType']
            del cmd_portal_info['apiVersion'], cmd_portal_info['learnMore']
            if rp_name not in portal_dict:
                portal_dict[rp_name] = {
                    rescoure_type: {
                        "resourceType": rescoure_type,
                        "apiVersion": api_version,
                        "learnMore": learn_more,
                        'commands': [cmd_portal_info]
                    }
                }
                continue
            rescoure_infos = portal_dict[rp_name]
            if rescoure_type not in rescoure_infos:
                rescoure_infos[rescoure_type] = {
                    "resourceType": rescoure_type,
                    "apiVersion": api_version,
                    "learnMore": learn_more,
                    'commands': [cmd_portal_info]
                }
                continue
            rescoure_info = rescoure_infos[rescoure_type]
            rescoure_info['commands'].append(cmd_portal_info)

        self.generate_portal_file(portal_dict)

    def generate_cmds_portal_info(self, aaz_spec_manager, registered_cmds):
        cmd_portal_list = []
        for cmd_name_version in registered_cmds:
            # cmd_name_version = ['monitor', 'diagnostic-setting', 'list', '2021-05-01-preview']
            node_names = cmd_name_version[:-2]
            leaf_name = cmd_name_version[-2]
            registered_version = cmd_name_version[-1]
            leaf = aaz_spec_manager.find_command(*node_names, leaf_name)
            if not leaf or not leaf.versions:
                logging.warning("Command group: " + " ".join(node_names) + " not exist")
                continue
            if not leaf.versions:
                logging.warning("Command group: " + " ".join(node_names) + " version not exist")
                continue
            target_version = None
            for v in (leaf.versions or []):
                if v.name == registered_version:
                    target_version = v
                    break
            if not target_version:
                logging.warning("Command: " + " ".join(node_names) + " version not exist")
                continue
            logging.info("Generating portal config of [ az {0} ] with registered version {1}".format(" ".join(cmd_name_version[:-1]),
                                                                                              registered_version))
            cfg_reader = aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(leaf, version=target_version)
            cmd_cfg = cfg_reader.find_command(*leaf.names)
            cmd_portal_info = self.generate_command_portal_raw(cmd_cfg, leaf, target_version)
            if cmd_portal_info:
                cmd_portal_list.append(cmd_portal_info)
        return cmd_portal_list

if __name__ == '__main__':
    generator = PortalCliGenerator()
    resource_info = {
        "resourceType": "virtualMachines",
        "apiVersion": "2021-11-01",
        "confirmation": True,
        "learnMore": {
            "url": "https://docs.microsoft.com/cli/azure/vm"
        },
    }
    schema = {
        "type": "object",
        "properties": {
            "resourceType": {"type": "string"},
            "apiVersion": {"type": "string"},
            "confirmation": {"type": "boolean"},
            "learnMore": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                }
            }
        }
    }
    print(jsonschema.validate(instance=resource_info, schema=schema))
    try:
        jsonschema.validate(instance=resource_info, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)

    print("verification done")


