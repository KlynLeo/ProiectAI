
class Exam:
    def __init__(self, questions_data):
        self.questions_data = questions_data
        self.selected_questions = []
        self.user_answers = []
        self.current_index = 0

    def select_questions(self, chapter, num_questions):
        if chapter not in self.questions_data:
            raise ValueError("Invalid chapter")
        self.selected_questions = self.questions_data[chapter][:num_questions]
        self.user_answers = [""] * len(self.selected_questions)
        self.current_index = 0

    def get_current_question(self):
        """Return the current question dict or None if done."""
        if self.current_index >= len(self.selected_questions):
            return None
        return self.selected_questions[self.current_index]

    def submit_answer(self, answer):
        if self.current_index < len(self.selected_questions):
            self.user_answers[self.current_index] = answer.strip()
            self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.selected_questions)

    def grade(self):
        if not self.selected_questions:
            return 0
        score = 0
        for q, ans in zip(self.selected_questions, self.user_answers):
            if ans.lower() == q['answer'].lower():
                score += 1
        return int((score / len(self.selected_questions)) * 100)

questions_data = {
    "Chapter 1": [
        {"type": "open", "question": "Explain the Turing Test.", "answer": "A test for AI intelligence."},
        {"type": "mcq", "question": "Which is a search algorithm?", "options": ["DFS", "TCP", "HTTP"], "answer": "DFS"}
    ],
    "Chapter 2": [
        {"type": "open", "question": "Define supervised learning.", "answer": "Learning from labeled data."},
        {"type": "mcq", "question": "Which is a neural network type?", "options": ["CNN", "FTP", "SMTP"], "answer": "CNN"}
    ]
}
