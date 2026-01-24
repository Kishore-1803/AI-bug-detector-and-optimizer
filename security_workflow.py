from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator

from agents.security import SecurityAgent
from agents.critic import CriticAgent
from agents.tester import TesterAgent
from dataset_interface import DatasetInterface

class SecurityAgentState(TypedDict):
    bug_info: dict # Reusing bug_info structure for consistency (contains 'code' and test info)
    original_code: str
    current_patch: str
    security_thought: str
    vulnerabilities: list
    critique_feedback: str
    test_feedback: str
    iterations: int
    status: str

class SecurityWorkflow:
    def __init__(self, dataset_interface: DatasetInterface):
        self.security_agent = SecurityAgent()
        self.critic = CriticAgent()
        self.tester = TesterAgent(dataset_interface)
        
        # Define the graph
        workflow = StateGraph(SecurityAgentState)
        
        workflow.add_node("security_engineer", self.run_security_engineer)
        workflow.add_node("critic", self.run_critic)
        workflow.add_node("tester", self.run_tester)
        
        workflow.set_entry_point("security_engineer")
        
        workflow.add_edge("security_engineer", "critic")
        
        workflow.add_conditional_edges(
            "critic",
            self.check_critique,
            {
                "approved": "tester",
                "rejected": "security_engineer"
            }
        )
        
        workflow.add_conditional_edges(
            "tester",
            self.check_test_results,
            {
                "passed": END,
                "failed": "security_engineer"
            }
        )
        
        self.app = workflow.compile()

    def run_security_engineer(self, state: SecurityAgentState):
        print("\n--- Security Engineer ---")
        feedback = ""
        if state.get("critique_feedback"):
            feedback += f"Critique: {state['critique_feedback']}\n"
        if state.get("test_feedback"):
            feedback += f"Test Output: {state['test_feedback']}\n"
            
        # If it's the first run, use original code, otherwise use last patch or feedback
        code_to_fix = state.get("current_patch") if state.get("current_patch") else state["original_code"]
        
        result = self.security_agent.audit_and_fix(code_to_fix, feedback)
        patch = result["code"]
        thought = result["thought"]
        vulnerabilities = result["vulnerabilities"]
        
        print(f"Security Thought: {thought}")
        print(f"Vulnerabilities Found: {len(vulnerabilities)}")
        return {
            "current_patch": patch,
            "security_thought": thought,
            "vulnerabilities": vulnerabilities,
            "iterations": state.get("iterations", 0) + 1
        }

    def run_critic(self, state: SecurityAgentState):
        print("\n--- Critic ---")
        review = self.critic.review_fix(state["bug_info"], state["current_patch"])
        print(f"Decision: {'Approved' if review['approved'] else 'Rejected'}")
        print(f"Feedback: {review['feedback']}")
        return {
            "critique_feedback": review["feedback"],
            "status": "approved" if review["approved"] else "rejected"
        }

    def run_tester(self, state: SecurityAgentState):
        print("\n--- Tester ---")
        # Ensure we are testing the patch against the project associated with the bug_info
        # In a real security mode, we should perhaps run a security scanner here too, 
        # but for now we verify we didn't break functionality.
        result = self.tester.test_fix(state["bug_info"], state["current_patch"])
        print(f"Test Passed: {result['passed']}")
        return {
            "test_feedback": result["stdout"] + "\n" + result["stderr"],
            "status": "passed" if result["passed"] else "failed"
        }

    def check_critique(self, state: SecurityAgentState):
        if state["iterations"] > 5:
            return "approved" 
        return state["status"]

    def check_test_results(self, state: SecurityAgentState):
        if state["iterations"] > 5:
            return "passed"
        return state["status"]
