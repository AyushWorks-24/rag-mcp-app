# RAG MCQ Quiz Generator

A web application that uses Retrieval-Augmented Generation (RAG) to generate multiple-choice quizzes from uploaded PDF documents.

## Features

- Upload PDF documents
- Extract and process text from PDFs
- Store document chunks in ChromaDB
- Generate 5 multiple-choice questions using Groq
- Submit answers and view quiz results
- Get correct answers and explanations after evaluation

## Tech Stack

- Python
- FastAPI
- Groq API
- ChromaDB
- PyMuPDF
- HTML, CSS, JavaScript

## Project Structure

```text
rag-mcp-app/
├── backend/
│   ├── app.py
│   ├── rag_engine.py
│   ├── quiz_service.py
│   ├── evaluator.py
│   ├── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── uploads/
├── vector_db/
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd rag-mcp-app
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your Groq API key and model:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Use your own API key. Do not commit the `.env` file to GitHub.

### 5. Start the backend

Run from the project root:

```bash
python -m uvicorn app:app --app-dir backend --reload
```

The API will be available at `http://127.0.0.1:8000`.

API documentation: `http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open another terminal from the project root:

```bash
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500` in your browser.

## Usage

1. Start the backend and frontend.
2. Upload a PDF document.
3. Generate a quiz.
4. Answer all five questions.
5. Submit your answers to see your score and explanations.

## Security

Keep API keys and other secrets in your local `.env` file. Do not upload secrets or private documents to the repository.

## License

This project is currently for learning and educational purposes.
