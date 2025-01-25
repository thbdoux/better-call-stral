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
    troubling_events : List[str] = Field(description="Troubling events that occured in the case")
    alibis: List[str] = Field(description="Possible alibis for defense")

class Interference(BaseModel):
    interruption: str = Field(description="Words to inject in speech")

class JudgeVerdict(BaseModel):
    verdict: Literal["guilty", "innocent"] = Field(description="Final verdict")
    arguments: str = Field(description="Justification for verdict")
    closing_sentence: str = Field(description="Formal verdict announcement")

class GameState(BaseModel):
    storyboard: Storyboard
    current_text: str
    question: str
    difficulty: int
    past_interruptions : List[str] = Field(description="Past interruptions made by the malfunction of the neuralink and injected in the lawyer's speech.")

class QA(BaseModel):
    judge_question : str
    attorney_answer : str
class DefenseHistory(BaseModel):
    QA_history: List[QA]
    case_summary: Storyboard

@app.post("/generate_storyboard")
async def generate_storyboard() -> Storyboard:
    parser = JsonOutputParser(pydantic_object=Storyboard)
    template = """
    You're a master in generating fake trail stories. 
Can you generate a fake story of a guy named Daniel in trail accused of something fun.
Can you give the answer in a json format?
find 3 troubling ideas
find at least 3 alibis
ANSWER WITH ONLY THE JSON
    \n{format_instructions}\n
    """
    prompt = PromptTemplate(
        template=template,
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
        The lawyer is equipped with a neuralink chip that occasionally malfunctions, generating random, inappropriate, crazy or nonsensical words
        during their responses. Don't write bad stuff but you can make it crazy, like play the role of someone very enthousiastic for no reason, for instance.
        The level of malfunction is {difficulty}/5. The number of words is ranging from 1 to 5 according to the malfunction level.
        The interruptions should be either unrelated to the context or expressing the opposite of what the lawyer wants to say,
        and designed to distract or confuse. It must be FUNNY. Don't write too long interruptions, i can only be a few words, 
        with punctuation, or exagerated words in CAPS LOCK, or lengthened words like "let's gooooooooo" for instance. 
        
        Context: {context}
        Current speech: {speech}
        Past interruptions (please be creative and innovate, do new ones): {past_interruptions}
        Provide the answer in a json format :

        ANSWER WITH ONLY THE JSON

        \n{format_instructions}\n """,
        input_variables=["difficulty", "context", "speech", "past_interruptions"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    try:
        return chain.invoke({
            "difficulty": state.difficulty,
            "context": state.storyboard.dict(),
            "past_interruptions" : state.past_interruptions,
            "speech": state.current_text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/judge_question")
async def judge_question(history: DefenseHistory) -> str:
    prompt = PromptTemplate(
        template="""You play as a judge in a court. and this is the case you're judging.
        You are very funny, and don't hesitate to make jokes. Based on the case, invent a fun and relevant question to challenge the lawyer.
        You must not repeat a question you already asked.
        Case: {case}
        Question-Answer history: {QA_history}""",
        input_variables=["case", "QA_history"]
    )
    
    chain = prompt | llm
    try:
        response = chain.invoke({
            "QA_history" : history.QA_history,
            "case": history.case_summary.dict(),
        })
        return response.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/final_verdict")
async def generate_verdict(history: DefenseHistory) -> JudgeVerdict:
    parser = JsonOutputParser(pydantic_object=JudgeVerdict)
    template = """
        You play as a judge in a court. and this is the case you're judging.
        You are very funny, and don't hesitate to make jokes.
        You have to tell me if the defense was good enough for the accused to be acquitted or in the other way, has a penalty.
        If the speech does not make any sense at all, and he is not answering right at the questions, pronounce the correct judgment for him.
        Add a number of years of prison that the accused will take for punishment (between 0 and 10. Don't hesitate to be harsh if the defense is bad). If the accused is released, the number is 0.

        Be concise, and answer with only a few words. in a json format. 
        
        Case: {case}
        Question-Answer history: {QA_history}

        ANSWER WITH ONLY THE JSON

        \n{format_instructions}\n 
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["case", "QA_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    try:
        return chain.invoke({
            "case": history.case_summary.dict(),
            "QA_history": history.QA_history
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}