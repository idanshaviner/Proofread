"""Proofread deterministic API mock. No storage, no contextual intelligence."""
from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Proofread Prototype", version="0.1.0")


class ReplyRequest(BaseModel):
    mode: Literal["generate", "rewrite"] = "generate"
    incoming_message: str = Field(min_length=1, max_length=10000)
    relationship: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, max_length=500)
    draft: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def check_input(self):
        if any(not v.strip() for v in (self.incoming_message, self.relationship, self.goal)):
            raise ValueError("Required fields may not be whitespace-only")
        if self.mode == "rewrite" and not (self.draft and self.draft.strip()):
            raise ValueError("Rewrite mode requires nonblank draft")
        return self


class Candidate(BaseModel):
    id: int
    text: str
    label: str


class ReplyResponse(BaseModel):
    candidates: list[Candidate]
    provider: str = "deterministic-mock"
    personalized: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/responses", response_model=ReplyResponse)
def responses(request: ReplyRequest):
    if request.mode == "rewrite":
        base = request.draft.strip().rstrip(".!?")
        outputs = [base, base + "!", base + " :)"]
    else:
        outputs = [
            "haha yeah i'm down, when are you free?",
            "we should, you free this weekend?",
            "took you long enough to say that lol",
        ]
    return ReplyResponse(candidates=[
        Candidate(id=i+1, text=out, label=label)
        for i, (out, label) in enumerate(zip(outputs, ("Natural", "Direct", "Playful")))
    ])
