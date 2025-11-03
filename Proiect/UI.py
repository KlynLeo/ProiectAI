import tkinter as tk
from tkinter import ttk, font, messagebox
from logic import Exam

# -------------------
# Setup exam instance
# -------------------
exam = Exam()

# -------------------
# Initialize UI
# -------------------
root = tk.Tk()
root.title("SmarTest - Search Problem Identification")
root.geometry("1000x650")
root.configure(bg="#2E3440")
root.resizable(False, False)

title_font = font.Font(family="Helvetica", size=22, weight="bold")
label_font = font.Font(family="Helvetica", size=14)
button_font = font.Font(family="Helvetica", size=14, weight="bold")

# -------------------
# Frames
# -------------------
start_frame = tk.Frame(root, bg="#3B4252", padx=50, pady=50)
start_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(start_frame, text="SmarTest - Search Problem Identification",
         font=title_font, fg="#ECEFF4", bg="#3B4252").grid(row=0, column=0, columnspan=2, pady=25)

tk.Label(start_frame, text="Number of Questions:",
         font=label_font, fg="#ECEFF4", bg="#3B4252").grid(row=1, column=0, sticky="w", pady=15)

num_questions_var = tk.IntVar(value=2)
num_entry = ttk.Entry(start_frame, textvariable=num_questions_var, font=label_font, width=5)
num_entry.grid(row=1, column=1, sticky="w", pady=15)

def start_test():
    num_q = num_questions_var.get()
    exam.select_questions(num_q)
    start_frame.place_forget()
    show_question()

start_btn = tk.Button(start_frame, text="Start Test", font=button_font,
                      bg="#81A1C1", fg="#2E3440", activebackground="#88C0D0",
                      padx=20, pady=10, command=start_test)
start_btn.grid(row=2, column=0, columnspan=2, pady=35)

question_frame = tk.Frame(root, bg="#3B4252", padx=40, pady=40, relief="groove", bd=2)
progress = ttk.Progressbar(root, length=900, mode='determinate')
progress.place(x=50, y=20)

score_frame = None
answer_var = tk.StringVar()

def update_progress():
    progress['maximum'] = len(exam.selected_questions)
    progress['value'] = exam.current_index

def show_question():
    global question_frame
    for widget in question_frame.winfo_children():
        widget.destroy()

    question_frame.place(relx=0.5, rely=0.55, anchor="center")
    update_progress()

    q_data = exam.get_current_question()
    if q_data is None:
        show_results()
        return

    tk.Label(question_frame, text=f"Question {exam.current_index + 1}/{len(exam.selected_questions)}",
             font=title_font, fg="#ECEFF4", bg="#3B4252").pack(pady=(0,10))
    tk.Label(question_frame, text=q_data['question'], font=label_font,
             fg="#D8DEE9", bg="#3B4252", wraplength=850, justify="left").pack(pady=(0,20))

    text_widget = tk.Text(question_frame, width=80, height=6, font=label_font,
                          bd=2, relief="sunken", padx=5, pady=5, wrap="word",
                          bg="#ECEFF4", fg="#2E3440")
    text_widget.pack(pady=5)

    btn_frame = tk.Frame(question_frame, bg="#3B4252")
    btn_frame.pack(pady=25)

    def next_question():
        exam.submit_answer(text_widget.get("1.0", tk.END))
        show_question()

    next_btn = tk.Button(btn_frame, text="Next", font=button_font,
                         bg="#81A1C1", fg="#2E3440", activebackground="#88C0D0",
                         padx=15, pady=8, command=next_question)
    next_btn.pack(side="left", padx=10)

    see_answer_btn = tk.Button(btn_frame, text="Show Correct Answer", font=button_font,
                               bg="#5E81AC", fg="#ECEFF4", activebackground="#81A1C1",
                               padx=15, pady=8,
                               command=lambda: messagebox.showinfo("Correct Answer", q_data["answer"]))
    see_answer_btn.pack(side="left", padx=10)

def show_results():
    global question_frame, score_frame
    question_frame.destroy()
    score_frame = tk.Frame(root, bg="#3B4252", padx=40, pady=40, relief="groove", bd=2)
    score_frame.place(relx=0.5, rely=0.5, anchor="center")

    score = exam.grade()

    tk.Label(score_frame, text="Test Finished", font=title_font, fg="#ECEFF4", bg="#3B4252").pack(pady=(0,20))
    tk.Label(score_frame, text=f"Your Score: {score}%", font=label_font, fg="#D8DEE9", bg="#3B4252").pack(pady=(0,10))

    end_btn = tk.Button(score_frame, text="End Test", font=button_font, bg="#81A1C1", fg="#2E3440",
                        activebackground="#88C0D0", padx=20, pady=10, command=root.destroy)
    end_btn.pack(pady=20)

root.mainloop()
