import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import os
from dotenv import load_dotenv

from dataset_interface import MockDatasetInterface
from workflow import BugFixWorkflow
from optimization_workflow import OptimizationWorkflow
from security_workflow import SecurityWorkflow

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Agentic Code Studio API is running. Please use the Next.js frontend."}

class BugFixRequest(BaseModel):
    description: str
    code: str

class SecurityRequest(BaseModel):
    code: str

class OptimizationRequest(BaseModel):
    code: str
    test_input: str = ""
    language: str = "python"

@app.post("/analyze/fix")
async def analyze_fix(request: BugFixRequest):
    # For now, we will just use a mock dataset interface wrapper 
    # since the existing BugFixWorkflow relies on it.
    # In a real app we would refactor BugFixWorkflow to take raw code too.
    # Hack: We will create a temporary "bug" in the mock dataset
    
    dataset = MockDatasetInterface()
    # We need to inject this custom bug into the mock dataset
    bug_id = "custom_1"
    project = "custom_project"
    
    dataset.bugs[bug_id] = {
        "project": project,
        "id": bug_id,
        "description": request.description,
        "code": request.code,
        "file_path": "custom.py",
        "test": "def test_custom(): assert False # Placeholder", 
        "test_file": "test_custom.py",
        "test_code": "def test_placeholder(): pass"
    }
    
    workflow = BugFixWorkflow(dataset)
    dataset.checkout_bug(project, bug_id)
    bug_info = dataset.get_bug_info(project, bug_id)
    
    initial_state = {
        "bug_info": bug_info,
        "current_patch": "",
        "critique_feedback": "",
        "test_feedback": "",
        "iterations": 0,
        "status": "start"
    }
    
    async def event_generator():
        try:
            # Stream intermediate steps for timeline view
            for output in workflow.app.stream(initial_state):
                 yield json.dumps(output) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "payload": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.post("/analyze/security")
async def analyze_security(request: SecurityRequest):
    # Hack: Reset mock dataset with this "bug" but strictly for context
    dataset = MockDatasetInterface()
    bug_id = "security_audit_1"
    project = "security_project"
    
    # We set up a bug entry so the Tester and Critic have context
    # ideally we would separate "Bug" from "Task" in the logic
    dataset.bugs[bug_id] = {
        "project": project,
        "id": bug_id,
        "description": "SQL Security Audit",
        "code": request.code,
        "file_path": "query.sql",
        "test": "def test_sql(): pass", # Dummy test 
        "test_file": "test_sql.py",
        "test_code": "def test_placeholder(): pass"
    }
    
    workflow = SecurityWorkflow(dataset)
    dataset.checkout_bug(project, bug_id)
    bug_info = dataset.get_bug_info(project, bug_id)
    
    initial_state = {
        "bug_info": bug_info,
        "original_code": request.code,
        "current_patch": "",
        "security_thought": "",
        "vulnerabilities": [],
        "critique_feedback": "",
        "test_feedback": "",
        "iterations": 0,
        "status": "start"
    }
    
    async def event_generator():
        try:
            for output in workflow.app.stream(initial_state):
                 yield json.dumps(output) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "payload": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.post("/analyze/optimize")
async def analyze_optimize(request: OptimizationRequest):
    print(f"DEBUG: Received optimization request for language: {request.language}")
    workflow = OptimizationWorkflow()
    
    initial_state = {
        "original_code": request.code,
        "current_optimized_code": "",
        "critique_feedback": "",
        "benchmark_feedback": "",
        "test_input": request.test_input,
        "iterations": 0,
        "status": "start",
        "language": request.language
    }
    
    async def event_generator():
        try:
             # We want to yield intermediate steps.
             # LangGraph `stream` method is perfect for this.
             
            for output in workflow.app.stream(initial_state):
                 # output is a dict of {node_name: {state_updates}}
                 yield json.dumps(output) + "\n"
                 
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
