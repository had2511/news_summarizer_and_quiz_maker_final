import google.generativeai as genai
import os
from dotenv import load_dotenv

# ✅ Load API key from .env file (safe & hidden)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ✅ Initialize Gemini model once
quiz_model = genai.GenerativeModel("models/gemini-2.5-flash")

def load_quiz_model():
    """Return None (for compatibility) and the Gemini model."""
    return None, quiz_model


def generate_quiz(_, model, summary_text, num_questions=3):
    """Generate MCQs from a given news summary using Gemini."""
    try:
        prompt = f"""
        You are a quiz maker AI. Based on the following news summary:
        "{summary_text}"

        Generate {num_questions} multiple-choice questions.
        Follow this exact format for each question:

        Question: <question text>
        A) <option 1>
        B) <option 2>
        C) <option 3>
        D) <option 4>
        Answer: <correct option letter>
        """

        response = model.generate_content(prompt)
        quiz_text = response.text.strip()

        # ✅ Parse output
        quizzes = []
        current_q = {"question": "", "options": [], "answer": ""}
        for line in quiz_text.splitlines():
            line = line.strip()
            if line.lower().startswith("question"):
                if current_q["question"]:
                    quizzes.append(current_q)
                    current_q = {"question": "", "options": [], "answer": ""}
                current_q["question"] = line.split(":", 1)[-1].strip()

            elif line[:2] in ["A)", "B)", "C)", "D)"]:
                current_q["options"].append(line[3:].strip())

            elif line.lower().startswith("answer"):
                current_q["answer"] = line.split(":", 1)[-1].strip()

        if current_q["question"]:
            quizzes.append(current_q)

        # ✅ Fallback for empty or malformed output
        if not quizzes:
            raise ValueError("No valid quiz found.")

        return quizzes[:num_questions]

    except Exception as e:
        return [{
            "question": f"⚠️ Error generating quiz: {e}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "A"
        }]
