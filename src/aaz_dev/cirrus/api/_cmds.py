import click
import logging
from flask import Blueprint
import sys
import os
import json

from protos import component_pb2, command_pb2, argument_pb2
from protos.plugin import model_pb2, resource_pb2, operation_pb2, output_pb2, selector_pb2, condition_pb2, http_pb2, schema_pb2
from google.protobuf.json_format import ParseDict, MessageToJson
from command.controller.specs_manager import AAZSpecsManager
from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('cirrus-cmds', __name__, url_prefix='/CIRRUS/CMDs', cli_group="cirrus")
bp.cli.short_help = "Generate aaz models as cirrus components."

@bp.cli.command("export-component", short_help="Export aaz models as a cirrus component.")
@click.option(
    "--aaz-path", '-a',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="The local path of aaz repo."
)
@click.option(
    "--output-path", '-o',
    required=True,
    help="The output path where the component will be exported."
)
@click.option(
    "--component-name", '--name',
    required=True,
    help="Name of the component"
)
def export_component(component_name, output_path):
    print(f"Using AAZ path: {Config.AAZ_PATH}")    
    
    specs_manager = AAZSpecsManager()
    module_name = component_name.lower()
    
    print(f"Exporting component: {module_name}")

    root_module = specs_manager.find_command_group(module_name)
    if root_module:
        # root_primitive = root_module.to_primitive()
        # os.makedirs(output_path, exist_ok=True)
        # root_module_file = os.path.join(output_path, f"{module_name}_root_module.json")
        # with open(root_module_file, 'w', encoding='utf-8') as f:
        #     json.dump(root_primitive, f, indent=2, ensure_ascii=False)
        # print(f"\nRoot module JSON saved to: {root_module_file}")

        proto_component = create_component_proto(root_module, component_name)
      
        os.makedirs(output_path, exist_ok=True)
        binary_file = os.path.join(output_path, f"{module_name}_1.pb")
        with open(binary_file, 'wb') as f:
            f.write(proto_component.SerializeToString())
        # Just for debugging, save as JSON
        json_file = os.path.join(output_path, f"{module_name}_1.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json_data = MessageToJson(
                proto_component, 
                preserving_proto_field_name=True,
                sort_keys=True,
                indent=2
            )
            f.write(json_data)
        
        print(f"Component protobuf saved to: {binary_file}")
        print(f"Component JSON saved to: {json_file}")
    else:
        print(f"Module '{module_name}' not found in AAZ repository")


def get_latest_version_from_module(specs_manager, root_module):
    all_versions = set()
    
    if hasattr(root_module, 'names') and root_module.names:
        names = root_module.names[1:] if root_module.names[0] == 'aaz' else root_module.names
    else:
        names = []
    
    for command in specs_manager.iter_commands(*names):
        if hasattr(command, 'versions') and command.versions:
            for version in command.versions:
                all_versions.add(version.name)
    
    if not all_versions:
        return None
    
    class MockVersion:
        def __init__(self, name):
            self.name = name
    
    sorted_versions = sorted(all_versions, reverse=True)
    return MockVersion(sorted_versions[0])


def create_component_proto(root_module, component_name):
    specs_manager = AAZSpecsManager()
    component_version = get_latest_version_from_module(specs_manager, root_module)
    version_str = component_version.name if component_version else "1.0.0"

    proto_component = component_pb2.CrsPluginComponent()
    proto_component.metadata.name = component_name
    component_uri = f"crs://azure/{component_name}"
    proto_component.metadata.version = version_str
    proto_component.metadata.uri = component_uri
    if root_module.help:
        proto_component.metadata.help.CopyFrom(convert_aaz_help_to_proto(root_module.help))
    
    proto_group = convert_aaz_command_group_to_proto(root_module, component_version)
    proto_component.interface.command_group.CopyFrom(proto_group)
    
    return proto_component

def convert_aaz_help_to_proto(aaz_help):
    proto_help = command_pb2.CrsHelp()
    if aaz_help.get('short'):
        proto_help.short = aaz_help.get('short')
    if aaz_help.get('lines'):
        proto_help.long = "\n".join(aaz_help.get('lines'))
    return proto_help

def convert_aaz_arg_help_to_proto(aaz_help):
    proto_help = argument_pb2.CrsArgHelp()
    if aaz_help.get('short'):
        proto_help.short = aaz_help.get('short')
    if aaz_help.get('lines'):
        proto_help.long = "\n".join(aaz_help.get('lines'))
    return proto_help

def convert_aaz_command_group_to_proto(aaz_group, component_version):
    proto_group = command_pb2.CrsCommandGroup()
    proto_group.name = " ".join(aaz_group.names) if aaz_group.names else ""
    proto_group.uri = f"crs://azure/{'/'.join(aaz_group.names)}" if aaz_group.names else "crs://azure/"
    
    if aaz_group.help:
        proto_group.help.CopyFrom(convert_aaz_help_to_proto(aaz_group.help))
    
    if hasattr(aaz_group, 'command_groups') and aaz_group.command_groups:
        for group_name, subgroup in aaz_group.command_groups.items():
            if has_version_in_group(subgroup, component_version):
                proto_subgroup = convert_aaz_command_group_to_proto(subgroup, component_version)
                proto_group.groups.append(proto_subgroup)
    
    if hasattr(aaz_group, 'commands') and aaz_group.commands:
        for cmd_name, command in aaz_group.commands.items():
            if has_command_version(command, component_version):
                proto_command = convert_aaz_command_to_proto(command, component_version)
                proto_group.commands.append(proto_command)
    
    return proto_group

def convert_aaz_resource_to_proto(aaz_resource):
    proto_resource = resource_pb2.CrsRestResource()
    proto_resource.id = getattr(aaz_resource, 'id', '')
    proto_resource.version = getattr(aaz_resource, 'version', '')
    proto_resource.plane = getattr(aaz_resource, 'plane', '')
    if hasattr(aaz_resource, 'subresource') and aaz_resource.subresource:
        proto_resource.subresource = aaz_resource.subresource
    return proto_resource

def convert_aaz_command_to_proto(aaz_command, component_version):
    proto_command = command_pb2.CrsCommand()
    proto_command.name = " ".join(aaz_command.names) if aaz_command.names else ""
    proto_command.uri = f"crs://azure/{'/'.join(aaz_command.names)}" if aaz_command.names else "crs://azure/"
    
    target_version = None
    if aaz_command.versions:
        for version in aaz_command.versions:
            if version.name == component_version.name:
                target_version = version
                break
    
    if target_version:
        proto_command.version = target_version.name

        specs_manager = AAZSpecsManager()
        cfg_reader = specs_manager.load_resource_cfg_reader_by_command_with_version(
            aaz_command, version=target_version)
        
        if cfg_reader:
            cmd_cfg = cfg_reader.find_command(*aaz_command.names)
            
            if cmd_cfg:
                result = cmd_cfg.to_primitive()
                
                # # Debug: save the complete command 
                # cfg_file = f"{'_'.join(aaz_command.names)}_cmd.json"
                # cfg_dir = os.path.dirname('C:\\Users\\shiyingchen\\aaz-cirrus\\devcenter\\')
                # if not os.path.exists(cfg_dir):
                #     os.makedirs(cfg_dir)
                # cfg_file = os.path.join(cfg_dir, cfg_file)
                # with open(cfg_file, 'w', encoding='utf-8') as f:
                #     json.dump(result, f, indent=2, ensure_ascii=False)
                # print(f"Command configuration saved to: {cfg_file}")
                
                
                if result.get('help'):
                    help_data = result['help']
                    proto_command.help.CopyFrom(convert_aaz_help_to_proto(help_data))
                
                if result.get('confirmation'):
                    proto_command.confirmation = result['confirmation']
                
                if result.get('argGroups'):
                    for aaz_arggrp in result['argGroups']:
                        arg_group_name = aaz_arggrp.get('name', '')
                        if aaz_arggrp.get('args'):
                            for aaz_arg in aaz_arggrp['args']:
                                    proto_arg = convert_aaz_arg_to_proto(arg_group_name, aaz_arg)
                                    proto_command.args.append(proto_arg)
                
                # Convert positional args
                if result.get('positional_args'):
                    proto_command.positional_args.extend(result['positional_args'])
                
                # Create plugin model command
                plugin_model = model_pb2.CrsPluginModelCommand()
                
                # Add resources from the target_version (not from result)
                if hasattr(target_version, 'resources') and target_version.resources:
                    for aaz_resource in target_version.resources:
                        proto_resource = convert_aaz_resource_to_proto(aaz_resource)
                        plugin_model.resources.append(proto_resource)
                
                # Add operations from result
                if result.get('operations'):
                    for aaz_operation_data in result['operations']:
                        proto_operation = convert_aaz_operation_to_proto(aaz_operation_data)
                        plugin_model.operations.append(proto_operation)
                
                # Add outputs from result
                if result.get('outputs'):
                    for aaz_output_data in result['outputs']:
                        proto_output = convert_aaz_output_to_proto(aaz_output_data)
                        plugin_model.outputs.append(proto_output)
                
                # Add conditions from result
                if result.get('conditions'):
                    for aaz_condition_data in result['conditions']:
                        proto_condition = convert_aaz_condition_to_proto(aaz_condition_data)
                        plugin_model.conditions.append(proto_condition)
                
                # Add selector from result
                if result.get('selector'):
                    proto_selector = convert_aaz_selector_to_proto(result['selector'])
                    plugin_model.subresource_selector.CopyFrom(proto_selector)
                
                proto_command.model.CopyFrom(plugin_model)
    
    return proto_command

def has_command_version(command, target_version):
    target_version_name = target_version.name if hasattr(target_version, 'name') else target_version
    if hasattr(command, 'versions') and command.versions:
        for version in command.versions:
            if version.name == target_version_name:
                return True
    return False

def has_version_in_group(group, target_version):
    if hasattr(group, 'commands') and group.commands:
        for cmd_name, command in group.commands.items():
            if has_command_version(command, target_version):
                return True
    if hasattr(group, 'command_groups') and group.command_groups:
        for group_name, subgroup in group.command_groups.items():
            if has_version_in_group(subgroup, target_version):
                return True
    return False

def convert_aaz_arg_to_proto(aaz_arg_group_name, aaz_arg):
    proto_arg = argument_pb2.CrsArg()
    
    proto_arg.var_name = aaz_arg.get('var', '')
    proto_arg.name = aaz_arg.get('idPart', '')
    
    if aaz_arg.get('options'):
        proto_arg.options.extend(aaz_arg['options'])
    
    proto_arg.group = aaz_arg_group_name
    proto_arg.internal = aaz_arg.get('internal', False)
    proto_arg.required = aaz_arg.get('required', False)
    proto_arg.nullable = aaz_arg.get('nullable', False)
    
    if aaz_arg.get('help'):
        proto_arg.help.CopyFrom(convert_aaz_arg_help_to_proto(aaz_arg['help']))
    
    if aaz_arg.get('blank'):
        proto_arg.blank.value = aaz_arg['blank']
    
    if aaz_arg.get('default'):
        proto_arg.default.value = aaz_arg['default']

    if aaz_arg.get('prompt'):
        proto_arg.prompt.prompt = aaz_arg['prompt']['msg']

    # # Seems like no secret or confirm in AAZ args, commented out for now
    # if aaz_arg.get('secret'):
    #     proto_arg.prompt.secret = aaz_arg['prompt']['secret']
    # if aaz_arg.get('confirm'):
    #     proto_arg.prompt.confirm = aaz_arg['prompt']['confirmation']
    
    arg_type = aaz_arg.get('type', None)

    if arg_type == 'string':
        string_arg = argument_pb2.CrsStringArg()

        format_type = aaz_arg.get('format', None)
        if format_type:
            str_format = argument_pb2.CrsStringFormat()
            if aaz_arg.get('pattern'):
                str_format.pattern = aaz_arg.get('pattern')
            if aaz_arg.get('max_length') is not None:
                str_format.max_length = aaz_arg.get('maxLength')
            if aaz_arg.get('min_length') is not None:
                str_format.min_length = aaz_arg.get('minLength')
            string_arg.string.format.string.CopyFrom(str_format)
        
        if aaz_arg.get('enum'):
            enum_items = aaz_arg.get('enum')
            if isinstance(enum_items, list):
                for item in enum_items:
                    enum_item = string_arg.enum.items.add()
                    enum_item.name = item.get('name', '')
                    enum_item.value = item.get('value', '')
                    enum_item.internal = item.get('internal', False)
            
            string_arg.enum.support_extension = aaz_arg.get('supportExtension', False)
            # Not found 'caseSensitive' in aaz
            string_arg.enum.case_sensitive = aaz_arg.get('caseSensitive', False)
        
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'binary':
        string_arg = argument_pb2.CrsStringArg()
        binary_format = argument_pb2.CrsBinaryFormat()
        string_arg.binary.CopyFrom(binary_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'byte':
        string_arg = argument_pb2.CrsStringArg()
        byte_format = argument_pb2.CrsByteFormat()
        string_arg.byte.CopyFrom(byte_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'duration':
        string_arg = argument_pb2.CrsStringArg()
        duration_format = argument_pb2.CrsDurationFormat()
        if aaz_arg.get('protocol'):
            duration_format.protocol = aaz_arg['protocol']
        string_arg.duration.CopyFrom(duration_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'date':
        string_arg = argument_pb2.CrsStringArg()
        date_format = argument_pb2.CrsDateFormat()
        if aaz_arg.get('protocol'):
            date_format.protocol = aaz_arg['protocol']
        string_arg.date.CopyFrom(date_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'dateTime':
        string_arg = argument_pb2.CrsStringArg()
        datetime_format = argument_pb2.CrsDateTimeFormat()
        if aaz_arg.get('protocol'):
            datetime_format.protocol = aaz_arg['protocol']
        string_arg.date_time.CopyFrom(datetime_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'time':
        string_arg = argument_pb2.CrsStringArg()
        time_format = argument_pb2.CrsTimeFormat()
        if aaz_arg.get('protocol'):
            time_format.protocol = aaz_arg['protocol']
        string_arg.time.CopyFrom(time_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'uuid':
        string_arg = argument_pb2.CrsStringArg()
        uuid_format = argument_pb2.CrsUuidFormat()
        string_arg.uuid.CopyFrom(uuid_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'password':
        string_arg = argument_pb2.CrsStringArg()
        string_arg.password.CopyFrom(argument_pb2.CrsPasswordFormat())
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'SubscriptionId':
        string_arg = argument_pb2.CrsStringArg()
        string_arg.subscription_id.CopyFrom(argument_pb2.CrsSubscriptionIdFormat())
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'ResourceGroupName':
        string_arg = argument_pb2.CrsStringArg()
        string_arg.resource_group_name.CopyFrom(argument_pb2.CrsResourceGroupNameFormat())
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'ResourceId':
        string_arg = argument_pb2.CrsStringArg()
        resource_id_format = argument_pb2.CrsResourceIdFormat()
        if aaz_arg.get('template'):
            templates = aaz_arg.get('template')
            if isinstance(templates, list):
                resource_id_format.templates.extend(templates)
            else:
                resource_id_format.templates.append(templates)
        string_arg.resource_id.CopyFrom(resource_id_format)
        proto_arg.string.CopyFrom(string_arg)

    elif arg_type == 'ResourceLocation':
        string_arg = argument_pb2.CrsStringArg()
        location_format = argument_pb2.CrsResourceLocationFormat()
        # Not found 'noRgDefault' in aaz
        location_format.no_rg_default = aaz_arg.get('noRgDefault', False) 
        string_arg.resource_location.CopyFrom(location_format)
        proto_arg.string.CopyFrom(string_arg)
        
    elif arg_type == 'boolean':
        boolean_arg = argument_pb2.CrsBooleanArg()
        # Not found 'reverse_options' in aaz
        if aaz_arg.get('reverseOptions'):
            boolean_arg.reverse_options.extend(aaz_arg.get('reverseOptions'))
        proto_arg.boolean.CopyFrom(boolean_arg)
        
    elif arg_type in ['integer', 'integer32', 'integer64', 'float', 'float32', 'float64', 'double']:
        number_arg = argument_pb2.CrsNumberArg()
        number_arg.enum.CopyFrom(argument_pb2.CrsArgEnum())
        if aaz_arg.get('enum'):
            enum_items = aaz_arg.get('enum')
            if isinstance(enum_items, list):
                for item in enum_items:
                    enum_item = number_arg.enum.items.add()
                    enum_item.name = item.get('name', '')
                    enum_item.value = item.get('value', '')
                    enum_item.internal = item.get('internal', False)
            number_arg.enum.support_extension = aaz_arg.get('supportExtension', False)
            number_arg.enum.case_sensitive = aaz_arg.get('caseSensitive', False)
        
        if arg_type == 'integer' or arg_type == 'integer32': 
            number_arg.format.CopyFrom(argument_pb2.CrsInt32Format())
            if aaz_arg.get('minimum'):
                number_arg.format.minimum = aaz_arg.get('minimum')
            if aaz_arg.get('maximum'):
                number_arg.format.maximum = aaz_arg.get('maximum')
            if aaz_arg.get('multipleOf'):
                number_arg.format.multiple_of = aaz_arg.get('multipleOf')
            
        elif  arg_type == 'integer64':
            number_arg.format.CopyFrom(argument_pb2.CrsInt64Format())
            if aaz_arg.get('minimum'):
                number_arg.format.minimum = aaz_arg.get('minimum')
            if aaz_arg.get('maximum'):
                number_arg.format.maximum = aaz_arg.get('maximum')
            if aaz_arg.get('multipleOf'):
                number_arg.format.multiple_of = aaz_arg.get('multipleOf')

        elif arg_type == 'float' or arg_type == 'float32':
            number_arg.format.CopyFrom(argument_pb2.CrsFloatFormat())
            if aaz_arg.get('minimum'):
                number_arg.format.minimum = aaz_arg.get('minimum')
            if aaz_arg.get('maximum'):
                number_arg.format.maximum = aaz_arg.get('maximum')
            if aaz_arg.get('multipleOf'):
                number_arg.format.multiple_of = aaz_arg.get('multipleOf')
            if aaz_arg.get('exclusiveMinimum'):
                number_arg.format.exclusive_minimum = aaz_arg.get('exclusiveMinimum')
            if aaz_arg.get('exclusiveMaximum'):
                number_arg.format.exclusive_maximum = aaz_arg.get('exclusiveMaximum')
        
        elif arg_type == 'float64' or arg_type == 'double':
            number_arg.format.CopyFrom(argument_pb2.CrsDoubleFormat())
            if aaz_arg.get('minimum'):
                number_arg.format.minimum = aaz_arg.get('minimum')
            if aaz_arg.get('maximum'):
                number_arg.format.maximum = aaz_arg.get('maximum')
            if aaz_arg.get('multipleOf'):
                number_arg.format.multiple_of = aaz_arg.get('multipleOf')
            if aaz_arg.get('exclusiveMinimum'):
                number_arg.format.exclusive_minimum = aaz_arg.get('exclusiveMinimum')
            if aaz_arg.get('exclusiveMaximum'):
                number_arg.format.exclusive_maximum = aaz_arg.get('exclusiveMaximum')
            

        proto_arg.number.CopyFrom(number_arg)

        
    elif arg_type == 'object':
        object_arg = argument_pb2.CrsObjectArg()
        
        if aaz_arg.get('cls_type'):
            object_arg.cls_type = aaz_arg.get('cls_type')
        
        object_format = argument_pb2.CrsObjectFormat()
        if aaz_arg.get('minLength') is not None:
            object_format.min_length = aaz_arg.get('minLength')
        if aaz_arg.get('maxLength') is not None:
            object_format.max_length = aaz_arg.get('maxLength')
        object_arg.format.CopyFrom(object_format)
        
        if aaz_arg.get('props'):
            props = aaz_arg.get('props')
            for prop in props:
                prop = object_arg.props.add()
                prop.CopyFrom(convert_aaz_arg_to_proto(aaz_arg_group_name, prop))
        
        if aaz_arg.get('additionalProps'):
            aaz_additional_props  = aaz_arg.get('additionalProps')
            additional_props = argument_pb2.CrsObjectArgAdditionalProperties()

            additional_props.item.CopyFrom(convert_aaz_arg_to_proto(
                aaz_arg.get('additional_properties'), 
                aaz_additional_props.get('item')
            ))
            object_arg.additional_props.CopyFrom(additional_props)
        
        proto_arg.object.CopyFrom(object_arg)
        
    elif arg_type == 'array':
        array_arg = argument_pb2.CrsArrayArg()
        
        # Set class type if available
        if aaz_arg.get('cls_type'):
            array_arg.cls_type = aaz_arg.get('cls_type')
        
        # Set format if available
        array_format = argument_pb2.CrsArrayFormat()
        array_format.unique = aaz_arg.get('unique', False)
        if aaz_arg.get('min_length') is not None:
            array_format.min_length = aaz_arg.get('min_length')
        if aaz_arg.get('max_length') is not None:
            array_format.max_length = aaz_arg.get('max_length')
        array_arg.format.CopyFrom(array_format)
        
        # Set item if available
        if aaz_arg.get('item'):
            item_group_name = f"{aaz_arg_group_name}.item" if aaz_arg_group_name else "item"
            array_arg.item.CopyFrom(convert_aaz_arg_to_proto(aaz_arg.get('item'), item_group_name))
        
        proto_arg.array.CopyFrom(array_arg)
        
    elif arg_type == 'cls':
        cls_arg = argument_pb2.CrsClsArg()
        cls_arg.cls_type = aaz_arg.get('cls_type', '')
        proto_arg.cls.CopyFrom(cls_arg)
        
    else:
        proto_arg.any_type.CopyFrom(argument_pb2.CrsAnyTypeArg())
    
    return proto_arg

def convert_aaz_operation_to_proto(aaz_operation_data):
    """Convert AAZ operation from primitive data to CRS protobuf operation"""
    proto_operation = operation_pb2.CrsOperation()
    
    # Add conditions if present
    if aaz_operation_data.get('when'):
        conditions = aaz_operation_data['when']
        if isinstance(conditions, list):
            proto_operation.conditions.extend(conditions)
        elif isinstance(conditions, str):
            proto_operation.conditions.append(conditions)
    
    # Handle different operation types
    if aaz_operation_data.get('http'):
        http_op = operation_pb2.CrsHttpOperation()
        http_data = aaz_operation_data['http']
        http_op.operation_id = http_data.get('operation_id', '')
        
        # Convert HTTP action
        if http_data.get('action'):
            http_action = convert_aaz_http_action_to_proto(http_data['action'])
            http_op.action.CopyFrom(http_action)
        
        proto_operation.http.CopyFrom(http_op)
    elif aaz_operation_data.get('instance_create'):
        # Handle instance create operations
        instance_op = operation_pb2.CrsInstanceOperation()
        instance_op.type = operation_pb2.CrsInstanceOperation.CREATE
        proto_operation.instance.CopyFrom(instance_op)
    elif aaz_operation_data.get('instance_update'):
        # Handle instance update operations
        instance_op = operation_pb2.CrsInstanceOperation()
        instance_op.type = operation_pb2.CrsInstanceOperation.UPDATE
        proto_operation.instance.CopyFrom(instance_op)
    elif aaz_operation_data.get('instance_delete'):
        # Handle instance delete operations
        instance_op = operation_pb2.CrsInstanceOperation()
        instance_op.type = operation_pb2.CrsInstanceOperation.DELETE
        proto_operation.instance.CopyFrom(instance_op)
    
    return proto_operation

def convert_aaz_http_action_to_proto(aaz_action_data):
    """Convert AAZ HTTP action from primitive data to CRS protobuf HTTP action"""
    proto_action = http_pb2.CrsHttpAction()
    
    proto_action.path = aaz_action_data.get('path', '')
    
    # Convert request
    if aaz_action_data.get('request'):
        proto_request = convert_aaz_http_request_to_proto(aaz_action_data['request'])
        proto_action.request.CopyFrom(proto_request)
    
    # Convert responses
    if aaz_action_data.get('responses'):
        for response_data in aaz_action_data['responses']:
            proto_response = convert_aaz_http_response_to_proto(response_data)
            proto_action.responses.append(proto_response)
    
    return proto_action

def convert_aaz_http_request_to_proto(aaz_request_data):
    """Convert AAZ HTTP request from primitive data to CRS protobuf HTTP request"""
    proto_request = http_pb2.CrsHttpRequest()
    
    # Map method
    method_map = {
        'GET': http_pb2.CrsHttpRequest.GET,
        'POST': http_pb2.CrsHttpRequest.POST,
        'PUT': http_pb2.CrsHttpRequest.PUT,
        'DELETE': http_pb2.CrsHttpRequest.DELETE,
        'PATCH': http_pb2.CrsHttpRequest.PATCH,
        'HEAD': http_pb2.CrsHttpRequest.HEAD,
        'OPTIONS': http_pb2.CrsHttpRequest.OPTIONS,
    }
    
    method = aaz_request_data.get('method', 'GET')
    proto_request.method = method_map.get(method.upper(), http_pb2.CrsHttpRequest.GET)
    
    # Handle additional request properties if they exist
    if aaz_request_data.get('path'):
        # Store path info if needed by the protobuf schema
        pass
    
    if aaz_request_data.get('query'):
        # Handle query parameters if supported
        pass
    
    if aaz_request_data.get('header'):
        # Handle headers if supported
        pass
    
    if aaz_request_data.get('body'):
        # Handle request body if supported
        pass
    
    return proto_request

def convert_aaz_http_response_to_proto(aaz_response_data):
    """Convert AAZ HTTP response from primitive data to CRS protobuf HTTP response"""
    proto_response = http_pb2.CrsHttpResponse()
    
    if aaz_response_data.get('status_codes'):
        status_codes = aaz_response_data['status_codes']
        if isinstance(status_codes, list):
            proto_response.status_codes.extend(status_codes)
        elif isinstance(status_codes, (int, str)):
            proto_response.status_codes.append(int(status_codes))
    
    proto_response.is_error = aaz_response_data.get('is_error', False)
    
    # Handle additional response properties if they exist
    if aaz_response_data.get('description'):
        # Store description if supported by protobuf schema
        pass
    
    if aaz_response_data.get('headers'):
        # Handle response headers if supported
        pass
    
    if aaz_response_data.get('body'):
        # Handle response body schema if supported
        pass
    
    return proto_response

def convert_aaz_output_to_proto(aaz_output_data):
    """Convert AAZ output from primitive data to CRS protobuf output"""
    proto_output = output_pb2.CrsOutput()
    
    if aaz_output_data.get('object'):
        obj_data = aaz_output_data['object']
        obj_output = output_pb2.CrsObjectOutput()
        obj_output.ref = obj_data.get('ref', '')
        obj_output.client_flatten = obj_data.get('client_flatten', False)
        proto_output.object.CopyFrom(obj_output)
    elif aaz_output_data.get('array'):
        array_data = aaz_output_data['array']
        array_output = output_pb2.CrsArrayOutput()
        array_output.ref = array_data.get('ref', '')
        array_output.client_flatten = array_data.get('client_flatten', False)
        if array_data.get('next_link'):
            array_output.next_link = array_data['next_link']
        proto_output.array.CopyFrom(array_output)
    elif aaz_output_data.get('string'):
        string_data = aaz_output_data['string']
        string_output = output_pb2.CrsStringOutput()
        if string_data.get('ref'):
            string_output.ref = string_data['ref']
        elif string_data.get('value'):
            string_output.value = string_data['value']
        proto_output.string.CopyFrom(string_output)
    elif aaz_output_data.get('number') or aaz_output_data.get('integer') or aaz_output_data.get('float'):
        # Handle number outputs
        number_data = aaz_output_data.get('number') or aaz_output_data.get('integer') or aaz_output_data.get('float')
        number_output = output_pb2.CrsNumberOutput()
        if isinstance(number_data, dict):
            if number_data.get('ref'):
                number_output.ref = number_data['ref']
            elif number_data.get('value') is not None:
                number_output.value = str(number_data['value'])
        proto_output.number.CopyFrom(number_output)
    elif aaz_output_data.get('boolean'):
        # Handle boolean outputs
        bool_data = aaz_output_data['boolean']
        bool_output = output_pb2.CrsBooleanOutput()
        if isinstance(bool_data, dict):
            if bool_data.get('ref'):
                bool_output.ref = bool_data['ref']
            elif bool_data.get('value') is not None:
                bool_output.value = bool(bool_data['value'])
        proto_output.boolean.CopyFrom(bool_output)
    else:
        # Try to determine type from type field
        output_type = aaz_output_data.get('type', 'object')
        if output_type == 'object':
            obj_output = output_pb2.CrsObjectOutput()
            obj_output.ref = aaz_output_data.get('ref', '')
            obj_output.client_flatten = aaz_output_data.get('client_flatten', False)
            proto_output.object.CopyFrom(obj_output)
        elif output_type == 'array':
            array_output = output_pb2.CrsArrayOutput()
            array_output.ref = aaz_output_data.get('ref', '')
            array_output.client_flatten = aaz_output_data.get('client_flatten', False)
            if aaz_output_data.get('next_link'):
                array_output.next_link = aaz_output_data['next_link']
            proto_output.array.CopyFrom(array_output)
        elif output_type == 'string':
            string_output = output_pb2.CrsStringOutput()
            string_output.ref = aaz_output_data.get('ref', '')
            proto_output.string.CopyFrom(string_output)
        else:
            # Default to object output
            obj_output = output_pb2.CrsObjectOutput()
            obj_output.ref = aaz_output_data.get('ref', '')
            obj_output.client_flatten = aaz_output_data.get('client_flatten', False)
            proto_output.object.CopyFrom(obj_output)
    
    return proto_output

def convert_aaz_condition_to_proto(aaz_condition_data):
    """Convert AAZ condition from primitive data to CRS protobuf condition"""
    proto_condition = condition_pb2.CrsCondition()
    
    proto_condition.var = aaz_condition_data.get('var', '')
    
    # Handle condition operators based on the actual structure
    if aaz_condition_data.get('has_value'):
        has_value_data = aaz_condition_data['has_value']
        has_value_op = condition_pb2.CrsConditionHasValueOperator()
        if isinstance(has_value_data, dict):
            has_value_op.arg = has_value_data.get('arg', '')
        elif isinstance(has_value_data, str):
            has_value_op.arg = has_value_data
        proto_condition.operator.has_value.CopyFrom(has_value_op)
    elif aaz_condition_data.get('equals'):
        equals_data = aaz_condition_data['equals']
        equals_op = condition_pb2.CrsConditionEqualsOperator()
        if isinstance(equals_data, dict):
            equals_op.arg = equals_data.get('arg', '')
            equals_op.value = str(equals_data.get('value', ''))
        proto_condition.operator.equals.CopyFrom(equals_op)
    elif aaz_condition_data.get('not'):
        # Handle NOT conditions
        not_data = aaz_condition_data['not']
        not_op = condition_pb2.CrsConditionNotOperator()
        if isinstance(not_data, dict):
            # Recursively convert the nested condition
            nested_condition = convert_aaz_condition_to_proto(not_data)
            not_op.condition.CopyFrom(nested_condition)
        # Use getattr to avoid Python keyword conflict
        getattr(proto_condition.operator, 'not').CopyFrom(not_op)
    elif aaz_condition_data.get('and'):
        # Handle AND conditions
        and_data = aaz_condition_data['and']
        and_op = condition_pb2.CrsConditionAndOperator()
        if isinstance(and_data, list):
            for sub_condition_data in and_data:
                sub_condition = convert_aaz_condition_to_proto(sub_condition_data)
                and_op.conditions.append(sub_condition)
        # Use getattr to avoid Python keyword conflict
        getattr(proto_condition.operator, 'and').CopyFrom(and_op)
    elif aaz_condition_data.get('or'):
        # Handle OR conditions
        or_data = aaz_condition_data['or']
        or_op = condition_pb2.CrsConditionOrOperator()
        if isinstance(or_data, list):
            for sub_condition_data in or_data:
                sub_condition = convert_aaz_condition_to_proto(sub_condition_data)
                or_op.conditions.append(sub_condition)
        # Use getattr to avoid Python keyword conflict
        getattr(proto_condition.operator, 'or').CopyFrom(or_op)
    else:
        # Default to has_value if no specific operator is found
        has_value_op = condition_pb2.CrsConditionHasValueOperator()
        has_value_op.arg = aaz_condition_data.get('arg', '')
        proto_condition.operator.has_value.CopyFrom(has_value_op)
    
    return proto_condition

def convert_aaz_selector_to_proto(aaz_selector_data):
    """Convert AAZ selector from primitive data to CRS protobuf selector"""
    proto_selector = selector_pb2.CrsSubresourceSelector()
    
    proto_selector.var = aaz_selector_data.get('var', '')
    proto_selector.ref = aaz_selector_data.get('ref', '')
    
    # Handle selector index - simplified version
    if aaz_selector_data.get('json'):
        selector_index = selector_pb2.CrsSelectorIndex()
        # Add appropriate conversion logic here based on your needs
        proto_selector.json.CopyFrom(selector_index)
    
    return proto_selector
