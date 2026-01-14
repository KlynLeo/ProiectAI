import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QSpinBox, QMessageBox, QTextEdit, QProgressBar, QScrollArea,
    QFrame, QSplitter
)

from exam import Exam
from search_problem_identification.search_logic import compare_search_answers
from nash_equilibrum.nash_logic import evaluate_nash_answer, extract_equilibria
from minimax.minimax_logic import evaluate_minimax_answer
from csp.csp_logic import evaluate_csp_answer


# -------------------------------------------------
# THEME (dark blue, readable)
# -------------------------------------------------
APP_STYLESHEET = """
QMainWindow {
    background: #0D1B2A;
}

QWidget {
    color: #E6EDF6;
    font-size: 14px;
}

/* Cards */
QFrame#Card {
    background: #1B263B;
    border: 1px solid #415A77;
    border-radius: 16px;
}

/* Titles */
QLabel#Title {
    font-size: 28px;
    font-weight: 700;
    color: #E6EDF6;
}

QLabel {
    color: #E6EDF6;
}

/* Inputs */
QTextEdit, QLineEdit {
    background: #FFFFFF;
    color: #000000;
    border: 1px solid #778DA9;
    border-radius: 8px;
    padding: 8px;
}

QSpinBox {
    background: #FFFFFF;
    color: #000000;
    border: 1px solid #778DA9;
    border-radius: 8px;
    padding: 4px;
}

/* Checkboxes */
QCheckBox {
    color: #E6EDF6;
}

/* Progress bar */
QProgressBar {
    background: #1B263B;
    border: 1px solid #415A77;
    border-radius: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #4F7DF3;
}

/* Buttons */
QPushButton {
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
    background: #415A77;
    color: #E6EDF6;
    border: 1px solid #778DA9;
}

QPushButton#Primary {
    background: #4F7DF3;
    color: #FFFFFF;
    border: none;
}
"""


def wrap_scroll(widget: QWidget) -> QScrollArea:
    s = QScrollArea()
    s.setWidgetResizable(True)
    s.setWidget(widget)
    return s


def score_question(q, ans: str) -> int:
    if q["type"] == "search":
        return compare_search_answers(ans, q["answer"])
    if q["type"] == "nash":
        return evaluate_nash_answer(ans, extract_equilibria(q["answer"]))
    if q["type"] == "minimax":
        return evaluate_minimax_answer(ans, q["answer"])
    if q["type"] == "csp":
        return evaluate_csp_answer(ans, q["answer"])
    return 0


# -------------------------------------------------
# START PAGE
# -------------------------------------------------
class StartPage(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start

        root = QVBoxLayout(self)
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)

        title = QLabel("SmarTest")
        title.setObjectName("Title")
        layout.addWidget(title)

        self.spin = QSpinBox()
        self.spin.setRange(1, 50)
        self.spin.setValue(5)
        layout.addWidget(self.spin)

        self.cb_search = QCheckBox("Search")
        self.cb_nash = QCheckBox("Nash")
        self.cb_minimax = QCheckBox("Minimax (Alpha-Beta)")
        self.cb_csp = QCheckBox("CSP")

        for cb in (self.cb_search, self.cb_nash, self.cb_minimax, self.cb_csp):
            cb.setChecked(True)
            layout.addWidget(cb)

        btn = QPushButton("Start Test")
        btn.setObjectName("Primary")
        btn.clicked.connect(self.start)
        layout.addWidget(btn)

        root.addWidget(card, alignment=Qt.AlignCenter)

    def start(self):
        if not any([self.cb_search.isChecked(), self.cb_nash.isChecked(),
                    self.cb_minimax.isChecked(), self.cb_csp.isChecked()]):
            QMessageBox.critical(self, "Error", "Select at least one type")
            return

        self.on_start(
            self.spin.value(),
            self.cb_search.isChecked(),
            self.cb_nash.isChecked(),
            self.cb_minimax.isChecked(),
            self.cb_csp.isChecked()
        )


# -------------------------------------------------
# QUESTION PAGE
# -------------------------------------------------
class QuestionPage(QWidget):
    def __init__(self, on_next, on_show):
        super().__init__()
        self.on_next = on_next
        self.on_show = on_show

        root = QVBoxLayout(self)

        self.progress = QProgressBar()
        root.addWidget(self.progress)

        splitter = QSplitter()
        root.addWidget(splitter, 1)

        self.problem = QTextEdit()
        self.problem.setReadOnly(True)
        splitter.addWidget(self.problem)

        self.answer = QTextEdit()
        splitter.addWidget(self.answer)

        btns = QHBoxLayout()
        show = QPushButton("Show Answer")
        show.clicked.connect(self.on_show)

        nextb = QPushButton("Next")
        nextb.setObjectName("Primary")
        nextb.clicked.connect(lambda: self.on_next(self.answer.toPlainText()))

        btns.addWidget(show)
        btns.addStretch(1)
        btns.addWidget(nextb)
        root.addLayout(btns)

    def set_question(self, idx, total, q):
        self.progress.setMaximum(total)
        self.progress.setValue(idx - 1)
        self.problem.setPlainText(f"{q['question']}\n\n{q.get('instance', '')}")
        self.answer.clear()


# -------------------------------------------------
# RESULTS PAGE
# -------------------------------------------------
class ResultsPage(QWidget):
    def __init__(self, on_restart):
        super().__init__()
        self.on_restart = on_restart

        root = QVBoxLayout(self)

        self.score = QLabel("Final Score: 0%")
        self.score.setObjectName("Title")
        root.addWidget(self.score)

        self.list = QVBoxLayout()
        host = QWidget()
        host.setLayout(self.list)

        root.addWidget(wrap_scroll(host), 1)

        btn = QPushButton("Restart")
        btn.setObjectName("Primary")
        btn.clicked.connect(self.on_restart)
        root.addWidget(btn)

    def set_results(self, qs, ans):
        while self.list.count():
            item = self.list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total = 0

        for q, user_ans in zip(qs, ans):
            s = score_question(q, user_ans)
            total += s

            card = QFrame()
            card.setObjectName("Card")
            layout = QVBoxLayout(card)

            layout.addWidget(QLabel(f"<b>Întrebare:</b><br>{q['question']}"))
            layout.addWidget(QLabel(
                f"<b>Răspunsul tău:</b><br>"
                f"<span style='color:#FFD166'>{user_ans or '(gol)'}</span>"
            ))
            layout.addWidget(QLabel(
                f"<b>Răspuns corect:</b><br>"
                f"<span style='color:#06D6A0'>{q['answer']}</span>"
            ))
            layout.addWidget(QLabel(f"<b>Scor:</b> {s}%"))

            self.list.addWidget(card)

        self.score.setText(f"Final Score: {total // len(qs)}%")


# -------------------------------------------------
# MAIN WINDOW
# -------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.exam = Exam()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start = StartPage(self.start_test)
        self.qpage = QuestionPage(self.next_q, self.show_ans)
        self.results = ResultsPage(self.restart)

        for w in (self.start, self.qpage, self.results):
            self.stack.addWidget(w)

        self.stack.setCurrentWidget(self.start)

    def start_test(self, n, s, nash, m, csp):
        self.exam.select_questions(n, s, nash, m, csp)
        self.stack.setCurrentWidget(self.qpage)
        self.render()

    def render(self):
        q = self.exam.get_current_question()
        if q is None:
            self.results.set_results(self.exam.questions, self.exam.user_answers)
            self.stack.setCurrentWidget(self.results)
            return
        self.qpage.set_question(self.exam.current_index + 1, len(self.exam.questions), q)

    def next_q(self, txt):
        self.exam.submit_answer(txt)
        self.render()

    def show_ans(self):
        q = self.exam.get_current_question()

        msg = QMessageBox(self)
        msg.setWindowTitle("Answer")
        msg.setText(q["answer"])

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4F7DF3;
                color: #FFFFFF;
                padding: 6px 12px;
                border-radius: 6px;
            }
        """)

        msg.exec()


    def restart(self):
        self.stack.setCurrentWidget(self.start)


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
