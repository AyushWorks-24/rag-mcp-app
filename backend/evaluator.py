
class QuizEvaluator:
    def evaluate(self, questions: list[dict], answers: list[int]) -> dict:
        if len(answers) != len(questions):
            raise ValueError("Please answer all 5 questions.")

        results = []
        score = 0

        for index, question in enumerate(questions):
            selected = answers[index]
            correct_answer = question["correct_answer"]

            if not isinstance(selected, int) or selected not in range(4):
                raise ValueError("Each answer must be an option number from 0 to 3.")

            is_correct = selected == correct_answer

            if is_correct:
                score += 1

            results.append({
                "question": question["question"],
                "selected_answer": selected,
                "correct_answer": correct_answer,
                "correct": is_correct,
                "explanation": question.get("explanation", "")
            })

        return {
            "score": score,
            "total": len(questions),
            "results": results
        }
