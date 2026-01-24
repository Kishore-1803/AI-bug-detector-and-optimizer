from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class DeveloperOutput(BaseModel):
    thought: str = Field(description="Your reasoning for the fix. Explain the bug and your solution.")
    code: str = Field(description="The full fixed code content.")

class DeveloperAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=DeveloperOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software developer. Your task is to fix bugs in Python code. "
                       "Analyze the bug, explain your fix, and then provide the code.\n"
                       "{format_instructions}"),
            ("user", "Bug Description: {description}\n\n"
                     "File Path: {file_path}\n\n"
                     "Current Code:\n{code}\n\n"
                     "Feedback (if any): {feedback}\n\n"
                     "Fix the bug:")
        ])
        self.prompt = self.prompt.partial(format_instructions=self.parser.get_format_instructions())
        
        self.chain = self.prompt | self.llm | self.parser

    def propose_fix(self, bug_info: dict, feedback: str = "") -> dict:
        return self.chain.invoke({
            "description": bug_info.get("description"),
            "file_path": bug_info.get("file_path"),
            "code": bug_info.get("code"),
            "feedback": feedback
        })
