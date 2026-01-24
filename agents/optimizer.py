from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class OptimizerOutput(BaseModel):
    thought: str = Field(description="Your reasoning process. Explain what you are optimizing and why.")
    code: str = Field(description="The full optimized code.")
    original_time_complexity: str = Field(description="The time complexity of the original code, e.g., O(n^2)")
    original_space_complexity: str = Field(description="The space complexity of the original code, e.g., O(n)")
    optimized_time_complexity: str = Field(description="The time complexity of the optimized code, e.g., O(n log n)")
    optimized_space_complexity: str = Field(description="The space complexity of the optimized code, e.g., O(1)")

class OptimizerAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)
        self.parser = JsonOutputParser(pydantic_object=OptimizerOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software optimization engineer. Your task is to optimize {language} code. "
                       "You must explain your reasoning first, then provide the code.\n"
                       "CRITICAL INSTRUCTION 1: The output code MUST be in {language}. Do NOT translate it to another language. "
                       "If the original code is in {language}, keep it in {language}. "
                       "If the original code is in a different language, translate it to {language} ONLY if explicitly asked, otherwise assume the user wants {language} code.\n"
                       "CRITICAL INSTRUCTION 2: You must PRESERVE the exact output of the program. "
                       "Do NOT change any print statements, logging messages, or the format of the output. "
                       "The optimized code must produce the EXACT SAME stdout as the original code, otherwise the benchmark will fail.\n"
                       "CRITICAL INSTRUCTION 3: If the requested language is NOT Python, do NOT attempt to make it runnable in Python. Just provide the optimized code in the requested language.\n"
                       "Additionally, you must estimate and output the time and space complexity for both the original and optimized code, in Big O notation.\n"
                       "Return your answer in the required JSON format.\n"
                       "{format_instructions}"),
            ("user", "Original Code:\n{code}\n\n"
                     "Feedback (if any): {feedback}\n\n"
                     "Optimize it and estimate the time and space complexity for both the original and optimized code:")
        ])
        self.prompt = self.prompt.partial(format_instructions=self.parser.get_format_instructions())
        
        self.chain = self.prompt | self.llm | self.parser

    def optimize_code(self, code: str, feedback: str = "", language: str = "python") -> dict:
        print(f"DEBUG: OptimizerAgent running for language: {language}")
        return self.chain.invoke({
            "code": code,
            "feedback": feedback,
            "language": language
        })
