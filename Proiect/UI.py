import tkinter as tk
from tkinter import ttk, font, messagebox

from exam import Exam
from search_problem_identification.search_logic import compare_search_answers
from nash_equilibrum.nash_logic import evaluate_nash_answer, extract_equilibria
from minimax.minimax_logic import evaluate_minimax_answer

# =====================
# INIT EXAM
# =====================
exam = Exam()

# =====================
# MAIN WINDOW
# =====================
root = tk.Tk()
root.title("SmarTest - Search Problem Identification & Game Theory")
root.geometry("1000x650")
root.configure(bg="#2E3440")
root.resizable(False, False)

title_font = font.Font(family="Helvetica", size=22, weight="bold")
label_font = font.Font(family="Helvetica", size=14)
button_font = font.Font(family="Helvetica", size=14, weight="bold")

# =====================
# START FRAME
# =====================
start_frame = tk.Frame(root, bg="#3B4252", padx=50, pady=50)
start_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(
    start_frame,
    text="SmarTest - Question Generator",
    font=title_font,
    fg="#ECEFF4",
    bg="#3B4252"
).grid(row=0, column=0, columnspan=2, pady=25)

tk.Label(
    start_frame,
    text="Number of Questions:",
    font=label_font,
    fg="#ECEFF4",
    bg="#3B4252"
).grid(row=1, column=0, sticky="w", pady=15)

num_questions_var = tk.IntVar(value=3)
num_entry = ttk.Entry(start_frame, textvariable=num_questions_var, font=label_font, width=5)
num_entry.grid(row=1, column=1, sticky="w", pady=15)

# =====================
# CHECKBOXES
# =====================
search_var = tk.BooleanVar(value=True)
nash_var = tk.BooleanVar(value=True)
minimax_var = tk.BooleanVar(value=True)

tk.Checkbutton(
    start_frame, text="Search Problems", variable=search_var,
    font=label_font, fg="#ECEFF4", bg="#3B4252",
    selectcolor="#3B4252", activebackground="#3B4252"
).grid(row=2, column=0, sticky="w", pady=5)

tk.Checkbutton(
    start_frame, text="Nash Equilibrium", variable=nash_var,
    font=label_font, fg="#ECEFF4", bg="#3B4252",
    selectcolor="#3B4252", activebackground="#3B4252"
).grid(row=3, column=0, sticky="w", pady=5)

tk.Checkbutton(
    start_frame, text="Minimax (Alpha-Beta)", variable=minimax_var,
    font=label_font, fg="#ECEFF4", bg="#3B4252",
    selectcolor="#3B4252", activebackground="#3B4252"
).grid(row=4, column=0, sticky="w", pady=5)

# =====================
# START TEST
# =====================
def start_test():
    num_q = num_questions_var.get()

    if not (search_var.get() or nash_var.get() or minimax_var.get()):
        messagebox.showerror("Error", "Please select at least one problem type.")
        return

    exam.select_questions(
        num_q,
        include_search=search_var.get(),
        include_nash=nash_var.get(),
        include_minimax=minimax_var.get()
    )

    start_frame.place_forget()
    show_question()

start_btn = tk.Button(
    start_frame, text="Start Test", font=button_font,
    bg="#81A1C1", fg="#2E3440", activebackground="#88C0D0",
    padx=20, pady=10, command=start_test
)
start_btn.grid(row=5, column=0, columnspan=2, pady=35)

# =====================
# QUESTION FRAME
# =====================
question_frame = tk.Frame(root, bg="#3B4252", padx=40, pady=40, relief="groove", bd=2)

progress = ttk.Progressbar(root, length=900, mode='determinate')
progress.place(x=50, y=20)

def update_progress():
    progress['maximum'] = len(exam.questions)
    progress['value'] = exam.current_index

def show_question():
    for widget in question_frame.winfo_children():
        widget.destroy()

    question_frame.place(relx=0.5, rely=0.55, anchor="center")
    update_progress()

    q_data = exam.get_current_question()
    if q_data is None:
        show_results()
        return

    tk.Label(
        question_frame,
        text=f"Question {exam.current_index + 1}/{len(exam.questions)}",
        font=title_font, fg="#ECEFF4", bg="#3B4252"
    ).pack(pady=(0, 10))

    tk.Label(
        question_frame,
        text=q_data["question"],
        font=label_font,
        fg="#D8DEE9",
        bg="#3B4252",
        wraplength=850,
        justify="left"
    ).pack(pady=(5, 10))

    if "instance" in q_data:
        tk.Label(
            question_frame,
            text=q_data["instance"],
            font=("Courier New", 14),
            fg="#ECEFF4",
            bg="#3B4252",
            justify="left",
            anchor="w"
        ).pack(pady=(0, 20))

    text_widget = tk.Text(
        question_frame, width=80, height=6,
        font=label_font, bd=2, relief="sunken",
        padx=5, pady=5, wrap="word",
        bg="#ECEFF4", fg="#2E3440"
    )
    text_widget.pack(pady=5)

    def next_question():
        exam.submit_answer(text_widget.get("1.0", tk.END))
        show_question()

    btn_frame = tk.Frame(question_frame, bg="#3B4252")
    btn_frame.pack(pady=25)

    tk.Button(
        btn_frame, text="Next", font=button_font,
        bg="#81A1C1", fg="#2E3440", activebackground="#88C0D0",
        padx=15, pady=8, command=next_question
    ).pack(side="left", padx=10)

    tk.Button(
        btn_frame, text="Show Correct Answer", font=button_font,
        bg="#5E81AC", fg="#ECEFF4", activebackground="#81A1C1",
        padx=15, pady=8,
        command=lambda: messagebox.showinfo("Correct Answer", q_data["answer"])
    ).pack(side="left", padx=10)

# =====================
# RESULTS
# =====================
def show_results():
    question_frame.destroy()

    score_frame = tk.Frame(root, bg="#3B4252", padx=40, pady=40)
    score_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        score_frame, text="Test Finished",
        font=title_font, fg="#ECEFF4", bg="#3B4252"
    ).pack(pady=(0, 20))

    total_score = 0

    for q, ans in zip(exam.questions, exam.user_answers):
        if q["type"] == "search":
            score = compare_search_answers(ans, q["answer"])
        elif q["type"] == "nash":
            score = evaluate_nash_answer(ans, extract_equilibria(q["answer"]))
        else:  # minimax
            score = evaluate_minimax_answer(ans, q["answer"])

        total_score += score

    final_score = total_score // len(exam.questions)

    tk.Label(
        score_frame, text=f"Final Score: {final_score}%",
        font=title_font, fg="#88C0D0", bg="#3B4252"
    ).pack(pady=20)

    tk.Button(
        score_frame, text="End Test", font=button_font,
        bg="#81A1C1", fg="#2E3440",
        activebackground="#88C0D0", padx=20, pady=10,
        command=root.destroy
    ).pack(pady=20)

root.mainloop()
