
from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)


class QuizResponse(BaseModel):
    quiz_id: str
    questions: list[Question] = Field(min_length=5, max_length=5)


class EvaluationRequest(BaseModel):
    quiz_id: str
    answers: list[int] = Field(min_length=5, max_length=5)


class EvaluationResult(BaseModel):
    score: int
    total: int
    results: list[dict]
