
const pdfFile = document.getElementById("pdfFile");
const generateBtn = document.getElementById("generateBtn");
const status = document.getElementById("status");
const quizForm = document.getElementById("quizForm");
const questionsContainer = document.getElementById("questions");
const results = document.getElementById("results");
const score = document.getElementById("score");
const review = document.getElementById("review");

const API_URL = "http://127.0.0.1:8000";

let currentQuizId = null;
let quizQuestions = [];

async function getErrorMessage(response) {
    const data = await response.json().catch(() => null);

    if (data?.detail) {
        if (typeof data.detail === "string") {
            return data.detail;
        }

        return JSON.stringify(data.detail);
    }

    return `Request failed with status ${response.status}`;
}

generateBtn.addEventListener("click", async () => {
    if (!pdfFile.files.length) {
        status.textContent = "Please select a PDF first.";
        return;
    }

    const file = pdfFile.files[0];

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        status.textContent = "Please select a PDF file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    generateBtn.disabled = true;
    quizForm.hidden = true;
    results.hidden = true;
    status.textContent = "Generating your quiz. Please wait.";

    try {
        const response = await fetch(`${API_URL}/generate-quiz`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(await getErrorMessage(response));
        }

        const data = await response.json();

        if (
            !data.quiz_id ||
            !Array.isArray(data.questions) ||
            data.questions.length !== 5 ||
            data.questions.some(
                question =>
                    typeof question.question !== "string" ||
                    !Array.isArray(question.options) ||
                    question.options.length !== 4
            )
        ) {
            throw new Error("The server returned an invalid quiz.");
        }

        currentQuizId = data.quiz_id;
        quizQuestions = data.questions;
        questionsContainer.replaceChildren();

        quizQuestions.forEach((question, index) => {
            const card = document.createElement("section");
            card.className = "question";

            const heading = document.createElement("h3");
            heading.textContent = `${index + 1}. ${question.question}`;
            card.appendChild(heading);

            question.options.forEach((option, optionIndex) => {
                const label = document.createElement("label");
                label.className = "option";

                const radio = document.createElement("input");
                radio.type = "radio";
                radio.name = `question-${index}`;
                radio.value = optionIndex;
                radio.required = true;

                const text = document.createElement("span");
                text.textContent = option;

                label.append(radio, text);
                card.appendChild(label);
            });

            questionsContainer.appendChild(card);
        });

        quizForm.hidden = false;
        status.textContent =
            "Quiz generated successfully. Select one answer for each question.";
    } catch (error) {
        status.textContent = `Generation error: ${error.message}`;
    } finally {
        generateBtn.disabled = false;
    }
});

quizForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentQuizId) {
        status.textContent = "Please generate a new quiz first.";
        return;
    }

    const answers = [];

    for (let index = 0; index < quizQuestions.length; index++) {
        const selected = document.querySelector(
            `input[name="question-${index}"]:checked`
        );

        if (!selected) {
            status.textContent = `Please answer question ${index + 1}.`;
            return;
        }

        answers.push(Number(selected.value));
    }

    const submitButton = quizForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    status.textContent = "Evaluating your answers.";
    results.hidden = true;

    try {
        const response = await fetch(`${API_URL}/evaluate-quiz`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                quiz_id: currentQuizId,
                answers
            })
        });

        if (!response.ok) {
            throw new Error(await getErrorMessage(response));
        }

        const data = await response.json();

        const percentage = data.total > 0
            ? Math.round((data.score / data.total) * 100)
            : 0;

        let performanceMessage = "Keep practising!";

        if (percentage === 100) {
            performanceMessage = "Perfect score! Excellent work.";
        } else if (percentage >= 80) {
            performanceMessage = "Great job!";
        } else if (percentage >= 60) {
            performanceMessage = "Good effort. Keep improving!";
        }

        score.textContent =
            `Score: ${data.score}/${data.total} | ${percentage}% — ${performanceMessage}`;

        review.replaceChildren();

        data.results.forEach((item, index) => {
            const card = document.createElement("section");
            card.className = "question";

            const heading = document.createElement("h3");
            heading.textContent = `${index + 1}. ${item.question}`;
            card.appendChild(heading);

            const selectedOption =
                quizQuestions[index].options[item.selected_answer];

            const correctOption =
                quizQuestions[index].options[item.correct_answer];

            const selectedText = document.createElement("p");
            selectedText.textContent = `Your answer: ${selectedOption}`;
            selectedText.className = item.correct ? "correct" : "incorrect";
            card.appendChild(selectedText);

            if (!item.correct) {
                const correctText = document.createElement("p");
                correctText.textContent = `Correct answer: ${correctOption}`;
                correctText.className = "correct";
                card.appendChild(correctText);
            }

            const explanation = document.createElement("p");
            explanation.textContent =
                `Explanation: ${item.explanation || "No explanation provided."}`;
            card.appendChild(explanation);

            review.appendChild(card);
        });

        results.hidden = false;
        status.textContent = "Evaluation complete.";
    } catch (error) {
        status.textContent = `Evaluation error: ${error.message}`;
    } finally {
        submitButton.disabled = false;
    }
});
