from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class OptimizationCritique(BaseModel):
    approved: bool = Field(description="Whether the optimization is valid and preserves logic")
    feedback: str = Field(description="Detailed feedback. If rejected, explain why (e.g., changed logic, introduced bug, not actually faster).")

class OptimizationCriticAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=OptimizationCritique)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior code reviewer specializing in optimization. "
                       "Review the proposed optimized code against the original code. "
                       "The code is written in {language}.\n"
                       "CRITICAL: The optimized code MUST produce exactly the same output/behavior as the original code for all inputs. "
                       "If logic is changed, REJECT it immediately. "
                       "If it's not actually more optimal, REJECT it. "
                       "If valid and efficient, Approve it.\n"
                       "{format_instructions}"),
            ("user", "Original Code:\n{original_code}\n\n"
                     "Proposed Optimized Code:\n{proposed_code}\n\n"
                     "Review:")
        ])
        self.prompt = self.prompt.partial(format_instructions=self.parser.get_format_instructions())
        
        self.chain = self.prompt | self.llm | self.parser

    def review_optimization(self, original_code: str, proposed_code: str, language: str = "python") -> dict:
        return self.chain.invoke({
            "original_code": original_code,
            "proposed_code": proposed_code,
            "language": language
        })
