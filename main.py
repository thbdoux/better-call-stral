from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os, random
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# LLMs initialization
llm = ChatMistralAI(
    model="mistral-small", 
    temperature=0.9,
    max_retries=2,
    api_key=os.getenv("MISTRAL_API_KEY")
)

# Pydantic models
class Storyboard(BaseModel):
    name: str = Field(description="Name of the accused person")
    accusation: str = Field(description="Crime they're accused of")
    how: str = Field(description="Method of the crime")
    when: str = Field(description="Time of the crime")
    alibis: List[str] = Field(description="Possible alibis for defense")

class Interference(BaseModel):
    interruption: str = Field(description="Words to inject in speech")
    position: int = Field(description="Position in text for injection")
    delay: float = Field(default=1.0, description="Delay before injection")

class JudgeVerdict(BaseModel):
    verdict: Literal["guilty", "innocent"] = Field(description="Final verdict")
    arguments: str = Field(description="Justification for verdict")
    closing_sentence: str = Field(description="Formal verdict announcement")

class GameState(BaseModel):
    storyboard: Storyboard
    current_text: str
    question: str
    difficulty: int

class DefenseHistory(BaseModel):
    attorney_responses: List[str]
    case_summary: Storyboard

@app.post("/generate_storyboard")
async def generate_storyboard() -> Storyboard:
    parser = JsonOutputParser(pydantic_object=Storyboard)
    prompt = PromptTemplate(
        template="Generate a creative criminal case.\n{format_instructions}\n",
        partial_variables={"format_instructions": parser.get_format_instructions()},
        input_variables=[]
    )
    
    chain = prompt | llm | parser
    try:
        return chain.invoke({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_interruption")
async def generate_interruption(state: GameState) -> Interference:
    parser = JsonOutputParser(pydantic_object=Interference)
    prompt = PromptTemplate(
        template="""You are responsible for simulating unexpected neural interference in a lawyer's speech.
        The lawyer is equipped with a neuralink chip that occasionally malfunctions, generating random, inappropriate, or nonsensical words
        during their responses. The level of malfunction is {difficulty}/10.
        These interruptions should have more words or be more inappropriate whether the malfunction is high. The interruptions should be either unrelated to the context or expressing the opposite of what the lawyer wants to say,
        and designed to distract or confuse. It must be FUNNY.
        
        Context: {context}
        Current speech: {speech}
        \n{format_instructions}\n """,
        input_variables=["difficulty", "context", "speech"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    try:
        return chain.invoke({
            "difficulty": state.difficulty,
            "context": state.storyboard.dict(),
            "speech": state.current_text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/judge_question")
async def judge_question(history: DefenseHistory) -> str:
    prompt = PromptTemplate(
        template="""You are a stern judge. Generate a probing question about the case.
        Case: {case}
        Previous responses: {responses}""",
        input_variables=["case", "responses"]
    )
    
    chain = prompt | llm
    try:
        response = chain.invoke({
            "case": history.case_summary.dict(),
            "responses": history.attorney_responses
        })
        return response.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/final_verdict")
async def generate_verdict(history: DefenseHistory) -> JudgeVerdict:
    parser = JsonOutputParser(pydantic_object=JudgeVerdict)
    prompt = PromptTemplate(
        template="""Deliver a final verdict based on the case evidence.
        Case: {case}
        Defense responses: {responses}
        \n{format_instructions}\n """,
        input_variables=["case", "responses"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    try:
        return chain.invoke({
            "case": history.case_summary.dict(),
            "responses": history.attorney_responses
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}