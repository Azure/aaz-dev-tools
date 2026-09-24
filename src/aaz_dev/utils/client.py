
from typing import Tuple

class CloudEnum:
    AzureCloud = 'AzureCloud'
    AzureChinaCloud = 'AzureChinaCloud'
    AzureUSGovernment = 'AzureUSGovernment'
    AzureGermanCloud = 'AzureGermanCloud'

    @classmethod
    def choices(cls) -> Tuple[str, str, str, str]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))
