

from schematics.models import Model
from schematics.types import ModelType, DictType, StringType, ListType


class PSModuleConfig(Model):
    name = StringType(required=True)
    folder = StringType(required=True)
    repo = StringType(required=True)    # swagger repo path, https://github.com/Azure/<repo_name>/tree/<commit> or $(this-folder)/../../../<repo_name>
    # swagger = StringType(required=True) # swagger resource provider, <plane>/<path:mod_names>/ResourceProviders/<rp_name>

    # use tag or input files to select the swagger apis
    tag = StringType() # if the tag selected, the input_files will be ignored
    input_files = ListType(
        StringType(),
        serialized_name='inputFiles',
        deserialize_from='inputFiles',
    )  # The input file should not contain $(repo) and can be directly appended to the repo

    title = StringType(required=True) # the required value for the autorest configuration
    service_name = StringType(
        required=True,
        serialized_name='serviceName',
        deserialize_from='serviceName',
    )  # by default calculated from the title with this implementation https://github.com/Azure/autorest.powershell/blob/main/powershell/plugins/plugin-tweak-model.ts#L25-L33

    # those default value defined in the noprofile.md configuration https://github.com/Azure/azure-powershell/blob/generation/src/readme.azure.noprofile.md
    module_name = StringType(
        required=True,
        serialized_name='moduleName',
        deserialize_from='moduleName',
        default='$(prefix).$(service-name)'
    )  # by default $(prefix).$(service-name)
    namespace = StringType(
        required=True,
        default='Microsoft.Azure.PowerShell.Cmdlets.$(service-name)'
    )  # used for sub module to define the powershell class namespace, by default Microsoft.Azure.PowerShell.Cmdlets.$(service-name)
    subject_prefix = StringType(
        required=True,
        serialized_name='subjectPrefix',
        deserialize_from='subjectPrefix',
        default='$(service-name)'
    )  # the default value $(service-name)
    # root_module_name = StringType()   # used for sub module to generate the code in root module if there are multiple sub modules

    prefix = StringType(
        default='Az',
    )  # Not allowed to change

    class Options:
        serialize_when_none = False

    # swagger related properties

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rps = []

    @property
    def repo_name(self):
        return self.repo.split('/tree/', 1)[0].split('/')[-1]
    
    @property
    def commit(self):
        parts = self.repo.split('/tree/', 1)
        if len(parts) == 2:
            return parts[1].split('/')[0]
        return None
    
    # @property
    # def plane(self):
    #     return self.swagger.split('/')[0]

    # @property
    # def mod_names(self):
    #     return self.swagger.split("/ResourceProviders/")[0].split('/')[1:]

    # @property
    # def rp_name(self):
    #     return self.swagger.split("/ResourceProviders/")[1].split('/')[0]
