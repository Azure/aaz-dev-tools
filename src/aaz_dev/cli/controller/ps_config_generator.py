from .az_module_manager import AzModuleManager
from swagger.controller.specs_manager import SwaggerSpecsManager
from command.controller.specs_manager import AAZSpecsManager
from utils.config import Config
from utils.exceptions import ResourceNotFind
from command.model.configuration import CMDConfiguration, CMDResource, CMDHttpOperation
import json
import logging
from pluralizer import Pluralizer
import re
import os
from swagger.model.specs._utils import map_path_2_repo

from fuzzywuzzy import fuzz


logger = logging.getLogger("backend")

class PSAutoRestConfiguration:
    
    def __init__(self):
        self.commit = None
        self.version = None
        self.module_name = None
        self.readme_file = None
        self.removed_subjects = []
        self.removed_verbs = []


class PSAutoRestConfigurationGenerator:
    _CAMEL_CASE_PATTERN = re.compile(r"^([a-zA-Z][a-z0-9]+)(([A-Z][a-z0-9]*)+)$")
    _pluralizer = Pluralizer()

    def __init__(self, az_module_manager: AzModuleManager, module_name) -> None:
        self.module_manager = az_module_manager
        self.module_name = module_name
        self.aaz_specs_manager = AAZSpecsManager()
        self.swagger_specs_manager = SwaggerSpecsManager()
        self._ps_profile = None

    def generate_config(self):
        ps_cfg = PSAutoRestConfiguration()
        # TODO: get the commit using git
        ps_cfg.commit = "cbbe228fd422db02b65e2748f83df5f2bcad7581"

        module = self.module_manager.load_module(self.module_name)

        cli_profile = {}

        for cli_command in self.iter_cli_commands(
            module.profiles[Config.CLI_DEFAULT_PROFILE]
        ):
            names = cli_command.names
            version_name = cli_command.version
            aaz_cmd = self.aaz_specs_manager.find_command(*names)
            if not aaz_cmd:
                raise ResourceNotFind(
                    "Command '{}' not exist in AAZ".format(" ".join(names))
                )
            version = None
            for v in aaz_cmd.versions or []:
                if v.name == version_name:
                    version = v
                    break
            if not version:
                raise ResourceNotFind(
                    "Version '{}' of command '{}' not exist in AAZ".format(
                        version_name, " ".join(names)
                    )
                )
            resource = v.resources[0]
            cfg: CMDConfiguration = self.aaz_specs_manager.load_resource_cfg_reader(
                resource.plane, resource.id, resource.version
            )
            if not cfg:
                raise ResourceNotFind(
                    "Resource Configuration '{}' not exist in AAZ".format(resource.id)
                )
            for resource in cfg.resources:
                tag = (resource.plane, "/".join(resource.mod_names), resource.rp_name)
                if tag not in cli_profile:
                    cli_profile[tag] = {}
                if resource.id not in cli_profile[tag]:
                    cli_profile[tag][resource.id] = {
                        "path": resource.path,
                        "cfg": cfg,
                        "commands": [],
                        "subresources": [],
                    }
                cli_profile[tag][resource.id]["commands"].append(cli_command.names)
                if resource.subresource:
                    cli_profile[tag][resource.id]["subresources"].append(
                        resource.subresource
                    )

        # TODO: let LLM to choice the plane and rp_name later
        if len(cli_profile.keys()) > 1:
            raise ValueError("Only one plane module and rp_name is supported")
        (plane, mod_names, rp_name) = list(cli_profile.keys())[0]
        cli_resources = cli_profile[(plane, mod_names, rp_name)]

        module_manager = self.swagger_specs_manager.get_module_manager(
            plane, mod_names.split("/")
        )
        rp = module_manager.get_openapi_resource_provider(rp_name)
        swagger_resources = rp.get_resource_map_by_tag(rp.default_tag)
        if not swagger_resources:
            raise ResourceNotFind("Resources not find in Swagger")
        
        readme_parts= rp._readme_path.split(os.sep)
        ps_cfg.readme_file = '/'.join(readme_parts[readme_parts.index("specification"):])
        ps_cfg.version = "0.1.0"
        ps_cfg.module_name = mod_names.split("/")[0]
        ps_cfg.module_name = ps_cfg.module_name[0].upper() + ps_cfg.module_name[1:]

        ps_profile = {}
        
        # create ps_profile by swagger resources
        for resource_id, resource in swagger_resources.items():
            resource = list(resource.values())[0]
            methods = set()
            operations = {}
            op_group_name = self.get_operation_group_name(resource)
            if resource_id not in cli_resources:
                # the whole resource id is not used in cli
                for op_tag, method in resource.operations.items():
                    operations[op_tag] = {
                        "tag": op_tag,
                        "delete": True,
                        "resource_id": resource_id,
                        "method": method,
                    }
                    methods.add(method)
            else:
                for cmd_names in cli_resources[resource_id]["commands"]:
                    cfg = cli_resources[resource_id]["cfg"]
                    command = cfg.find_command(*cmd_names)
                    assert command is not None
                    for cmd_op in command.operations:
                        if not isinstance(cmd_op, CMDHttpOperation):
                            continue
                        op_tag = cmd_op.operation_id
                        if op_tag not in resource.operations:
                            # make sure the operation is from the same resource
                            continue
                        method = resource.operations[op_tag]
                        operations[op_tag] = {
                            "tag": op_tag,
                            "delete": False,
                            "resource_id": resource_id,
                            "method": method,
                        }
                        methods.add(method)

                for op_tag, method in resource.operations.items():
                    if op_tag not in operations:                        
                        operations[op_tag] = {
                            "tag": op_tag,
                            "delete": (
                                False if method == "patch" else True
                            ),  # PowerShell Prefer Patch Method for update commands
                            "resource_id": resource_id,
                            "method": method,
                        }
                        methods.add(method)
            
            for op_tag, op in operations.items():
                variants = self.inferCommandNames(op_tag, op_group_name)
                op['variants'] = []
                for variant in variants:
                    if op['method'] == 'put' and variant['action'] == 'Update':
                        if 'get' not in methods:
                            # "update" should be "set" if it's a PUT and not the generic update (GET+PUT)
                            variant['verb'] = 'Set'
                        else:
                            use_generic_update = True
                            for patch_op in operations.values():
                                if patch_op['method'] == 'patch':
                                    use_generic_update = patch_op['delete']
                                    break
                            if not use_generic_update:
                                continue
                    op['variants'].append(variant)
                # make sure the variants should have the same subject
                subjects = list(set([v['subject'] for v in op['variants']]))
                assert len(subjects) == 1, f"Operation {op_tag} has different subjects: {subjects}"

                subject = subjects[0]
                if subject not in ps_profile:
                    ps_profile[subject] = {
                        "operations": {},
                        "delete": False,
                    }
                ps_profile[subject]["operations"][op_tag] = op
            
        for subject in ps_profile.values():
            subject_delete = True
            for op in subject['operations'].values():
                if not op['delete']:
                    subject_delete = False
                    break
            subject['delete'] = subject_delete

        self._ps_profile = ps_profile

        ps_cfg.removed_subjects = []
        ps_cfg.removed_verbs = []
        for subject_name, subject in ps_profile.items():
            if subject['delete']:
                ps_cfg.removed_subjects.append(subject_name)
                continue
            for op in subject['operations'].values():
                if op['delete']:
                    for variant in op['variants']:
                        ps_cfg.removed_verbs.append((variant['subject'], variant['verb']))
        return ps_cfg

    def iter_cli_commands(self, profile):
        for command_group in profile.command_groups.values():
            for cli_command in self._iter_cli_commands(command_group):
                yield cli_command

    def _iter_cli_commands(self, view_command_group):
        if view_command_group.commands:
            for cli_command in view_command_group.commands.values():
                yield cli_command
        if view_command_group.command_groups:
            for command_group in view_command_group.command_groups.values():
                for cli_command in self._iter_cli_commands(command_group):
                    yield cli_command

    def get_operation_group_name(self, resource):
        operation_groups = set()
        for operation_id, method in resource.operations.items():
            op_group = self._parse_operation_group_name(resource, operation_id, method)
            operation_groups.add(op_group)

        if None in operation_groups:
            return None

        if len(operation_groups) == 1:
            return operation_groups.pop()

        op_group_name = sorted(
            operation_groups,
            key=lambda nm: fuzz.partial_ratio(
                resource.id, nm
            ),  # use the name which is closest to resource_id
            reverse=True,
        )[0]
        return op_group_name

    def _parse_operation_group_name(self, resource, op_id, method):
        # extract operation group name from operation_id
        value = op_id.strip()
        value = value.replace("-", "_")
        if "_" in value:
            parts = value.split("_")
            op_group_name = parts[0]
            if op_group_name.lower() in ("create", "get", "update", "delete", "patch"):
                op_group_name = parts[1]
        else:
            if " " in value:
                value = value.replace(" ", "")  # Changed to Camel Case
            match = self._CAMEL_CASE_PATTERN.match(value)
            if not match:
                logger.error(
                    f"InvalidOperationIdFormat:"
                    f"\toperationId should be in format of '[OperationGroupName]_[OperationName]' "
                    f"or '[Verb][OperationGroupName]':\n"
                    f"\tfile: {map_path_2_repo(resource.file_path)}\n"
                    f"\tpath: {resource.path}\n"
                    f"\tmethod: {method} operationId: {op_id}\n"
                )
                return None
            op_group_name = match[2]  # [OperationGroupName]

        return self.singular_noun(op_group_name)
    
    @classmethod
    def inferCommandNames(cls, operation_id, op_group_name):
        parts = operation_id.split("_")
        assert len(parts) == 2
        method = parts[1]
        method = method[0].upper() + method[1:]

        if VERB_MAPPING.get(method):
            return [
                cls.create_command_variant(method, [op_group_name], [])
            ]

        # split camel case to words
        words = re.findall(r'[A-Z][a-z]*', method)
        return cls._infer_command(words, op_group_name, [])

    @classmethod
    def _infer_command(cls, operation, op_group_name, suffix):
        operation = [w for w in operation if w != 'All']
        if len(operation) == 1:
            # simple operation, just an id with a single value
            return [
                cls.create_command_variant(operation[0], [op_group_name], suffix)
            ]
        
        if len(operation) == 2:
            # should try to infer [SUBJECT] and [ACTION] from operation
            if VERB_MAPPING.get(operation[0]):
                # [ACTION][SUBJECT]
                return [
                    cls.create_command_variant(operation[0], [op_group_name, operation[1]], suffix)
                ]
            if VERB_MAPPING.get(operation[1]):
                # [SUBJECT][ACTION]
                return [
                    cls.create_command_variant(operation[1], [op_group_name, operation[0]], suffix)
                ]
            logger.warning(f"Operation ${operation[0]}/${operation[1]} is inferred without finding action.")
            return [
                cls.create_command_variant(operation[0], [op_group_name, operation[1]], suffix)
            ]
        
        # three or more words.
        # first, see if it's an 'or'
        if 'Or' in operation:
            idx = operation.index('Or')
            return cls._infer_command(
                operation[:idx] + operation[idx+2:],
                op_group_name,
                suffix
            ) + cls._infer_command(
                operation[idx+1:],
                op_group_name,
                suffix
            )
        
        for w in ['With', 'At', 'By', 'For', 'In', 'Of']:
            if w in operation:
                idx = operation.index(w)
                if idx > 0:
                    # so this is something like DoActionWithStyle
                    return cls._infer_command(
                        operation[:idx],
                        op_group_name,
                        operation[idx:],
                    )

        # if not, then seek out a verb from there.
        for i in range(len(operation)):
            if VERB_MAPPING.get(operation[i]):
                # if the action is first
                if i == 0:
                    # everything else is the subject
                    return [
                        cls.create_command_variant(operation[0], [op_group_name] + operation[1:], suffix)
                    ]
                if i == len(operation) - 1:
                    # if it's last, the subject would be the first thing
                    return [
                        cls.create_command_variant(operation[i], [op_group_name] + operation[:i], suffix)
                    ]
                # otherwise          
                # things before are part of the subject
                # things after the verb should be part of the suffix
                return [
                    cls.create_command_variant(operation[i], [op_group_name] + operation[:i], suffix + operation[i+1:])
                ]
        
        # so couldn't tell what the action was.
        # fallback to the original behavior with a warning.
        logger.warning(f"Operation ${operation[0]}/${operation[1]} is inferred without finding action.")
        return [
            cls.create_command_variant(operation[0], [op_group_name] + operation[1:], suffix)
        ]

    @classmethod
    def create_command_variant(cls, action, subject, variant):
        verb = cls.get_powershell_verb(action)
        if verb == 'Invoke':
            # if the 'operation' name was  "post" -- it's kindof redundant.
            # so, only include the operation name in the group name if it's anything else
            if action.lower() != 'post':
                subject = [action] + subject
        subject = [cls.singular_noun(s) or s for s in subject]
        # remove duplicate values
        values = set()
        simplified_subject = []
        for s in subject:
            if s in values:
                continue
            values.add(s)
            simplified_subject.append(s)
        return {
            "subject": ''.join(simplified_subject),
            "verb": verb,
            "variant": ''.join(variant),
            "action": action,
        }

    @staticmethod
    def get_powershell_verb(action):
        action = action[0].upper() + action[1:].lower()
        return VERB_MAPPING.get(action, "Invoke")

    @classmethod
    def singular_noun(cls, noun):
        words = re.findall(r'[A-Z][a-z]*', noun)
        # singular the last word in operation group name
        w = cls._pluralizer.singular(words[-1].lower())
        words[-1] = w[0].upper() + w[1:]
        noun = ''.join(words)
        return noun


VERB_MAPPING = {
    "Access": "Get",
    "Acquire": "Get",
    "Activate": "Initialize",
    "Add": "Add",
    "Allocate": "New",
    "Analyze": "Test",
    "Append": "Add",
    "Apply": "Add",
    "Approve": "Approve",
    "Assert": "Assert",
    "Assign": "Set",
    "Associate": "Join",
    "Attach": "Add",
    "Authorize": "Grant",
    "Backup": "Backup",
    "Block": "Block",
    "Build": "Build",
    "Bypass": "Skip",
    "Cancel": "Stop",
    "Capture": "Export",
    "Cat": "Get",
    "Change": "Rename",
    "Check": "Test",
    "Checkpoint": "Checkpoint",
    "Clear": "Clear",
    "Clone": "Copy",
    "Close": "Close",
    "Combine": "Join",
    "Compare": "Compare",
    "Compile": "Build",
    "Complete": "Complete",
    "Compress": "Compress",
    "Concatenate": "Add",
    "Configure": "Set",
    "Confirm": "Confirm",
    "Connect": "Connect",
    "Convert": "Convert",
    "ConvertFrom": "ConvertFrom",
    "ConvertTo": "ConvertTo",
    "Copy": "Copy",
    "Create": "New",
    "Cut": "Remove",
    "Debug": "Debug",
    "Delete": "Remove",
    "Deny": "Deny",
    "Deploy": "Deploy",
    "Dir": "Get",
    "Disable": "Disable",
    "Discard": "Remove",
    "Disconnect": "Disconnect",
    "Discover": "Find",
    "Dismount": "Dismount",
    "Display": "Show",
    "Dispose": "Remove",
    "Dump": "Get",
    "Duplicate": "Copy",
    "Edit": "Edit",
    "Enable": "Enable",
    "End": "Stop",
    "Enter": "Enter",
    "Erase": "Clear",
    "Evaluate": "Test",
    "Examine": "Get",
    "Execute": "Invoke",
    "Exit": "Exit",
    "Expand": "Expand",
    "Export": "Export",
    "Failover": "Set",
    "Find": "Find",
    "Finish": "Complete",
    "Flush": "Clear",
    "ForceReboot": "Restart",
    "Format": "Format",
    "Generalize": "Reset",
    "Generate": "New",
    "Get": "Get",
    "Grant": "Grant",
    "Group": "Group",
    "Hide": "Hide",
    "Import": "Import",
    "Initialize": "Initialize",
    "Insert": "Add",
    "Install": "Install",
    "Into": "Enter",
    "Invoke": "Invoke",
    "Is": "Test",
    "Join": "Join",
    "Jump": "Skip",
    "Limit": "Limit",
    "List": "Get",
    "Load": "Import",
    "Locate": "Find",
    "Lock": "Lock",
    "Make": "New",
    "Measure": "Measure",
    "Merge": "Merge",
    "Migrate": "Move",
    "Mount": "Mount",
    "Move": "Move",
    "Name": "Move",
    "New": "New",
    "Notify": "Send",
    "Nullify": "Clear",
    "Obtain": "Get",
    "Open": "Open",
    "Optimize": "Optimize",
    "Out": "Out",
    "Patch": "Update",
    "Pause": "Suspend",
    "Perform": "Invoke",
    "Ping": "Ping",
    "Pop": "Pop",
    "Post": "Invoke",
    "Power": "Start",
    "PowerOff": "Stop",
    "PowerOn": "Start",
    "Produce": "Show",
    "Protect": "Protect",
    "Provision": "New",
    "Publish": "Publish",
    "Purge": "Clear",
    "Push": "Push",
    "Put": "Set",
    "Read": "Read",
    "Reassociate": "Move",
    "Reboot": "Restart",
    "Receive": "Receive",
    "Recover": "Restore",
    "Redo": "Redo",
    "Refresh": "Update",
    "Regenerate": "New",
    "Register": "Register",
    "Reimage": "Update",
    "Release": "Publish",
    "Remove": "Remove",
    "Rename": "Rename",
    "Repair": "Repair",
    "Replace": "Update",
    "Replicate": "Copy",
    "Reprocess": "Update",
    "Request": "Request",
    "Reset": "Reset",
    "Resize": "Resize",
    "Resolve": "Resolve",
    "Restart": "Restart",
    "Restore": "Restore",
    "Restrict": "Lock",
    "Resubmit": "Submit",
    "Resume": "Resume",
    "Retarget": "Update",
    "Retrieve": "Get",
    "Revoke": "Revoke",
    "Run": "Start",
    "Save": "Save",
    "Search": "Search",
    "Secure": "Lock",
    "Select": "Select",
    "Send": "Send",
    "Separate": "Split",
    "Set": "Set",
    "Show": "Show",
    "Shutdown": "Stop",
    "Skip": "Skip",
    "Split": "Split",
    "Start": "Start",
    "Step": "Step",
    "Stop": "Stop",
    "Submit": "Submit",
    "Suggest": "Get",
    "Suspend": "Suspend",
    "Swap": "Switch",
    "Switch": "Switch",
    "Sync": "Sync",
    "Synch": "Sync",
    "Synchronize": "Sync",
    "Test": "Test",
    "Trace": "Trace",
    "Transfer": "Move",
    "Trigger": "Start",
    "Type": "Get",
    "Unblock": "Unblock",
    "Undelete": "Restore",
    "Undo": "Undo",
    "Uninstall": "Uninstall",
    "Unite": "Join",
    "Unlock": "Unlock",
    "Unmark": "Clear",
    "Unprotect": "Unprotect",
    "Unpublish": "Unpublish",
    "Unregister": "Unregister",
    "Unrestrict": "Unlock",
    "Unsecure": "Unlock",
    "Unset": "Clear",
    "Update": "Update",
    "Upgrade": "Update",
    "Use": "Use",
    "Validate": "Test",
    "Verify": "Test",
    "Wait": "Wait",
    "Watch": "Watch",
    "Wipe": "Clear",
    "Write": "Write",
}
