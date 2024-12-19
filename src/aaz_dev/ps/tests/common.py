from app.tests.common import ApiTestCase
from utils.config import Config
# from command.tests.common import workspace_name
# from swagger.utils.tools import swagger_resource_path_to_resource_id
# from swagger.utils.source import SourceTypeEnum
# from utils.plane import PlaneEnum
# from utils.stage import AAZStageEnum
# from utils.client import CloudEnum


class CommandTestCase(ApiTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
