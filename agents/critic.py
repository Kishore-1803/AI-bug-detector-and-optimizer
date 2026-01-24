from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class Critique(BaseModel):
    approved: bool = Field(description="Whether the code is approved or not")
    feedback: str = Field(description="Detailed feedback on logic, style, or potential bugs")

class CriticAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=Critique)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior code reviewer. You are critical and strict. "
                       "Review the proposed fix for the bug. Check for logical errors, hallucinations (variables that don't exist), and style issues. "
                       "If the code looks correct and fixes the bug, approve it. Otherwise, reject it with feedback.\n"
                       "{format_instructions}"),
            ("user", "Bug Description: {description}\n\n"
                     "Original Code:\n{original_code}\n\n"
                     "Proposed Fix:\n{proposed_code}\n\n"
                     "Review:")
        ]).partial(format_instructions=self.parser.get_format_instructions())
        
        self.chain = self.prompt | self.llm | self.parser

    def review_fix(self, bug_info: dict, proposed_code: str) -> dict:
        return self.chain.invoke({
            "description": bug_info.get("description"),
            "original_code": bug_info.get("code"),
            "proposed_code": proposed_code
        })
