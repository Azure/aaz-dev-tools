from .az_module_manager import AzModuleManager

class PSAutoRestConfigurationGenerator:

    def __init__(self, az_module_manager: AzModuleManager, module_name) -> None:
        az_module_manager.load_module()
