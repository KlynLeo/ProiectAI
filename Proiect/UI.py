import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
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


# -------------------------
# Theme
# -------------------------
APP_STYLESHEET = """
QMainWindow { background: #0B1220; }
QWidget { color: #E8EEF7; font-size: 14px; }
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
QLabel#Title { font-size: 28px; font-weight: 700; }
QLabel#Section { font-weight: 700; }
QLabel#Badge {
    padding: 6px 10px;
    border-radius: 10px;
    background: rgba(136,192,208,0.2);
    border: 1px solid rgba(136,192,208,0.4);
}
QPushButton {
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}
QPushButton#Primary {
    background: rgba(136,192,208,0.3);
    border: 1px solid rgba(136,192,208,0.6);
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


# -------------------------
# Pages
# -------------------------
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

        left = QTextEdit()
        left.setReadOnly(True)
        splitter.addWidget(left)
        self.problem = left

        right = QTextEdit()
        splitter.addWidget(right)
        self.answer = right

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
        self.problem.setPlainText(f"{q['question']}\n\n{q.get('instance','')}")
        self.answer.clear()


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
        total = 0
        for q, a in zip(qs, ans):
            s = score_question(q, a)
            total += s
            lbl = QLabel(f"{q['question']} → {s}%")
            self.list.addWidget(lbl)
        self.score.setText(f"Final Score: {total // len(qs)}%")


# -------------------------
# Main
# -------------------------
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
        QMessageBox.information(self, "Answer", q["answer"])

    def restart(self):
        self.stack.setCurrentWidget(self.start)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
