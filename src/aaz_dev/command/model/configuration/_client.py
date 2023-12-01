import logging
import abc

from schematics.models import Model
from schematics.types import ModelType, ListType, StringType, UTCDateTimeType, PolyModelType
from schematics.types.serializable import serializable
from utils.fields import PlaneField, CloudField
from urllib.parse import urlparse
from utils import exceptions


from ._arg_group import CMDArgGroup
from ._utils import CMDArgBuildPrefix, CMDDiffLevelEnum
from ._arg_builder import CMDArgBuilder
from ._schema import CMDSchemaField, CMDStringSchema
from ._subresource_selector import CMDSubresourceSelector
from ._operation import CMDHttpOperation
from ._command import handle_duplicated_options
from ._resource import CMDResource


logger = logging.getLogger('backend')


class CMDClientAADAuthConfig(Model):
    scopes = ListType(StringType, required=True, min_size=1)

    class Options:
        serialize_when_none = False
    
    def reformat(self, **kwargs):
        # TODO: check scopes schema
        self.scopes = sorted(self.scopes)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if sorted(self.scopes) != sorted(old.scopes):
                diff['scopes'] = f"{old.scopes} != {self.scopes}"
        return diff


class CMDClientAuth(Model):
    aad = ModelType(
        CMDClientAADAuthConfig,
    )

    class Options:
        serialize_when_none = False
    
    def reformat(self, **kwargs):
        if self.aad:
            self.aad.reformat(**kwargs)
        else:
            raise exceptions.VerificationError('Invalid auth config', default='Client auth is not defined')

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if old.aad:
                if not self.aad:
                    diff['aad'] = f"miss aad auth now."
                else:
                    aad_diff = self.aad.diff(old.aad, level)
                    if aad_diff:
                        diff['aad'] = aad_diff

        if level >= CMDDiffLevelEnum.Structure:
            if self.aad:
                aad_diff = self.aad.diff(old.aad, level)
                if aad_diff:
                    diff['aad'] = aad_diff
        return diff


class _EndpointTemplateMixin:
    @staticmethod
    def _iter_placeholders(template):
        endpoint = urlparse(template).netloc
        while True:
            idx = 0
            required = True
            while idx < len(endpoint) and endpoint[idx] != '{':
                idx += 1
            endpoint = endpoint[idx + 1:]
            if not endpoint:
                # not found '{'
                return

            idx = 0
            while idx < len(endpoint) and endpoint[idx] != '}':
                idx += 1
            if idx >= len(endpoint):
                # not found '}'
                return
            placeholder = endpoint[:idx]
            endpoint = endpoint[idx+1:]

            yield placeholder, required

    @staticmethod
    def _reformat(template):
        parsed = urlparse(template)
        if parsed.path:
            if parsed.path == '/' and not parsed.params and not parsed.query and not parsed.fragment:
                return template.rstrip('/')
            else:
                raise exceptions.VerificationError('Invalid endpoints', details='"{}" contains path'.format(template))
        if not parsed.scheme or not parsed.netloc:
            raise exceptions.VerificationError('Invalid endpoints', details='"{}" has no schema or hostname'.format(template))

        return template


class CMDClientEndpointTemplate(Model, _EndpointTemplateMixin):

    cloud = CloudField(required=True)
    
    # https://{accountName}.{zone}.blob.storage.azure.net
    template = StringType(required=True)

    class Options:
        serialize_when_none = False

    def iter_placeholders(self):
        return self._iter_placeholders(self.template)

    def reformat(self, **kwargs):
        self.template = self._reformat(self.template)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.cloud != old.cloud:
                diff['cloud'] = f"{old.cloud} != {self.cloud}"
            if self.template != old.template:
                diff['template'] = f"{old.template} != {self.template}"
        return diff


class CMDClientEndpointCloudMetadataTemplate(Model, _EndpointTemplateMixin):

    selector_index = StringType(
        required=True,
        serialized_name="selectorIndex",
        deserialize_from="selectorIndex",
    )  # index, used to retrieve property in arm cloud metadata endpoints.
    prefix_template = StringType(
        serialized_name="prefixTemplate",
        deserialize_from="prefixTemplate",
    )  # prefix template, required for suffixes.

    class Options:
        serialize_when_none = False

    def iter_placeholders(self):
        if self.prefix_template is None:
            return
        for placeholder in self._iter_placeholders(self.prefix_template):
            yield placeholder

    def reformat(self, **kwargs):
        if self.prefix_template is None:
            return
        self.prefix_template = self._reformat(self.prefix_template)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.selector_index != old.selector_index:
                diff['selector_index'] = f"{old.selector_index} != {self.selector_index}"
            if self.prefix_template != old.prefix_template:
                diff['prefix_template'] = f"{old.prefix_template} != {self.prefix_template}"
        return diff


class CMDClientEndpoints(Model):
    # properties as tags
    TYPE_VALUE = None  # types: "template", "http-operation"

    class Options:
        serialize_when_none = False

    @serializable
    def type(self):
        return self._get_type()

    def _get_type(self):
        assert self.TYPE_VALUE is not None
        return self.TYPE_VALUE

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.TYPE_VALUE is None:
            return False

        if isinstance(data, dict):
            type_value = data.get('type', None)
            return type_value == cls.TYPE_VALUE
        elif isinstance(data, CMDClientEndpoints):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False

    @abc.abstractmethod
    def reformat(self, **kwargs):
        pass

    @abc.abstractmethod
    def prepare(self):
        pass

    @abc.abstractmethod
    def generate_args(self, ref_args):
        pass

    @abc.abstractmethod
    def diff(self, old, level):
        pass


class CMDClientEndpointsByTemplate(CMDClientEndpoints):
    TYPE_VALUE = 'template'

    templates = ListType(ModelType(CMDClientEndpointTemplate), required=True, min_size=1)
    cloud_metadata = ModelType(CMDClientEndpointCloudMetadataTemplate,
                               serialized_name="cloudMetadata",
                               deserialize_from="cloudMetadata")
    params = ListType(CMDSchemaField())

    def reformat(self, **kwargs):
        for template in self.templates:
            template.reformat(**kwargs)
        self.templates = sorted(self.templates, key=lambda e: e.cloud)
        if self.cloud_metadata:
            self.cloud_metadata.reformat(**kwargs)

        # make sure the placeholders across all the endpoints are consistent
        placeholders = {}
        for template in self.templates:
            for placeholder, required in template.iter_placeholders():
                if placeholder in placeholders:
                    placeholders[placeholder]['count'] += 1
                    if placeholders[placeholder]['required'] != required:
                        raise exceptions.VerificationError('Invalid endpoints', details='Inconsistent required for placeholder "{}"'.format(placeholder))
                else:
                    placeholders[placeholder] = {
                        "required": required,
                        "count": 1
                    }
        expected_count = len(self.templates)
        if self.cloud_metadata:
            for placeholder, required in self.cloud_metadata.iter_placeholders():
                if placeholder in placeholders:
                    placeholders[placeholder]['count'] += 1
                    if placeholders[placeholder]['required'] != required:
                        raise exceptions.VerificationError('Invalid endpoints', details='Inconsistent required for placeholder "{}" in endpoints or cloud metadata'.format(placeholder))
                else:
                    placeholders[placeholder] = {
                        "required": required,
                        "count": 1
                    }
            expected_count += 1
        for item in placeholders.values():
            if item['count'] != expected_count:
                raise exceptions.VerificationError('Invalid endpoints', details='placeholder "{}" is missed in some endpoints or cloud metadata'.format(placeholder))

        # make sure the parameters are consistent with the placeholders
        if self.params:
            for param in self.params:
                if param.name not in placeholders:
                    raise exceptions.VerificationError('Invalid endpoints', details='Unknown endpoint parameter: "{}"'.format(param.name))
                if param.required != placeholders[param.name]['required']:
                    raise exceptions.VerificationError('Invalid endpoints', details='Inconsistent required for parameter: "{}"'.format(param.name))
        if len(placeholders) > 0 and (not self.params or len(placeholders) != len(self.params)):
            raise exceptions.VerificationError('Invalid endpoints', details='Inconsistent endpoint templates and parameters')

        if self.params:
            self.params = sorted(self.params, key=lambda p: p.name)
    
    def prepare(self):
        params = {}
        for template in self.templates:
            for placeholder, required in template.iter_placeholders():
                if placeholder not in params:
                    params[placeholder] = CMDStringSchema({
                        "name": placeholder,
                        "required": required,
                        "skip_url_encoding": True,
                    })
        if self.cloud_metadata:
            for placeholder, required in self.cloud_metadata.iter_placeholders():
                if placeholder not in params:
                    params[placeholder] = CMDStringSchema({
                        "name": placeholder,
                        "required": required,
                        "skip_url_encoding": True,
                    })
        self.params = sorted(params.values(), key=lambda p: p.name) or None

    def generate_args(self, ref_args):
        args = []
        if self.params:
            for param in self.params:
                builder = CMDArgBuilder.new_builder(
                    schema=param,
                    var_prefix=CMDArgBuildPrefix.ClientEndpoint, ref_args=ref_args
                )
                args.extend(builder.get_args())
        return args

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.cloud_metadata) != (not old.cloud_metadata):
                diff['cloud_metadata'] = "Add cloud metadata" if self.cloud_metadata else "Remove cloud metadata"
            elif self.cloud_metadata:
                if cloud_metadata_diff := self.cloud_metadata.diff(old.cloud_metadata, level):
                    diff['cloud_metadata'] = cloud_metadata_diff

            if len(self.templates) != len(old.templates):
                diff['templates'] = "template not match"
            else:
                templates_diff = {}
                for template in self.templates:
                    peer_template = None
                    for old_template in old.templates:
                        if old_template.cloud == template.cloud:
                            peer_template = old_template
                            break
                    template_diff = template.diff(peer_template, level)
                    if template_diff:
                        templates_diff[template.cloud] = template_diff
                if templates_diff:
                    diff['templates'] = templates_diff
        return diff


class CMDClientEndpointsByHttpOperation(CMDClientEndpoints):
    TYPE_VALUE = 'http-operation'

    resource = ModelType(CMDResource, required=True)

    selector = PolyModelType(
        CMDSubresourceSelector,
        allow_subclasses=True,
        serialized_name="selector",
        deserialize_from="selector",
    )

    operation = ModelType(
        CMDHttpOperation,
        required=True,
        serialized_name="operation",
        deserialize_from="operation"
    )

    def reformat(self, **kwargs):
        self.selector.reformat(**kwargs)
        schema_cls_map = {}
        self.operation.reformat(schema_cls_map=schema_cls_map, **kwargs)
        for key, value in schema_cls_map.items():
            if value is None:
                raise exceptions.VerificationError(
                    message=f"ReformatError: Schema Class '{key}' not defined.",
                    details=None
                )

    def prepare(self):
        # TODO: remove unused schema based on selector
        pass

    def generate_args(self, ref_args):
        arguments = {}
        has_subresource = False
        if self.selector:
            has_subresource = True
            for arg in self.selector.generate_args(
                    ref_args=ref_args,
                    var_prefix=CMDArgBuildPrefix.ClientEndpoint
            ):
                if arg.var not in arguments:
                    arguments[arg.var] = arg

        for arg in self.operation.generate_args(
                ref_args=ref_args,
                has_subresource=has_subresource,
                var_prefix=CMDArgBuildPrefix.ClientEndpoint
        ):
            if arg.var not in arguments:
                arguments[arg.var] = arg

        return handle_duplicated_options(
            arguments, has_subresource=has_subresource, operation_id=self.operation.operation_id)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if resource_diff := self.resource.diff(old.resource, level):
            diff["resource"] = resource_diff
        if selector_diff := self.selector.diff(old.selector, level):
            diff["selector"] = selector_diff
        if operation_diff := self.operation.diff(old.operation, level):
            diff["operation"] = operation_diff
        return diff


class CMDClientConfig(Model):
    # this property is used to manage the client config version.
    version = UTCDateTimeType(required=True)

    plane = PlaneField(required=True)
    endpoints = PolyModelType(
        CMDClientEndpoints,
        allow_subclasses=True,
        required=True)

    auth = ModelType(CMDClientAuth, required=True)
    arg_group = ModelType(
        CMDArgGroup,
        serialized_name='argGroup',
        deserialize_from='argGroup',
    )

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        self.endpoints.reformat(**kwargs)
        self.auth.reformat(**kwargs)
        if self.arg_group:
            self.arg_group.reformat(**kwargs)

    def generate_args(self, ref_args=None, ref_options=None):
        if not ref_args:
            ref_args = []
            if self.arg_group:
                ref_args.extend(self.arg_group.args)
            ref_args = ref_args or None

        arguments = {}
        for arg in self.endpoints.generate_args(ref_args):
            if arg.var not in arguments:
                if ref_options and arg.var in ref_options:
                    # replace generated options by ref_options
                    arg.options = [*ref_options[arg.var]]
                arg.group = 'Client'
                arguments[arg.var] = arg

        # verify duplicated options
        used_args = set()
        for arg in arguments.values():
            used_args.add(arg.var)
            r_arg = None
            for v in arguments.values():
                if v.var in used_args:
                    continue
                if not set(arg.options).isdisjoint(v.options):
                    r_arg = v
                    break
            if r_arg:
                raise exceptions.VerificationError(
                    "Argument Options conflict",
                    details=f"Duplicated Option Value: {set(arg.options).intersection(r_arg.options)} : {arg.var} with {r_arg.var}"
                )

        if arguments:
            self.arg_group = CMDArgGroup({
                "name": 'Client',
            })
            self.arg_group.args = sorted(arguments.values(), key=lambda a: a.var)
        else:
            self.arg_group = None
