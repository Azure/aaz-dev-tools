from command.controller.config_editor import ConfigEditorWorkspaceManager
from command.tests.common import CommandTestCase
from utils.plane import PlaneEnum
import os


class WorkspaceTest(CommandTestCase):

    def test_workspace_manager(self):
        name = f"{self.__class__.__name__}_test_workspace_manager_1"
        ws = ConfigEditorWorkspaceManager(name)
        assert ws.path.endswith(os.path.join(name, "ws.json"))

        ws1 = ConfigEditorWorkspaceManager.new(name, plane=PlaneEnum.Mgmt)
        ws2 = ConfigEditorWorkspaceManager(name)
        assert ws.ws.to_primitive() == ws2.ws.to_primitive()
        # ws3 = ConfigEditorWorkspaceManager.update_workspace(name, ws2)
        # assert ws3.version != ws.version
        # ws4 = ConfigEditorWorkspaceManager.load_workspace(name)
        # assert ws4.to_primitive() == ws3.to_primitive()
