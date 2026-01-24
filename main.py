import argparse
import os
from dotenv import load_dotenv
from dataset_interface import MockDatasetInterface
from workflow import BugFixWorkflow

# Load environment variables (API keys)
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Bug Fixer")
    parser.add_argument("--project", type=str, default="dummy_project", help="Project name")
    parser.add_argument("--bug-id", type=str, default="1", help="Bug ID")
    parser.add_argument("--mock", action="store_true", default=True, help="Use mock dataset interface")
    
    args = parser.parse_args()
    
    # Initialize dataset interface
    if args.mock:
        dataset = MockDatasetInterface()
    else:
        # Placeholder for real BugsInPy interface
        raise NotImplementedError("Real BugsInPy interface not yet implemented.")
        
    # Setup workspace
    print(f"Checking out bug {args.bug_id} from {args.project}...")
    dataset.checkout_bug(args.project, args.bug_id)
    
    # Get bug info
    bug_info = dataset.get_bug_info(args.project, args.bug_id)
    print(f"Bug Description: {bug_info['description']}")
    
    # Initialize Workflow
    workflow = BugFixWorkflow(dataset)
    
    # Run Workflow
    initial_state = {
        "bug_info": bug_info,
        "current_patch": "",
        "critique_feedback": "",
        "test_feedback": "",
        "iterations": 0,
        "status": "start"
    }
    
    print("Starting Multi-Agent Debate...")
    final_state = workflow.app.invoke(initial_state)
    
    print("\n--- Final Result ---")
    print(f"Status: {final_state['status']}")
    print(f"Final Patch:\n{final_state['current_patch']}")
    
    if final_state['status'] == 'passed':
        print("SUCCESS: Bug fixed!")
    else:
        print("FAILURE: Could not fix bug within iteration limit.")

if __name__ == "__main__":
    main()
