"""Proofread API: deterministic mock by default, opt-in model provider."""
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator
from .provider import (ReplyResponse, OpenAIProvider, ProviderConfigurationError,
                       ProviderFailure, build_provider, create_provider_http_client)


@asynccontextmanager
async def lifespan(application):
    async with create_provider_http_client() as client:
        application.state.provider_http_client = client
        try:
            yield
        finally:
            del application.state.provider_http_client


app = FastAPI(title="Proofread Prototype", version="0.2.0", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def invalid_request(_request, exception):
    # Pydantic errors include input and exception context, sometimes the entire
    # message body. Keep field locations and categories, never submitted values.
    return JSONResponse(status_code=422, content={"detail": [
        {"loc": error["loc"], "type": error["type"], "msg": "Invalid request field"}
        for error in exception.errors()
    ]})


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
        provider = build_provider()
        if isinstance(provider, OpenAIProvider) and provider.client is None and provider.transport is None:
            # Mounted apps may not run their own lifespan. None retains the
            # provider's transient ownership path, which closes after the call.
            provider.client = getattr(app.state, "provider_http_client", None)
        return await provider.generate(request)
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ProviderFailure as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
