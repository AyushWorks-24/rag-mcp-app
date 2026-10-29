
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from quiz_service import QuizService
from evaluator import QuizEvaluator
from schemas import QuizResponse, EvaluationRequest, EvaluationResult

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="RAG MCQ Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

quiz_service = QuizService()
evaluator = QuizEvaluator()


@app.get("/")
def home():
    return {"message": "RAG MCQ Generator API is running"}


@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    document_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")

        if not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

        pdf_path.write_bytes(content)
        processed_document_id = quiz_service.rag.process_pdf(str(pdf_path))
        questions = quiz_service.generate_quiz(processed_document_id)
        quiz_id = str(uuid.uuid4())
        quiz_service.quizzes[quiz_id] = questions

        
        return {
    "quiz_id": quiz_id,
    "questions": [
        {
            "question": question["question"],
            "options": question["options"]
        }
        for question in questions
    ]
}


    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if pdf_path.exists():
            pdf_path.unlink()


@app.post("/evaluate-quiz", response_model=EvaluationResult)
def evaluate_quiz(request: EvaluationRequest):
    questions = quiz_service.quizzes.get(request.quiz_id)

    if not questions:
        raise HTTPException(status_code=404, detail="Quiz not found. Please generate a new quiz.")

    try:
        return evaluator.evaluate(questions, request.answers)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
