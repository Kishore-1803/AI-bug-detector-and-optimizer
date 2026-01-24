# Multi-Agent Debate for Bug Fixing & Agentic Code Studio

This project implements a "Critic-Actor" multi-agent architecture to fix bugs, designed to work with the BugsInPy dataset (or a mock version). It includes both a CLI workflow and a modern Web UI.

## Architecture
The system uses **LangGraph** to orchestrate three agents:
1.  **Developer**: Proposes fixes for bugs.
2.  **Critic**: Reviews the fixes for logic and style errors.
3.  **Tester**: Runs unit tests to verify the fix.

## Prerequisites
- Python 3.8+
- Node.js 18+ (for Web UI)
- API Key (Google Gemini)

## Setup

1.  **Backend Setup**:
    ```bash
    pip install -r requirements.txt
    ```
    - Copy `.env.example` to `.env` (or create one)
    - Add your `GOOGLE_API_KEY`

2.  **Frontend Setup** (Next.js):
    ```bash
    cd frontend_next
    npm install
    ```

## Usage

### 1. Command Line Interface (CLI)
Run the bug fixing workflow directly in the terminal:
```bash
python main.py --mock
```

### 2. Web Interface (Agentic Code Studio)
To run the full web application, you need to start both the Python backend and the Next.js frontend.

**Start the Backend API:**
```bash
python server.py
# Server will start on http://localhost:8000
```

**Start the Frontend:**
```bash
cd frontend_next
npm run dev
# Open http://localhost:3000 in your browser
```

## Agents and Workflows
- `main.py`: CLI entry point.
- `server.py`: FastAPI backend server.
- `agents/`: Contains agent implementations (Developer, Critic, Tester).
- `workflow.py`, `optimization_workflow.py`, `security_workflow.py`: Define the LangGraph workflows.
