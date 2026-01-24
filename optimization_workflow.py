from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator

from agents.optimizer import OptimizerAgent
from agents.optimization_critic import OptimizationCriticAgent
from agents.benchmarker import BenchmarkerAgent

class OptimizationState(TypedDict):
    original_code: str
    current_optimized_code: str
    optimizer_thought: str
    critique_feedback: str
    benchmark_feedback: str
    test_input: str
    iterations: int
    status: str
    original_time_complexity: str
    original_space_complexity: str
    optimized_time_complexity: str
    optimized_space_complexity: str
    language: str

class OptimizationWorkflow:
    def __init__(self):
        self.optimizer = OptimizerAgent()
        self.critic = OptimizationCriticAgent()
        self.benchmarker = BenchmarkerAgent()
        
        # Define the graph
        workflow = StateGraph(OptimizationState)
        
        workflow.add_node("optimizer", self.run_optimizer)
        workflow.add_node("critic", self.run_critic)
        workflow.add_node("benchmarker", self.run_benchmarker)
        
        workflow.set_entry_point("optimizer")
        
        workflow.add_edge("optimizer", "critic")
        
        workflow.add_conditional_edges(
            "critic",
            self.check_critique,
            {
                "approved": "benchmarker",
                "rejected": "optimizer"
            }
        )
        
        workflow.add_conditional_edges(
            "benchmarker",
            self.check_benchmark_results,
            {
                "passed": END,
                "failed": "optimizer"
            }
        )
        
        self.app = workflow.compile()

    def run_optimizer(self, state: OptimizationState):
        print("\n--- Optimizer ---")
        feedback = ""
        if state.get("critique_feedback"):
            feedback += f"Critique: {state['critique_feedback']}\n"
        if state.get("benchmark_feedback"):
            feedback += f"Benchmark Output: {state['benchmark_feedback']}\n"

        # First iteration, use original code if no current optimized code
        code_to_fix = state["current_optimized_code"] if state["current_optimized_code"] else state["original_code"]
        language = state.get("language", "python")

        result_data = self.optimizer.optimize_code(code_to_fix, feedback, language)
        optimized_code = result_data["code"]
        thought = result_data["thought"]
        # Ensure all complexity fields are present, even if LLM omits them
        orig_time = result_data["original_time_complexity"] if "original_time_complexity" in result_data and result_data["original_time_complexity"] else "?"
        orig_space = result_data["original_space_complexity"] if "original_space_complexity" in result_data and result_data["original_space_complexity"] else "?"
        opt_time = result_data["optimized_time_complexity"] if "optimized_time_complexity" in result_data and result_data["optimized_time_complexity"] else "?"
        opt_space = result_data["optimized_space_complexity"] if "optimized_space_complexity" in result_data and result_data["optimized_space_complexity"] else "?"

        print(f"Optimizer Thought: {thought}")
        print(f"Proposed Optimization (Length: {len(optimized_code)})")
        print(f"Original Time: {orig_time}, Space: {orig_space}")
        print(f"Optimized Time: {opt_time}, Space: {opt_space}")
        return {
            "current_optimized_code": optimized_code,
            "optimizer_thought": thought,
            "iterations": state.get("iterations", 0) + 1,
            "original_time_complexity": orig_time,
            "original_space_complexity": orig_space,
            "optimized_time_complexity": opt_time,
            "optimized_space_complexity": opt_space,
            "language": language
        }

    def run_critic(self, state: OptimizationState):
        print("\n--- Optimization Critic ---")
        language = state.get("language", "python")
        review = self.critic.review_optimization(state["original_code"], state["current_optimized_code"], language)
        print(f"Decision: {'Approved' if review['approved'] else 'Rejected'}")
        print(f"Feedback: {review['feedback']}")
        return {
            "critique_feedback": review["feedback"],
            "status": "approved" if review["approved"] else "rejected"
        }

    def run_benchmarker(self, state: OptimizationState):
        print("\n--- Benchmarker ---")
        language = state.get("language", "python")
        print(f"DEBUG: Benchmarker running for language: {language}")
        result = self.benchmarker.run_benchmark(state["original_code"], state["current_optimized_code"], state.get("test_input", ""), language)
        print(f"Benchmark Passed: {result['passed']}")
        print(f"Output:\n{result['stdout']}")
        
        return {
            "benchmark_feedback": result["stdout"] + "\n" + result["stderr"],
            "status": "passed" if result["passed"] else "failed"
        }

    def check_critique(self, state: OptimizationState):
        if state["iterations"] > 5:
            print("Max iterations reached (Critic).")
            return "approved" 
            
        if state["status"] == "approved":
            return "approved"
        return "rejected"

    def check_benchmark_results(self, state: OptimizationState):
        if state["iterations"] > 8:
             print("Max iterations reached (Benchmark).")
             return "passed" 
             
        if state["status"] == "passed":
            return "passed"
        return "failed"
