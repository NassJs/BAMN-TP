from fastapi import FastAPI
from pydantic import BaseModel

from app.retrieve import retrieve

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: QuestionRequest):

    results = retrieve(req.question)

    sources = []

    for hit in results:
        source = hit.payload.get("source", "Inconnue")
        sources.append(source)

    return {
        "question": req.question,
        "nb_results": len(results),
        "sources": list(set(sources))
    }