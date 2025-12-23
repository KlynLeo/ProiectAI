import sys
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QSpinBox, QMessageBox, QTextEdit, QProgressBar, QScrollArea,
    QFrame, QSizePolicy, QSplitter
)

from exam import Exam
from search_problem_identification.search_logic import compare_search_answers
from nash_equilibrum.nash_logic import evaluate_nash_answer, extract_equilibria
from csp.csp_logic import evaluate_csp_answer


# -------------------------
# Theme / Styling
# -------------------------
APP_STYLESHEET = """
QMainWindow {
    background: #0B1220;
}

QWidget {
    color: #E8EEF7;
    font-size: 14px;
}

/* Card containers */
QFrame#Card {
    background: #101A2E;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
}

QFrame#SubCard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
}

QLabel#Title {
    font-size: 28px;
    font-weight: 700;
}

QLabel#Subtitle {
    font-size: 14px;
    color: rgba(232,238,247,0.72);
}

QLabel#Section {
    font-size: 14px;
    font-weight: 700;
    color: rgba(232,238,247,0.90);
}

QLabel#Badge {
    padding: 6px 10px;
    border-radius: 10px;
    font-weight: 700;
    background: rgba(136, 192, 208, 0.14);
    border: 1px solid rgba(136, 192, 208, 0.30);
    color: #88C0D0;
}

QPushButton {
    background: rgba(129, 161, 193, 0.18);
    border: 1px solid rgba(129, 161, 193, 0.35);
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}

QPushButton:hover {
    background: rgba(129, 161, 193, 0.28);
}

QPushButton:pressed {
    background: rgba(129, 161, 193, 0.35);
}

QPushButton#Primary {
    background: rgba(136, 192, 208, 0.22);
    border: 1px solid rgba(136, 192, 208, 0.45);
}

QPushButton#Danger {
    background: rgba(191, 97, 106, 0.18);
    border: 1px solid rgba(191, 97, 106, 0.40);
}

QTextEdit {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 10px;
}

QProgressBar {
    height: 10px;
    border-radius: 6px;
    background: rgba(255,255,255,0.08);
}

QProgressBar::chunk {
    border-radius: 6px;
    background: rgba(136, 192, 208, 0.75);
}

QScrollArea {
    border: none;
    background: transparent;
}
"""


def make_card_layout(title: str, subtitle: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("Card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(12)

    title_lbl = QLabel(title)
    title_lbl.setObjectName("Title")
    layout.addWidget(title_lbl)

    if subtitle:
        sub_lbl = QLabel(subtitle)
        sub_lbl.setObjectName("Subtitle")
        sub_lbl.setWordWrap(True)
        layout.addWidget(sub_lbl)

    return card, layout


def wrap_in_scroll(widget: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(widget)
    return scroll


def score_question(q, ans: str) -> int:
    if q["type"] == "search":
        return compare_search_answers(ans, q["answer"])
    if q["type"] == "nash":
        correct_eq = extract_equilibria(q["answer"])
        return evaluate_nash_answer(ans, correct_eq)
    if q["type"] == "csp":
        return evaluate_csp_answer(ans, q["answer"])
    return 0


# -------------------------
# Pages
# -------------------------
class StartPage(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start
        strong_number_font = QFont()
        strong_number_font.setPointSize(16)
        strong_number_font.setWeight(QFont.Bold)


        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        card, layout = make_card_layout(
            "SmarTest",
            "Modern generator for Search Problems, Nash Equilibrium, and CSP Backtracking variants (FC / MRV / AC-3)."
        )
        root.addWidget(card, 1, alignment=Qt.AlignCenter)
        card.setMaximumWidth(780)

        # Controls
        controls = QFrame()
        controls.setObjectName("SubCard")
        c = QVBoxLayout(controls)
        c.setContentsMargins(16, 16, 16, 16)
        c.setSpacing(10)
        layout.addWidget(controls)

        row1 = QHBoxLayout()
        lbl = QLabel("Number of questions")
        lbl.setObjectName("Section")
        row1.addWidget(lbl)

        self.spin = QSpinBox()
        self.spin.setRange(1, 50)
        self.spin.setValue(5)
        self.spin.setFixedWidth(90)
        self.spin.setFont(strong_number_font)
        self.spin.setStyleSheet("""
            QSpinBox {
                color: #ECEFF4;
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 10px;
                padding: 6px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                background: transparent;
            }
        """)
        row1.addStretch(1)
        row1.addWidget(self.spin)
        c.addLayout(row1)

        self.cb_search = QCheckBox("Search Problems")
        self.cb_search.setChecked(True)
        self.cb_nash = QCheckBox("Nash Equilibrium")
        self.cb_nash.setChecked(True)
        self.cb_csp = QCheckBox("CSP (Backtracking: FC / MRV / AC-3)")
        self.cb_csp.setChecked(True)

        c.addWidget(self.cb_search)
        c.addWidget(self.cb_nash)
        c.addWidget(self.cb_csp)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.start_btn = QPushButton("Start Test")
        self.start_btn.setObjectName("Primary")
        self.start_btn.clicked.connect(self._start_clicked)
        btn_row.addWidget(self.start_btn)

        c.addLayout(btn_row)

    def _start_clicked(self):
        n = int(self.spin.value())
        include_search = self.cb_search.isChecked()
        include_nash = self.cb_nash.isChecked()
        include_csp = self.cb_csp.isChecked()

        if not (include_search or include_nash or include_csp):
            QMessageBox.critical(self, "Error", "Please select at least one problem type.")
            return

        self.on_start(n, include_search, include_nash, include_csp)


class QuestionPage(QWidget):
    def __init__(self, on_next, on_show_answer):
        super().__init__()
        self.on_next = on_next
        self.on_show_answer = on_show_answer

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # Top bar: progress + title row
        top = QFrame()
        top.setObjectName("Card")
        top_l = QVBoxLayout(top)
        top_l.setContentsMargins(16, 14, 16, 14)
        top_l.setSpacing(10)

        title_row = QHBoxLayout()
        self.q_index_lbl = QLabel("Question 1 / 1")
        self.q_index_lbl.setObjectName("Section")
        title_row.addWidget(self.q_index_lbl)
        title_row.addStretch(1)
        self.badge = QLabel("")
        self.badge.setObjectName("Badge")
        self.badge.hide()
        title_row.addWidget(self.badge)
        top_l.addLayout(title_row)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        top_l.addWidget(self.progress)

        root.addWidget(top)

        # Main split
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        # Left card (problem)
        left_card = QFrame()
        left_card.setObjectName("Card")
        left = QVBoxLayout(left_card)
        left.setContentsMargins(16, 16, 16, 16)
        left.setSpacing(10)

        problem_lbl = QLabel("Problem")
        problem_lbl.setObjectName("Section")
        left.addWidget(problem_lbl)

        self.problem_text = QLabel("")
        self.problem_text.setWordWrap(True)
        self.problem_text.setStyleSheet("color: rgba(232,238,247,0.92);")
        left.addWidget(self.problem_text)

        self.instance_edit = QTextEdit()
        self.instance_edit.setReadOnly(True)
        self.instance_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.instance_edit.setMinimumHeight(220)
        left.addWidget(self.instance_edit, 1)

        splitter.addWidget(left_card)

        # Right card (answer)
        right_card = QFrame()
        right_card.setObjectName("Card")
        right = QVBoxLayout(right_card)
        right.setContentsMargins(16, 16, 16, 16)
        right.setSpacing(10)

        answer_lbl = QLabel("Your Answer")
        answer_lbl.setObjectName("Section")
        right.addWidget(answer_lbl)

        self.hint_lbl = QLabel("")
        self.hint_lbl.setWordWrap(True)
        self.hint_lbl.setStyleSheet("color: rgba(232,238,247,0.70);")
        right.addWidget(self.hint_lbl)

        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("Type your answer here…")
        right.addWidget(self.answer_edit, 1)

        btn_row = QHBoxLayout()
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("Primary")
        self.next_btn.clicked.connect(self._next_clicked)

        self.show_btn = QPushButton("Show Answer")
        self.show_btn.clicked.connect(self._show_clicked)

        btn_row.addWidget(self.show_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.next_btn)
        right.addLayout(btn_row)

        splitter.addWidget(right_card)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        # Make monospace nicer for instance
        mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        mono.setPointSize(12)
        self.instance_edit.setFont(mono)

    def _next_clicked(self):
        self.on_next(self.answer_edit.toPlainText())

    def _show_clicked(self):
        self.on_show_answer()

    def set_question(self, idx: int, total: int, q_data: dict):
        self.q_index_lbl.setText(f"Question {idx} / {total}")
        self.progress.setMaximum(total)
        self.progress.setValue(idx - 1)

        # Badge for CSP algorithm (or type)
        if q_data.get("type") == "csp":
            alg = q_data.get("algorithm", "").strip()
            self.badge.setText(f"Backtracking + {alg}")
            self.badge.show()
        elif q_data.get("type") == "nash":
            self.badge.setText("Nash (Pure)")
            self.badge.show()
        elif q_data.get("type") == "search":
            self.badge.setText("Search")
            self.badge.show()
        else:
            self.badge.hide()

        self.problem_text.setText(q_data.get("question", ""))

        instance = q_data.get("instance", "")
        self.instance_edit.setPlainText(instance)

        # Contextual hint
        if q_data.get("type") == "nash":
            self.hint_lbl.setText("Format: a Python list of tuples, e.g. [(A1, B2)] or [(A1, B2), (A2, B1)].")
        elif q_data.get("type") == "csp":
            self.hint_lbl.setText("Format: {'A': 1, 'B': 3, 'C': 5} or A=1, B=3, C=5. Use 'None' if no solution.")
        else:
            self.hint_lbl.setText("")

        self.answer_edit.clear()


class ResultsPage(QWidget):
    def __init__(self, on_restart, on_exit):
        super().__init__()
        self.on_restart = on_restart
        self.on_exit = on_exit

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        top_card, top = make_card_layout("Results", "Review each question below. Your final score is the average.")
        root.addWidget(top_card)

        self.score_lbl = QLabel("Final Score: 0%")
        self.score_lbl.setObjectName("Title")
        top.addWidget(self.score_lbl)

        # Scrollable list
        self.scroll_host = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_host)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.addStretch(1)

        root.addWidget(wrap_in_scroll(self.scroll_host), 1)

        # Bottom buttons
        btn_row = QHBoxLayout()
        restart_btn = QPushButton("Restart")
        restart_btn.setObjectName("Primary")
        restart_btn.clicked.connect(self.on_restart)

        exit_btn = QPushButton("Exit")
        exit_btn.setObjectName("Danger")
        exit_btn.clicked.connect(self.on_exit)

        btn_row.addWidget(exit_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(restart_btn)

        root.addLayout(btn_row)

    def set_results(self, questions: list[dict], answers: list[str]):
        # Clear old cards
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        total = 0
        for i, (q, ans) in enumerate(zip(questions, answers), start=1):
            s = score_question(q, ans)
            total += s

            card = QFrame()
            card.setObjectName("Card")
            card_l = QVBoxLayout(card)
            card_l.setContentsMargins(16, 14, 16, 14)
            card_l.setSpacing(10)

            header = QHBoxLayout()
            title = QLabel(f"Question {i}")
            title.setObjectName("Section")
            header.addWidget(title)
            header.addStretch(1)

            badge = QLabel(f"{s}%")
            badge.setObjectName("Badge")
            header.addWidget(badge)

            card_l.addLayout(header)

            # Problem
            q_lbl = QLabel(q.get("question", ""))
            q_lbl.setWordWrap(True)
            q_lbl.setStyleSheet("color: rgba(232,238,247,0.88);")
            card_l.addWidget(q_lbl)

            # Correct / Yours
            sub = QFrame()
            sub.setObjectName("SubCard")
            sub_l = QVBoxLayout(sub)
            sub_l.setContentsMargins(12, 12, 12, 12)
            sub_l.setSpacing(8)

            correct = QLabel(f"Correct: {q.get('answer', '')}")
            correct.setWordWrap(True)
            correct.setStyleSheet("color: rgba(163, 190, 140, 0.95); font-weight: 700;")
            sub_l.addWidget(correct)

            yours = QLabel(f"Yours: {ans.strip()}")
            yours.setWordWrap(True)
            yours.setStyleSheet("color: rgba(235, 203, 139, 0.92);")
            sub_l.addWidget(yours)

            card_l.addWidget(sub)

            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

        final_score = int(total / max(1, len(questions)))
        self.score_lbl.setText(f"Final Score: {final_score}%")

class AnswerDialog(QMainWindow):
    def __init__(self, answer_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Correct Answer")
        self.setMinimumSize(520, 420)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Correct Answer")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("Review the expected solution for this question.")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(subtitle)

        # Card
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        label = QLabel("Answer")
        label.setObjectName("Section")
        card_layout.addWidget(label)

        # Scrollable text
        answer_edit = QTextEdit()
        answer_edit.setReadOnly(True)
        answer_edit.setPlainText(answer_text)
        answer_edit.setMinimumHeight(220)

        # Monospace improves CSP/Nash readability
        mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        mono.setPointSize(12)
        answer_edit.setFont(mono)

        card_layout.addWidget(answer_edit)

        layout.addWidget(card, 1)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("Primary")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

# -------------------------
# Main Window
# -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.exam = Exam()

        self.setWindowTitle("SmarTest")
        self.setMinimumSize(1100, 720)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage(self.start_test)
        self.question_page = QuestionPage(self.next_question, self.show_answer)
        self.results_page = ResultsPage(self.restart, self.close)

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.question_page)
        self.stack.addWidget(self.results_page)

        self.stack.setCurrentWidget(self.start_page)

    def start_test(self, n, include_search, include_nash, include_csp):
        self.exam.select_questions(n, include_search, include_nash, include_csp)
        self.stack.setCurrentWidget(self.question_page)
        self.render_current_question()

    def render_current_question(self):
        q = self.exam.get_current_question()
        if q is None:
            self.show_results()
            return

        idx = self.exam.current_index + 1
        total = len(self.exam.questions)
        self.question_page.set_question(idx, total, q)

    def next_question(self, user_text: str):
        self.exam.submit_answer(user_text)
        self.render_current_question()

    def show_answer(self):
        q = self.exam.get_current_question()
        if not q:
            return

        dialog = AnswerDialog(q.get("answer", ""), parent=self)
        dialog.show()


    def show_results(self):
        self.results_page.set_results(self.exam.questions, self.exam.user_answers)
        self.stack.setCurrentWidget(self.results_page)

    def restart(self):
        # Reset to start page
        self.stack.setCurrentWidget(self.start_page)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
