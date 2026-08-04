"""
sir9tui — offline AI STEM tutor. Textual TUI. Built by Nenifix.
Fixed v1.1.0: working entry point, offline AI fallback, quiz engine, settings,
progress tracking, multi-module curriculum, cross-platform paths.
"""
from __future__ import annotations

import asyncio
import json
import urllib.request
from pathlib import Path
from typing import Optional

from textual.app import App
from textual.widgets import Label, Static, Button, Header, Footer, Input, Select
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding

from .database import Sir9Database
from .curriculum import Curriculum

try:
    from . import __version__
except Exception:  # pragma: no cover
    __version__ = "1.1.0"

LM_STUDIO_URL = "http://127.0.0.1:1234"
LM_STUDIO_MODEL = "liquid/lfm2.5-1.2b"
LM_STUDIO_TIMEOUT = 120


def lm_studio_available() -> bool:
    """Return True if an LM Studio / OpenAI-compatible server is responding on :1234."""
    try:
        req = urllib.request.Request(f"{LM_STUDIO_URL}/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


async def ask_lm_studio(prompt: str, system_prompt: str = "You are sir9, an AI STEM tutor. Answer briefly and clearly.") -> str:
    """Send a message to LM Studio (OpenAI-compatible) and return the response."""
    payload = json.dumps({
        "model": LM_STUDIO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{LM_STUDIO_URL}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=LM_STUDIO_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "No response")
            return "No response from model"
    except Exception as e:
        return f"Error connecting to LM Studio: {e}"


# Offline fallback: a small local answer bank so sir9 still works with no LLM.
OFFLINE_ANSWERS = {
    "stem": (
        "STEM stands for Science, Technology, Engineering and Mathematics. "
        "These four disciplines work together to build the modern world — from "
        "phones and bridges to the medicine we take. In Ghana, STEM skills power "
        "industries from banking apps to cocoa processing, and it all starts with "
        "curiosity and practice."
    ),
    "science": (
        "Science is the study of how the natural world works. It uses observation, "
        "experiments and evidence — for example, testing which soil grows the best "
        "maize, or how rain forms over the coast."
    ),
    "technology": (
        "Technology is using knowledge to create tools that solve problems — "
        "computers, mobile money apps like MoMo, solar panels and farm machines. "
        "It turns ideas into things people can actually use."
    ),
    "engineering": (
        "Engineering is designing and building solutions: bridges, roads, cars, "
        "and even software. Engineers apply maths and science to make things "
        "strong, safe and useful — like Ghana's Akosombo Dam."
    ),
    "mathematics": (
        "Mathematics is the language of patterns, numbers and logic. It's how we "
        "measure, predict and build — from counting market change to designing "
        "rockets. Every STEM field leans on maths."
    ),
    "career": (
        "STEM careers include scientists (biologists, chemists, physicists), "
        "engineers (civil, electrical, software), technologists (developers, "
        "network specialists) and mathematicians (data scientists, analysts). "
        "In Ghana, growing fields include AI, fintech, renewable energy and agritech."
    ),
    "quiz": (
        "In quiz mode you answer multiple-choice questions and sir9 tracks your "
        "progress and score. Try the Quiz button to begin!"
    ),
}

DEFAULT_OFFLINE_ANSWER = (
    "sir9 is in offline mode — no AI model detected. Start LM Studio (or another "
    "OpenAI-compatible server on port 1234) for AI answers. Meanwhile, ask about "
    "STEM, science, technology, engineering, mathematics, careers or quizzes."
)


def offline_ask(prompt: str) -> str:
    """Local keyword-based answer for offline mode."""
    text = prompt.lower()
    for key, answer in OFFLINE_ANSWERS.items():
        if key in text:
            return answer
    return DEFAULT_OFFLINE_ANSWER


class QuizState:
    """Tracks the active quiz for one module."""

    def __init__(self, questions):
        self.questions = list(questions)
        self.index = 0
        self.correct = 0
        self.answered = 0

    @property
    def current(self):
        if not self.questions:
            return None
        return self.questions[self.index]

    def answer(self, option_index: int) -> dict:
        q = self.current
        if q is None:
            return {}
        self.answered += 1
        is_correct = option_index == int(q["correct_option"])
        if is_correct:
            self.correct += 1
        self.index += 1
        return {
            "question": q["question_text"],
            "chosen": q["options"][option_index],
            "correct": is_correct,
            "answer": q["options"][int(q["correct_option"])],
            "explanation": q["explanation"],
        }


class sir9UI(App):
    """
    Main sir9 terminal UI application (fixed v1.1.0).
    """

    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("s", "open_settings", "Settings"),
        Binding("m", "toggle_modules", "Modules"),
        Binding("1,2,3,4", "press_option", "Answer"),
    ]

    def __init__(self):
        super().__init__()
        self.db: Optional[Sir9Database] = None
        self.store = None
        self.curriculum: Optional[Curriculum] = None
        self.current_user_id: Optional[int] = None
        self.current_username: str = "student"
        self.status_bar = Label("Loading sir9…", name="status_bar")
        self.quiz: Optional[QuizState] = None
        self.online = False
        self.settings_open = False

    # ---------- lifecycle ----------

    async def on_mount(self) -> None:
        self.title = "sir9 — Built by Nenifix"
        self.db = Sir9Database()
        self.curriculum = Curriculum()
        self.current_user_id = self.db.create_user(self.current_username, "Sir9 Student")
        self.online = lm_studio_available()
        mode = "AI online (LM Studio)" if self.online else "OFFLINE mode — no AI server detected"
        self.status_bar.update(f"Ready. {mode}. 's' settings, 'm' modules, 'q' quit.")
        if not self.online:
            self.notify(
                "No LM Studio detected on port 1234 — running in offline mode with built-in answers.",
                title="sir9 offline mode",
                timeout=8,
            )

    def on_unmount(self) -> None:
        if self.db:
            self.db.close()

    # ---------- actions ----------

    def action_quit_app(self) -> None:
        self.exit()

    def action_toggle_modules(self) -> None:
        self.compose_modules_screen()

    def action_open_settings(self) -> None:
        self.compose_settings_screen()

    def action_press_option(self, option: str) -> None:
        if self.quiz and self.quiz.current is not None:
            self.answer_quiz(int(option) - 1)

    # ---------- screens ----------

    def compose(self):
        yield Header()
        yield Container(
            Label("Welcome to sir9 — AI STEM Tutor", id="title"),
            Label("Built by Nenifix · offline-first", id="brand"),
            Static(
                "# Introduction to STEM\n\nAsk sir9 anything, or start a lesson.",
                id="content",
                markup=True,
            ),
            Horizontal(
                Button("Start Learning", id="start_btn", variant="primary"),
                Button("View Quiz", id="quiz_btn"),
                Button("Modules", id="modules_btn"),
                id="btn_row",
            ),
            id="main_content",
        )
        yield self.status_bar
        yield Footer()

    def compose_modules_screen(self) -> None:
        if not self.curriculum:
            return
        self.settings_open = False
        self.quiz = None
        modules = self.curriculum.get_modules()
        options = [(str(m["id"]), m["title"]) for m in modules]
        self.query_one("#content", Static).update(
            "Select a module to load its lesson.\n\n" +
            "\n".join(f"{m['id']}. {m['title']} — {m['description']}" for m in modules)
        )
        self.status_bar.update("Modules: type a module number (e.g. 1) to open it, or 'q' to quit.")
        self.module_options = options

    def compose_settings_screen(self) -> None:
        self.settings_open = True
        self.quiz = None
        self.query_one("#content", Static).update(
            "Settings — sir9 v1.1.0\n\n"
            f"AI mode: {'LM Studio online' if self.online else 'Offline (built-in answers)'}\n"
            f"Model: {LM_STUDIO_MODEL}\n"
            f"Server: {LM_STUDIO_URL}\n"
            f"Student: {self.current_username}\n\n"
            "Press 's' again to close settings."
        )
        self.status_bar.update("Settings. Press 's' to close.")

    # ---------- button handlers ----------

    def on_modules_btn_clicked(self) -> None:
        self.compose_modules_screen()

    def on_start_btn_clicked(self) -> None:
        self.quiz = None
        self.settings_open = False
        self.status_bar.update("Loading AI content…")
        self.query_one("#content", Static).update("Asking sir9 to explain STEM…")

        async def get_explanation():
            prompt = (
                "Explain what STEM is in 3 sentences for a student in Ghana. "
                "Then name 3 STEM careers they can pursue."
            )
            if self.online:
                response = await ask_lm_studio(
                    prompt,
                    "You are sir9, an AI STEM tutor for Ghanaian students. "
                    "Use simple language and local examples.",
                )
            else:
                await asyncio.sleep(0.1)
                response = offline_ask(prompt)
            self.query_one("#content", Static).update(response)
            self.status_bar.update("Ready. 's' settings · 'm' modules · 'q' quit.")

        self.run_worker(get_explanation())

    def on_quiz_btn_clicked(self) -> None:
        if not self.curriculum:
            return
        self.settings_open = False
        modules = self.curriculum.get_modules()
        if not modules:
            self.status_bar.update("No modules available.")
            return
        first = modules[0]
        questions = self.curriculum.get_questions_for_module(first["id"])
        if not questions:
            self.status_bar.update("No questions in this module.")
            return
        self.quiz = QuizState(questions)
        self.status_bar.update(
            f"Quiz: {first['title']} — answer with keys 1–{len(self.quiz.questions[0]['options'])}. 'q' quits."
        )
        self.show_question()

    def show_question(self) -> None:
        q = self.quiz.current
        if q is None:
            self.finish_quiz()
            return
        lines = [f"[b]{q['question_text']}[/b]", ""]
        for i, opt in enumerate(q["options"], start=1):
            lines.append(f"  {i}. {opt}")
        lines.append("")
        lines.append("Press 1–4 to answer.")
        self.query_one("#content", Static).update("\n".join(lines))

    def answer_quiz(self, option_index: int) -> None:
        result = self.quiz.answer(option_index)
        if not result:
            return
        question = self.quiz.questions[self.quiz.index - 1] if self.quiz.index > 0 else None
        qid = question["id"] if question else 0
        mid = question["module_id"] if question else 1
        self.db.record_quiz_attempt(
            self.current_user_id, mid, qid, option_index, bool(result["correct"]),
        )
        lines = [
            ("[green]Correct![/green]" if result["correct"] else "[red]Incorrect.[/red]"),
            "",
            f"Answer: {result['answer']}",
            f"Explanation: {result['explanation'] or '—'}",
            f"Score: {self.quiz.correct}/{self.quiz.answered}",
            "",
        ]
        if self.quiz.current is None:
            lines.append("Quiz complete! Press any key to continue.")
        else:
            lines.append("Press Enter for next question.")
        self.query_one("#content", Static).update("\n".join(lines))
        self.status_bar.update(f"Quiz {self.quiz.answered}/{len(self.quiz.questions)} · {self.quiz.correct} correct")

    def finish_quiz(self) -> None:
        total = len(self.quiz.questions)
        pct = int((self.quiz.correct / total) * 100) if total else 0
        summary = (
            f"[b]Quiz complete![/b]\n\n"
            f"Score: {self.quiz.correct}/{total} ({pct}%)\n\n"
            f"Keep practising — press 'm' for modules or 's' for settings."
        )
        self.query_one("#content", Static).update(summary)
        self.status_bar.update(f"Quiz done: {self.quiz.correct}/{total}. 'm' modules, 'q' quit.")
        self.quiz = None

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Allow typing module numbers to open a module."""
        val = event.value.strip()
        if val.isdigit() and getattr(self, "module_options", None):
            mid = int(val)
            match = [opt for opt in self.module_options if int(opt[0]) == mid]
            if match:
                self.open_module(mid)
        event.input.value = ""

    def open_module(self, module_id: int) -> None:
        if not self.curriculum:
            return
        module = self.curriculum.get_module(module_id)
        if not module:
            self.status_bar.update("Module not found.")
            return
        self.quiz = None
        self.settings_open = False
        self.query_one("#content", Static).update(module["content_text"] or "No content.")
        lines = [f"[b]{module['title']}[/b]", module["description"], ""]
        self.status_bar.update(
            f"Module {module_id}: {module['title']} — type 'quiz' + module number or press Quiz to test yourself."
        )


def main() -> None:
    """Entry point used by the console script."""
    app = sir9UI()
    app.run()


if __name__ == "__main__":
    main()
