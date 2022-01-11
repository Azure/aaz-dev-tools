from command.controller.config_editor import ConfigEditorWorkspaceManager
from command.tests.common import CommandTestCase


class WorkspaceTest(CommandTestCase):

    def test_workspace_manager(self):
        name = f"{self.__class__.__name__}_test_workspace_manager_1"
        file_name = ConfigEditorWorkspaceManager.get_ws_file_name(name)
        assert file_name == f"{name}.ws.json"
        file_path = ConfigEditorWorkspaceManager.get_ws_file_path(name)

        ws = ConfigEditorWorkspaceManager.create_workspace(name)
        ws2 = ConfigEditorWorkspaceManager.load_workspace(name)
        assert ws.to_primitive() == ws2.to_primitive()
        ws3 = ConfigEditorWorkspaceManager.update_workspace(name, ws2)
        assert ws3.version != ws.version
        ws4 = ConfigEditorWorkspaceManager.load_workspace(name)
        assert ws4.to_primitive() == ws3.to_primitive()
