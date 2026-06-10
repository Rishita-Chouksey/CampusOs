# =============================================================================
# CampusOS — Exam Prep + AI Copilot
# main.py  |  FastAPI Application
#
# Run:  uvicorn main:app --reload
# Docs: http://127.0.0.1:8000/docs   (Swagger UI — auto-generated)
# =============================================================================

import os
import json
import re
import logging
from contextlib import asynccontextmanager
from typing import Optional, Any

import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# =============================================================================
# Logging Setup
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("campusOS")

# =============================================================================
# Environment & Gemini Configuration
# =============================================================================

# Load .env file (API_KEY lives there; never hard-code secrets)
load_dotenv()

API_KEY    = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not API_KEY:
    # Fail fast at startup — better than a cryptic runtime error
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Add it to your .env file or export it as an environment variable."
    )

genai.configure(api_key=API_KEY)
logger.info("Gemini configured with model: %s", MODEL_NAME)


def get_model() -> genai.GenerativeModel:
    """Returns a fresh GenerativeModel instance (stateless, thread-safe)."""
    return genai.GenerativeModel(MODEL_NAME)


# =============================================================================
# Lifespan — startup / shutdown hooks
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup and once on shutdown."""
    logger.info("🚀 CampusOS API starting up …")
    yield
    logger.info("🛑 CampusOS API shutting down …")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title       = "CampusOS — Exam Prep + AI Copilot",
    description = (
        "AI-powered exam preparation API built with Google Gemini.\n\n"
        "Endpoints:\n"
        "- `POST /flashcards`  — Generate flashcards from notes\n"
        "- `POST /quiz`        — Generate MCQ quiz from notes\n"
        "- `POST /studyplan`   — Generate a day-wise study plan\n"
        "- `POST /copilot`     — Natural-language AI copilot router\n"
        "- `GET  /health`      — Service health check\n"
    ),
    version     = "1.0.0",
    lifespan    = lifespan,
)

# =============================================================================
# CORS Middleware — allow React frontend (any localhost port during dev)
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    # In production replace "*" with your actual frontend domain,
    # e.g. ["https://campus-os.vercel.app"]
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# =============================================================================
# Global Exception Handler — catches unhandled errors cleanly
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content     = {"detail": f"Internal server error: {str(exc)}"},
    )


# =============================================================================
# Pydantic — Request Models
# =============================================================================

class FlashcardRequest(BaseModel):
    """Request body for POST /flashcards"""
    notes_text: str = Field(
        ...,
        min_length  = 10,
        description = "Raw study notes to generate flashcards from.",
        examples    = ["TCP provides reliable communication. UDP is connectionless."],
    )

    @field_validator("notes_text")
    @classmethod
    def notes_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("notes_text must not be blank.")
        return v.strip()


class QuizRequest(BaseModel):
    """Request body for POST /quiz"""
    notes_text: str = Field(
        ...,
        min_length  = 10,
        description = "Raw study notes to generate MCQs from.",
    )
    num_questions: int = Field(
        default     = 10,
        ge          = 1,
        le          = 20,
        description = "Number of MCQs to generate (1–20). Default: 10.",
    )

    @field_validator("notes_text")
    @classmethod
    def notes_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("notes_text must not be blank.")
        return v.strip()


class StudyPlanRequest(BaseModel):
    """Request body for POST /studyplan"""
    subject: str = Field(
        ...,
        min_length  = 2,
        description = "Subject or topic to study (e.g. 'Computer Networks').",
        examples    = ["Computer Networks"],
    )
    days_left: int = Field(
        ...,
        ge          = 1,
        le          = 60,
        description = "Days remaining before the exam (1–60).",
        examples    = [5],
    )

    @field_validator("subject")
    @classmethod
    def subject_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("subject must not be blank.")
        return v.strip()


class CopilotRequest(BaseModel):
    """Request body for POST /copilot"""
    query: str = Field(
        ...,
        min_length  = 3,
        description = "Natural-language request (e.g. 'Generate flashcards from my notes').",
        examples    = ["Generate flashcards from my notes"],
    )
    notes_text: Optional[str] = Field(
        default     = "",
        description = "Study notes (required for flashcard / quiz intents).",
    )
    subject: Optional[str] = Field(
        default     = "",
        description = "Subject name (used for study plan intent).",
    )
    days_left: Optional[int] = Field(
        default     = 7,
        ge          = 1,
        le          = 60,
        description = "Days remaining (used for study plan intent).",
    )


# =============================================================================
# Pydantic — Response Models
# =============================================================================

class FlashcardItem(BaseModel):
    question: str
    answer  : str

class FlashcardResponse(BaseModel):
    flashcards: list[FlashcardItem]
    count     : int


class QuizItem(BaseModel):
    question: str
    options : list[str]    # ["A. ...", "B. ...", "C. ...", "D. ..."]
    answer  : str          # "A" | "B" | "C" | "D"

class QuizResponse(BaseModel):
    quiz : list[QuizItem]
    count: int


class StudyPlanResponse(BaseModel):
    study_plan: dict[str, str]   # {"Day 1": "...", "Day 2": "..."}
    subject   : str
    days_left : int


class CopilotResponse(BaseModel):
    intent  : str        # "flashcard" | "quiz" | "study_plan" | "unknown"
    message : str
    response: Any        # the actual payload — varies by intent


class HealthResponse(BaseModel):
    status : str
    service: str
    model  : str


# =============================================================================
# Core AI Functions (identical logic to the Jupyter notebook module)
# =============================================================================

def _parse_json(raw: str) -> Any:
    """
    Strips Gemini's markdown code-fences and parses JSON.
    Raises ValueError on failure.
    """
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse Gemini response as JSON.\nRaw:\n{raw}\nError: {e}"
        )


def _generate_flashcards(notes_text: str) -> list[dict]:
    """Calls Gemini to produce flashcards. Returns list of {question, answer}."""
    prompt = f"""
You are an expert study assistant helping students prepare for exams.

Given the following study notes, generate a list of flashcards.

Rules:
- Each flashcard must have a "question" and an "answer".
- Questions should test key concepts, definitions, or facts.
- Answers must be concise (1–2 sentences max).
- Return ONLY a valid JSON array — no extra text, no markdown fences.

Output format:
[
  {{"question": "...", "answer": "..."}},
  {{"question": "...", "answer": "..."}}
]

Study Notes:
\"\"\"
{notes_text}
\"\"\"
"""
    model      = get_model()
    response   = model.generate_content(prompt)
    flashcards = _parse_json(response.text)

    if not isinstance(flashcards, list):
        raise ValueError("Gemini returned non-list for flashcards.")

    for card in flashcards:
        if "question" not in card or "answer" not in card:
            raise ValueError(f"Malformed flashcard: {card}")

    logger.info("Generated %d flashcard(s).", len(flashcards))
    return flashcards


def _generate_quiz(notes_text: str, num_questions: int = 10) -> list[dict]:
    """Calls Gemini to produce MCQs. Returns list of {question, options, answer}."""
    prompt = f"""
You are an expert exam question setter for university students.

Given the following study notes, generate exactly {num_questions} MCQs.

Rules:
- Each question must have exactly 4 options labelled A, B, C, D.
- The "answer" field must contain only the letter (e.g. "B").
- Base questions strictly on the notes provided.
- Vary difficulty: recall, application, and conceptual questions.
- Return ONLY a valid JSON array — no extra text, no markdown fences.

Output format:
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "B"
  }}
]

Study Notes:
\"\"\"
{notes_text}
\"\"\"
"""
    model    = get_model()
    response = model.generate_content(prompt)
    quiz     = _parse_json(response.text)

    if not isinstance(quiz, list):
        raise ValueError("Gemini returned non-list for quiz.")

    for i, q in enumerate(quiz):
        if not all(k in q for k in ("question", "options", "answer")):
            raise ValueError(f"Malformed question at index {i}: {q}")
        if len(q["options"]) != 4:
            raise ValueError(f"Question {i} must have 4 options, got {len(q['options'])}.")

    logger.info("Generated %d MCQ(s).", len(quiz))
    return quiz


def _generate_study_plan(subject: str, days_left: int) -> dict:
    """Calls Gemini to produce a day-wise study plan. Returns {Day N: text}."""
    prompt = f"""
You are an expert academic tutor and study coach.

Create a detailed day-wise study plan for a student preparing for their {subject} exam.
They have exactly {days_left} day(s) remaining.

Rules:
- Spread topics logically across the available days.
- Include revision and mock-test practice on the final day.
- Each day's entry should be a concise paragraph (2–4 sentences).
- Keys must be exactly "Day 1", "Day 2", ..., "Day {days_left}".
- Return ONLY a valid JSON object — no extra text, no markdown fences.

Output format:
{{
  "Day 1": "...",
  "Day 2": "...",
  ...
  "Day {days_left}": "..."
}}
"""
    model    = get_model()
    response = model.generate_content(prompt)
    plan     = _parse_json(response.text)

    if not isinstance(plan, dict):
        raise ValueError("Gemini returned non-dict for study plan.")

    logger.info("Generated study plan for '%s' (%d days).", subject, days_left)
    return plan


def _ai_copilot(
    query     : str,
    notes_text: str = "",
    subject   : str = "",
    days_left : int = 7,
) -> dict:
    """
    Keyword-based router: detects intent and delegates to the right function.
    Returns {intent, message, result}.
    """
    q = query.lower()

    # ── Flashcard intent ──────────────────────────────────────────────────────
    if any(kw in q for kw in ["flashcard", "flash card", "flash cards"]):
        logger.info("Copilot intent → FLASHCARD")
        if not notes_text.strip():
            return {
                "intent" : "flashcard",
                "message": "Please provide your notes so I can generate flashcards.",
                "result" : None,
            }
        result = _generate_flashcards(notes_text)
        return {
            "intent" : "flashcard",
            "message": f"Generated {len(result)} flashcard(s) from your notes!",
            "result" : result,
        }

    # ── Quiz intent ───────────────────────────────────────────────────────────
    if any(kw in q for kw in ["quiz", "mcq", "multiple choice", "question", "test"]):
        logger.info("Copilot intent → QUIZ")
        if not notes_text.strip():
            return {
                "intent" : "quiz",
                "message": "Please provide your notes so I can generate a quiz.",
                "result" : None,
            }
        result = _generate_quiz(notes_text)
        return {
            "intent" : "quiz",
            "message": f"Generated {len(result)} MCQ(s) from your notes!",
            "result" : result,
        }

    # ── Study plan intent ─────────────────────────────────────────────────────
    if any(kw in q for kw in ["study plan", "plan", "schedule", "timetable", "roadmap", "revision"]):
        logger.info("Copilot intent → STUDY PLAN")
        resolved_subject = subject
        if not resolved_subject:
            m = re.search(r"for\s+(.+?)(?:\s+exam|\s+in\s+\d|\s*$)", q)
            resolved_subject = m.group(1).strip().title() if m else "General Exam Preparation"
        result = _generate_study_plan(resolved_subject, days_left)
        return {
            "intent" : "study_plan",
            "message": f"Here is your {days_left}-day study plan for {resolved_subject}!",
            "result" : result,
        }

    # ── Unknown ───────────────────────────────────────────────────────────────
    logger.info("Copilot intent → UNKNOWN")
    return {
        "intent" : "unknown",
        "message": (
            "I'm not sure what you need. Try:\n"
            "• 'Generate flashcards from my notes'\n"
            "• 'Create a quiz from my notes'\n"
            "• 'Make a study plan for Computer Networks in 5 days'"
        ),
        "result" : None,
    }


# =============================================================================
# API Endpoints
# =============================================================================

# ── Health Check ──────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model = HealthResponse,
    summary        = "Health Check",
    tags           = ["System"],
)
async def health_check():
    """Returns service status. Used by uptime monitors and the React frontend."""
    return HealthResponse(
        status  = "ok",
        service = "CampusOS Exam Prep API",
        model   = MODEL_NAME,
    )


# ── POST /flashcards ──────────────────────────────────────────────────────────

@app.post(
    "/flashcards",
    response_model  = FlashcardResponse,
    status_code     = status.HTTP_200_OK,
    summary         = "Generate Flashcards",
    tags            = ["Exam Prep"],
    responses       = {
        422: {"description": "Validation error — check request body"},
        500: {"description": "Gemini API or parsing error"},
    },
)
async def flashcards_endpoint(req: FlashcardRequest):
    """
    Generate study flashcards from raw notes.

    - **notes_text**: Your study notes (plain text, min 10 chars)

    Returns a list of `{question, answer}` objects.
    """
    logger.info("POST /flashcards — notes length: %d", len(req.notes_text))
    try:
        cards = _generate_flashcards(req.notes_text)
        return FlashcardResponse(
            flashcards = [FlashcardItem(**c) for c in cards],
            count      = len(cards),
        )
    except ValueError as e:
        logger.warning("Flashcard generation ValueError: %s", e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error("Flashcard generation error: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── POST /quiz ────────────────────────────────────────────────────────────────

@app.post(
    "/quiz",
    response_model  = QuizResponse,
    status_code     = status.HTTP_200_OK,
    summary         = "Generate Quiz (MCQs)",
    tags            = ["Exam Prep"],
    responses       = {
        422: {"description": "Validation error — check request body"},
        500: {"description": "Gemini API or parsing error"},
    },
)
async def quiz_endpoint(req: QuizRequest):
    """
    Generate multiple-choice questions from raw notes.

    - **notes_text**: Your study notes (plain text, min 10 chars)
    - **num_questions**: How many MCQs to generate (1–20, default 10)

    Returns a list of `{question, options[4], answer}` objects.
    """
    logger.info(
        "POST /quiz — notes length: %d, num_questions: %d",
        len(req.notes_text), req.num_questions,
    )
    try:
        questions = _generate_quiz(req.notes_text, req.num_questions)
        return QuizResponse(
            quiz  = [QuizItem(**q) for q in questions],
            count = len(questions),
        )
    except ValueError as e:
        logger.warning("Quiz generation ValueError: %s", e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error("Quiz generation error: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── POST /studyplan ───────────────────────────────────────────────────────────

@app.post(
    "/studyplan",
    response_model  = StudyPlanResponse,
    status_code     = status.HTTP_200_OK,
    summary         = "Generate Study Plan",
    tags            = ["Exam Prep"],
    responses       = {
        422: {"description": "Validation error — check request body"},
        500: {"description": "Gemini API or parsing error"},
    },
)
async def studyplan_endpoint(req: StudyPlanRequest):
    """
    Generate a day-wise study plan for an upcoming exam.

    - **subject**: The subject or topic (e.g. "Computer Networks")
    - **days_left**: Number of days before the exam (1–60)

    Returns a `{Day 1: ..., Day 2: ...}` plan.
    """
    logger.info(
        "POST /studyplan — subject: '%s', days_left: %d",
        req.subject, req.days_left,
    )
    try:
        plan = _generate_study_plan(req.subject, req.days_left)
        return StudyPlanResponse(
            study_plan = plan,
            subject    = req.subject,
            days_left  = req.days_left,
        )
    except ValueError as e:
        logger.warning("Study plan ValueError: %s", e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error("Study plan error: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── POST /copilot ─────────────────────────────────────────────────────────────

@app.post(
    "/copilot",
    response_model  = CopilotResponse,
    status_code     = status.HTTP_200_OK,
    summary         = "AI Copilot (Natural Language Router)",
    tags            = ["Copilot"],
    responses       = {
        422: {"description": "Validation error — check request body"},
        500: {"description": "Gemini API or parsing error"},
    },
)
async def copilot_endpoint(req: CopilotRequest):
    """
    Natural-language AI Copilot that routes requests to the right module.

    Examples:
    - *"Generate flashcards from my notes"* → calls `/flashcards` logic
    - *"Create a quiz from my notes"*       → calls `/quiz` logic
    - *"Make a study plan for CN exam"*     → calls `/studyplan` logic

    - **query**: What you want to do (natural language)
    - **notes_text**: Your notes (needed for flashcard/quiz intents)
    - **subject**: Subject name (needed for study plan intent)
    - **days_left**: Days until exam (for study plan intent, default 7)
    """
    logger.info("POST /copilot — query: '%s'", req.query)
    try:
        result = _ai_copilot(
            query      = req.query,
            notes_text = req.notes_text or "",
            subject    = req.subject or "",
            days_left  = req.days_left or 7,
        )
        return CopilotResponse(
            intent   = result["intent"],
            message  = result["message"],
            response = result["result"],
        )
    except ValueError as e:
        logger.warning("Copilot ValueError: %s", e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error("Copilot error: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))