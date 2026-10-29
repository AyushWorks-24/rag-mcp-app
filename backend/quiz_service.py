
import json
import os
import random
import re
from groq import Groq
from dotenv import load_dotenv
from rag_engine import RAGEngine

load_dotenv()


class QuizService:
    def __init__(self):
        self.client = Groq()
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.rag = RAGEngine()
        self.quizzes = {}

    def generate_quiz(self, document_id: str):
        context_chunks = self.rag.retrieve(
            document_id,
            "Identify the most important concepts, definitions, facts, processes, examples, and key ideas in this document for an educational quiz.",
            top_k=8
        )

        if not context_chunks:
            raise ValueError("No relevant content found in this PDF.")

        context = "\n\n".join(context_chunks)

        prompt = f"""
Create exactly 5 high-quality educational multiple-choice questions using only the supplied document context.

Requirements:
- Test understanding of important concepts, not just trivial personal details.
- Prefer meaningful concepts, definitions, applications, and facts.
- Avoid questions about email addresses, phone numbers, or personal details unless essential to the document's educational subject.
- Every question must have exactly 4 distinct and plausible options.
- Exactly one option must be correct.
- Distractors must be clearly incorrect according to the context.
- Avoid duplicate or nearly identical questions.
- Keep questions and explanations concise.
- The explanation must support the correct answer using the context.
- correct_answer must be an integer from 0 to 3 representing the correct option's index.
- Return valid JSON only, without markdown fences.

Required JSON format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Document context:
{context}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You create accurate educational MCQs grounded only in the provided source text. Return valid JSON and never invent facts."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )

        content = response.choices[0].message.content or ""
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                raise ValueError("The AI returned an invalid quiz format. Please try again.")
            data = json.loads(match.group(0))

        questions = data.get("questions", [])

        if not isinstance(questions, list) or len(questions) != 5:
            raise ValueError("The AI must generate exactly 5 questions. Please try again.")

        seen_questions = set()

        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("The AI returned an invalid question.")

            text = question.get("question")
            options = question.get("options")
            answer = question.get("correct_answer")
            explanation = question.get("explanation", "")

            if not isinstance(text, str) or not text.strip():
                raise ValueError("A question has missing text.")

            if not isinstance(options, list) or len(options) != 4:
                raise ValueError("Every question must have exactly 4 options.")

            if not all(isinstance(option, str) and option.strip() for option in options):
                raise ValueError("Every option must contain valid text.")

            if len({option.strip().casefold() for option in options}) != 4:
                raise ValueError("A question contains duplicate options. Please generate the quiz again.")

            if isinstance(answer, bool) or not isinstance(answer, int) or answer not in range(4):
                raise ValueError("A question has an invalid correct answer.")

            normalized_question = re.sub(r"\W+", " ", text.casefold()).strip()

            if normalized_question in seen_questions:
                raise ValueError("Duplicate questions were generated. Please try again.")

            seen_questions.add(normalized_question)
            question["question"] = text.strip()
            question["options"] = options
            question["explanation"] = explanation if isinstance(explanation, str) else ""

        positions = [0, 1, 2, 3, random.randrange(4)]
        random.shuffle(positions)

        for question, target_position in zip(questions, positions):
            original_options = question["options"]
            correct_option = original_options[question["correct_answer"]]
            distractors = [
                option for index, option in enumerate(original_options)
                if index != question["correct_answer"]
            ]
            random.shuffle(distractors)

            shuffled_options = []
            distractor_index = 0

            for index in range(4):
                if index == target_position:
                    shuffled_options.append(correct_option)
                else:
                    shuffled_options.append(distractors[distractor_index])
                    distractor_index += 1

            question["options"] = shuffled_options
            question["correct_answer"] = target_position

        return questions
