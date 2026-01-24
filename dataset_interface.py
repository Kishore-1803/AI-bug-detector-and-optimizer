import os
import subprocess
from typing import Dict, Any, Optional

class DatasetInterface:
    def get_bug_info(self, project: str, bug_id: str) -> Dict[str, Any]:
        """
        Retrieves information about a specific bug.
        """
        raise NotImplementedError

    def checkout_bug(self, project: str, bug_id: str) -> str:
        """
        Checks out the buggy version of the code.
        Returns the path to the checked-out code.
        """
        raise NotImplementedError

    def run_test(self, project: str, bug_id: str, patch_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the tests for the specific bug.
        If patch_content is provided, it applies the patch before running tests.
        """
        raise NotImplementedError

class MockDatasetInterface(DatasetInterface):
    """
    A mock interface for testing the agent workflow on Windows or without full BugsInPy setup.
    """
    def __init__(self, work_dir: str = "mock_workspace"):
        self.work_dir = os.path.abspath(work_dir)
        os.makedirs(self.work_dir, exist_ok=True)
        
        self.bugs = {
            "1": {
                "project": "dummy_project",
                "id": "1",
                "description": "The function 'add' incorrectly subtracts numbers.",
                "file_path": "calculator.py",
                "code": "def add(a, b):\n    return a - b  # Bug here\n",
                "test_file": "test_calculator.py",
                "test_code": "from calculator import add\n\ndef test_add():\n    assert add(2, 3) == 5\n"
            },
            "2": {
                "project": "dummy_project",
                "id": "2",
                "description": "Binary search implementation has a logic error. It fails to find elements in sorted arrays.",
                "file_path": "search.py",
                "code": """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            high = mid - 1  # Bug: Should be low = mid + 1
        else:
            low = mid + 1   # Bug: Should be high = mid - 1
    return -1
""",
                "test_file": "test_search.py",
                "test_code": """from search import binary_search

def test_binary_search():
    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert binary_search(arr, 5) == 4
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 10) == 9
    assert binary_search(arr, 11) == -1
"""
            },
            "3": {
                "project": "dummy_project",
                "id": "3",
                "description": "Sudoku solver fails to solve valid puzzles. It seems to get stuck or return incorrect results.",
                "file_path": "sudoku.py",
                "code": """def solve_sudoku(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty

    for num in range(1, 10):
        if is_valid(board, num, (row, col)):
            board[row][col] = num

            if solve_sudoku(board):
                return True

            # Bug: Missing backtrack step!
            # board[row][col] = 0 

    return False

def find_empty(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def is_valid(board, num, pos):
    # Check row
    for i in range(len(board[0])):
        if board[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x*3, box_x*3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False

    return True
""",
                "test_file": "test_sudoku.py",
                "test_code": """from sudoku import solve_sudoku

def test_solve_sudoku():
    board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]
    
    assert solve_sudoku(board) == True
    
    # Check if full
    for i in range(9):
        for j in range(9):
            assert board[i][j] != 0
"""
            }
        }

    def get_bug_info(self, project: str, bug_id: str) -> Dict[str, Any]:
        if bug_id not in self.bugs:
             raise ValueError(f"Bug ID {bug_id} not found.")
        return self.bugs[bug_id]

    def checkout_bug(self, project: str, bug_id: str) -> str:
        if bug_id not in self.bugs:
             raise ValueError(f"Bug ID {bug_id} not found.")
             
        bug = self.bugs[bug_id]
        
        # Create source file
        file_path = os.path.join(self.work_dir, bug["file_path"])
        with open(file_path, "w") as f:
            f.write(bug["code"])
        
        # Create test file
        test_path = os.path.join(self.work_dir, bug["test_file"])
        with open(test_path, "w") as f:
            f.write(bug["test_code"])
            
        return self.work_dir

    def run_test(self, project: str, bug_id: str, patch_content: Optional[str] = None) -> Dict[str, Any]:
        bug = self.bugs[bug_id]
        
        if patch_content:
            target_file = os.path.join(self.work_dir, bug["file_path"])
            with open(target_file, "w") as f:
                f.write(patch_content)

        # Run pytest
        try:
            result = subprocess.run(
                ["pytest", bug["test_file"]], 
                cwd=self.work_dir, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            passed = result.returncode == 0
            return {
                "passed": passed,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "passed": False,
                "stdout": "",
                "stderr": str(e)
            }
