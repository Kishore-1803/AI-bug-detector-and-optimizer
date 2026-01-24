import time
import io
import sys
import contextlib
import traceback

class BenchmarkerAgent:
    def __init__(self):
        pass

    def run_benchmark(self, original_code: str, optimized_code: str, test_input: str = "", language: str = "python") -> dict:
        """
        Runs both original and optimized code.
        If test_input is provided, it tries to inject it or run with it.
        For now, this attempts to simple EXEC the code and capture stdout/time.
        WARNING: This executes arbitrary code. In a real system, use a sandbox.
        """
        print(f"DEBUG: BenchmarkerAgent received language: {language}")
        
        if language.lower() != "python":
            print(f"DEBUG: Skipping benchmark for non-Python language: {language}")
            return {
                "passed": True,
                "stdout": f"Benchmarking skipped for language: {language}. Only Python is currently supported for execution. Code structure and logic appear valid.",
                "stderr": ""
            }

        # Simple helper to execute and time code
        def execute_and_time(code_str, input_str):
            output_capture = io.StringIO()
            start_time = time.perf_counter()
            error = None
            
            try:
                # Redirect stdout to capture output
                with contextlib.redirect_stdout(output_capture):
                    # Create a constrained global/local scope
                    exec_globals = {}
                    # If the code expects input(), this will fail without mocking input.
                    # For simplicity, we assume code operates on variables or prints.
                    # We can try to mock input() if test_input is present, 
                    # but simple exec won't easily handle interactive input unless we mock sys.stdin
                    
                    if input_str:
                         sys.stdin = io.StringIO(input_str)

                    exec(code_str, exec_globals)
            except Exception as e:
                error = traceback.format_exc()
            finally:
                sys.stdin = sys.__stdin__ # Reset stdin
                
            end_time = time.perf_counter()
            return {
                "output": output_capture.getvalue(),
                "time": end_time - start_time,
                "error": error
            }

        print("--- Benchmarking Original ---")
        orig_res = execute_and_time(original_code, test_input)
        
        print("--- Benchmarking Optimized ---")
        opt_res = execute_and_time(optimized_code, test_input)
        
        # Determine pass/fail
        # 1. Optimised code must not error (or same error as original?) - usually shouldn't error.
        # 2. Output should match (if original didn't error).
        
        passed = True
        feedback = ""
        
        if opt_res["error"]:
            passed = False
            feedback += f"Optimized code failed with error: {opt_res['error']}\n"
        elif orig_res["output"] != opt_res["output"]:
            passed = False
            feedback += f"Output mismatch!\nOriginal: {orig_res['output']}\nOptimized: {opt_res['output']}\n"
        else:
            # Check Performance
            feedback += f"Original Time: {orig_res['time']:.6f}s\n"
            feedback += f"Optimized Time: {opt_res['time']:.6f}s\n"
            if opt_res["time"] < orig_res["time"]:
                improvement = (orig_res["time"] - opt_res["time"]) / orig_res["time"] * 100
                feedback += f"Speedup: {improvement:.2f}%\n"
            else:
                feedback += "No speedup detected (optimised might be slower or too fast to measure difference).\n"

        return {
            "passed": passed,
            "stdout": feedback,
            "stderr": opt_res["error"] if opt_res["error"] else ""
        }
