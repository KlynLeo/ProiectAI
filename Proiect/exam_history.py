import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("exam_history.json")


def load_history():
    if not HISTORY_FILE.exists():
        return {"exams": []}

    with HISTORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def append_exam(questions: list[dict]):
    history = load_history()

    exam_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "questions": questions
    }

    history["exams"].append(exam_entry)
    save_history(history)
