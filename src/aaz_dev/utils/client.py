
class CloudEnum:
    AzureCloud = 'AzureCloud'
    AzureChinaCloud = 'AzureChinaCloud'
    AzureUSGovernment = 'AzureUSGovernment'
    AzureGermanCloud = 'AzureGermanCloud'

    @classmethod
    def choices(cls):
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))
