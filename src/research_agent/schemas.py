from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)
    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class ResearchQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)
    question: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    needs_web: bool = Field(default=False)

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v:str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v

    

