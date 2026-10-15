"""Proofread API: deterministic mock by default, opt-in model provider."""
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator
from .provider import ReplyResponse, ProviderConfigurationError, ProviderFailure, build_provider

app = FastAPI(title="Proofread Prototype", version="0.2.0")

class ReplyRequest(BaseModel):
    mode: Literal["generate", "rewrite"] = "generate"
    incoming_message: str = Field(min_length=1, max_length=10000)
    relationship: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, max_length=500)
    draft: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def validate_input(self):
        if any(not s.strip() for s in (self.incoming_message, self.relationship, self.goal)):
            raise ValueError("Required fields may not be whitespace-only")
        if self.mode == "rewrite" and not (self.draft and self.draft.strip()):
            raise ValueError("Rewrite requires nonblank draft")
        return self

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/responses", response_model=ReplyResponse)
async def responses(request: ReplyRequest):
    try:
        return await build_provider().generate(request)
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ProviderFailure as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
