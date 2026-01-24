from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

class Vulnerability(BaseModel):
    severity: str = Field(description="High, Medium, or Low")
    type: str = Field(description="Type of vulnerability (e.g., SQL Injection, XSS)")
    description: str = Field(description="Description of the vulnerability")

class SecurityOutput(BaseModel):
    vulnerabilities: List[Vulnerability] = Field(description="List of found vulnerabilities")
    thought: str = Field(description="Reasoning for the security patches.")
    code: str = Field(description="The secured code content.")

class SecurityAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=SecurityOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Database Security Engineer. Your task is to analyze SQL queries for vulnerabilities and performance issues. "
                       "Strictly focus on SQL code. If the code provided is not SQL (e.g. Python, Java), respond by stating that you only analyze SQL. "
                       "Identify issues like SQL Injection risks, inefficient joins, missing indexes, or dangerous commands (DROP/TRUNCATE). "
                       "Provide a list of vulnerabilities/issues found, explain your hardening strategy, and provide the fully secured and optimized SQL query.\n"
                       "{format_instructions}"),
            ("user", "SQL Query to Audit:\n{code}\n\n"
                     "Feedback (from checks): {feedback}\n\n"
                     "Secure this SQL:")
        ])
        self.prompt = self.prompt.partial(format_instructions=self.parser.get_format_instructions())
        
        self.chain = self.prompt | self.llm | self.parser

    def audit_and_fix(self, code: str, feedback: str = "") -> dict:
        return self.chain.invoke({
            "code": code,
            "feedback": feedback
        })
