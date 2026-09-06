"""REST API for Education Knowledge Graph."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from education_kg.models import ConceptDifficulty
from education_kg.pipeline import Pipeline

app = FastAPI(title="Education Knowledge Graph API", version="1.0.0")
pipeline = Pipeline()


class TextInput(BaseModel):
    text: str
    subject: str = ""


class LearningPathInput(BaseModel):
    start: str
    goal: str


class QuizInput(BaseModel):
    concept_ids: list[str]
    num_questions: int = 5


class QuestionInput(BaseModel):
    query: str
    concept_id: str = ""


@app.get("/")
async def root():
    return {"message": "Education Knowledge Graph API", "version": "1.0.0"}


@app.get("/stats")
async def stats():
    graph = pipeline.get_graph()
    return graph.get_statistics()


@app.post("/extract")
async def extract(input_data: TextInput):
    result = pipeline.process_text(input_data.text, input_data.subject)
    return {
        "concepts_extracted": result.concepts_extracted,
        "relations_found": result.relations_found,
        "errors": result.errors,
        "warnings": result.warnings,
    }


@app.get("/concepts")
async def concepts(subject: str = "", difficulty: str = "", limit: int = 20):
    graph = pipeline.get_graph()
    diff = None
    if difficulty:
        try:
            diff = ConceptDifficulty(difficulty)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid difficulty")
    results = graph.search("", subject=subject, difficulty=diff, limit=limit)
    return [c.to_dict() for c in results]


@app.get("/concepts/{concept_id}")
async def get_concept(concept_id: str):
    graph = pipeline.get_graph()
    concept = graph.get_concept(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    return concept.to_dict()


@app.post("/learning-path")
async def learning_path(input_data: LearningPathInput):
    result = pipeline.generate_learning_path(input_data.start, input_data.goal)
    if not result:
        raise HTTPException(status_code=404, detail="No path found")
    return result.to_dict()


@app.post("/quiz")
async def quiz(input_data: QuizInput):
    result = pipeline.generate_quiz(input_data.concept_ids, input_data.num_questions)
    return result.to_dict()


@app.post("/ask")
async def ask(input_data: QuestionInput):
    result = pipeline.answer_question(input_data.query, input_data.concept_id)
    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "reasoning_path": result.reasoning_path,
        "supporting_evidence": result.supporting_evidence,
    }


@app.get("/languages")
async def languages():
    ml = pipeline.get_multilang()
    return {"languages": ml.get_supported_languages()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
