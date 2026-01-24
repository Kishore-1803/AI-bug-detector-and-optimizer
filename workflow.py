from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator

from agents.developer import DeveloperAgent
from agents.critic import CriticAgent
from agents.tester import TesterAgent
from dataset_interface import DatasetInterface

class AgentState(TypedDict):
    bug_info: dict
    current_patch: str
    developer_thought: str
    critique_feedback: str
    test_feedback: str
    iterations: int
    status: str

class BugFixWorkflow:
    def __init__(self, dataset_interface: DatasetInterface):
        self.developer = DeveloperAgent()
        self.critic = CriticAgent()
        self.tester = TesterAgent(dataset_interface)
        
        # Define the graph
        workflow = StateGraph(AgentState)
        
        workflow.add_node("developer", self.run_developer)
        workflow.add_node("critic", self.run_critic)
        workflow.add_node("tester", self.run_tester)
        
        workflow.set_entry_point("developer")
        
        workflow.add_edge("developer", "critic")
        
        workflow.add_conditional_edges(
            "critic",
            self.check_critique,
            {
                "approved": "tester",
                "rejected": "developer"
            }
        )
        
        workflow.add_conditional_edges(
            "tester",
            self.check_test_results,
            {
                "passed": END,
                "failed": "developer"
            }
        )
        
        self.app = workflow.compile()

    def run_developer(self, state: AgentState):
        print("\n--- Developer ---")
        feedback = ""
        if state.get("critique_feedback"):
            feedback += f"Critique: {state['critique_feedback']}\n"
        if state.get("test_feedback"):
            feedback += f"Test Output: {state['test_feedback']}\n"
            
        patch_data = self.developer.propose_fix(state["bug_info"], feedback)
        patch = patch_data["code"]
        thought = patch_data["thought"]
        
        print(f"Developer Thought: {thought}")
        print(f"Proposed Patch:\n{patch}")
        return {
            "current_patch": patch,
            "developer_thought": thought,
            "iterations": state.get("iterations", 0) + 1
        }

    def run_critic(self, state: AgentState):
        print("\n--- Critic ---")
        review = self.critic.review_fix(state["bug_info"], state["current_patch"])
        print(f"Decision: {'Approved' if review['approved'] else 'Rejected'}")
        print(f"Feedback: {review['feedback']}")
        return {
            "critique_feedback": review["feedback"],
            "status": "approved" if review["approved"] else "rejected"
        }

    def run_tester(self, state: AgentState):
        print("\n--- Tester ---")
        result = self.tester.test_fix(state["bug_info"], state["current_patch"])
        print(f"Test Passed: {result['passed']}")
        if not result['passed']:
            print(f"Test Output: {result['stderr']}")
        return {
            "test_feedback": result["stdout"] + "\n" + result["stderr"],
            "status": "passed" if result["passed"] else "failed"
        }

    def check_critique(self, state: AgentState):
        if state["iterations"] > 5:
            print("Max iterations reached.")
            return "approved" # Force move to test or end
            
        if state["status"] == "approved":
            return "approved"
        return "rejected"

    def check_test_results(self, state: AgentState):
        if state["iterations"] > 10:
             print("Max iterations reached (Total).")
             return "passed" # Give up
             
        if state["status"] == "passed":
            return "passed"
        return "failed"
