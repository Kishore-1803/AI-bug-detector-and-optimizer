from dataset_interface import DatasetInterface

class TesterAgent:
    def __init__(self, dataset_interface: DatasetInterface):
        self.dataset_interface = dataset_interface

    def test_fix(self, bug_info: dict, patch_content: str) -> dict:
        """
        Runs the tests with the proposed patch.
        """
        project = bug_info.get("project")
        bug_id = bug_info.get("id")
        
        result = self.dataset_interface.run_test(project, bug_id, patch_content)
        
        return result
