import logging

from schematics.models import Model
from schematics.types import ModelType, ListType, StringType, UTCDateTimeType
from utils.fields import PlaneField, CloudField
from urllib.parse import urlparse
from utils import exceptions


from ._arg_group import CMDArgGroup
from ._utils import CMDArgBuildPrefix, CMDDiffLevelEnum
from ._arg_builder import CMDArgBuilder
from ._schema import CMDSchemaField, CMDStringSchema

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


class CMDClientEndpointTemplate(Model):
    cloud = CloudField(required=True)
    
    # https://{accountName}.{zone}.blob.storage.azure.net
    template = StringType(required=True)

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        parsed = urlparse(self.template)
        if parsed.path:
            if parsed.path == '/' and not parsed.params and not parsed.query and not parsed.fragment:
                self.template = self.template.rstrip('/')
            else:
                raise exceptions.VerificationError('Invalid endpoints', details='"{}" contains path'.format(self.template))
        if not parsed.scheme or not parsed.netloc:
            raise exceptions.VerificationError('Invalid endpoints', details='"{}" has no schema or hostname'.format(self.template))
    
    def iter_placeholders(self):
        parsed = urlparse(self.template)
        return self._iter_placeholders(parsed.netloc)

    def _iter_placeholders(self, endpoint):
        while True:
            idx = 0
            required = True
            while idx < len(endpoint) and endpoint[idx] != '{':
                idx += 1
            endpoint = endpoint[idx+1:]
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


class CMDClientEndpoints(Model):

    templates = ListType(ModelType(CMDClientEndpointTemplate), required=True, min_size=1)
    params = ListType(CMDSchemaField())

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        for template in self.templates:
            template.reformat(**kwargs)
        self.templates = sorted(self.templates, key=lambda e: e.cloud)

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
        for item in placeholders.values():
            if item['count'] != len(self.templates):
                raise exceptions.VerificationError('Invalid endpoints', details='placeholder "{}" is missed in some endpoints'.format(placeholder))

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
    
    def generate_params(self):
        params = {}
        for template in self.templates:
            for placeholder, required in template.iter_placeholders():
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


class CMDClientConfig(Model):
     # this property is used to manage the client config version.
    version = UTCDateTimeType(required=True)

    plane = PlaneField(required=True)
    endpoints = ModelType(CMDClientEndpoints, required=True)

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
                "name": self.arg_group.name if self.arg_group else 'Client',
            })
            self.arg_group.args = sorted(arguments.values(), key=lambda a: a.var)
        else:
            self.arg_group = None
