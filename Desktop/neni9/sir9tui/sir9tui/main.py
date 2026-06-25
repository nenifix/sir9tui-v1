"""
Textual TUI main app for sir9 — offline AI STEM tutor.
Built by Nenifix v2 — LM Studio integration
"""
import asyncio
import json
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App
from textual.widgets import Label, Static, Button, Header, Footer
from textual.containers import Container
from textual.screen import Screen
from textual.binding import Binding
from textual.css.query import NoMatches

LM_STUDIO_URL = "http://127.0.0.1:1234"
LM_STUDIO_MODEL = "liquid/lfm2.5-1.2b"


async def ask_lm_studio(prompt: str, system_prompt: str = "You are sir9, an AI STEM tutor. Answer briefly and clearly.") -> str:
    """Send a message to LM Studio and return the response."""
    payload = json.dumps({
        "model": LM_STUDIO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False
    }).encode()

    req = urllib.request.Request(
        f"{LM_STUDIO_URL}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "No response")
            return "No response from model"
    except Exception as e:
        return f"Error connecting to LM Studio: {e}"

class sir9UI(App):
    """
    Main sir9 terminal UI application.
    """

    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("s", "open_settings", "Settings"),
    ]

    def __init__(self):
        super().__init__()
        self.current_user: Optional[Dict[str, Any]] = None
        self.status_bar = Label("Ready", name="status_bar")
        
        # Simple curriculum for testing
        self.curriculum_data = {
            "title": "Introduction to STEM",
            "description": "Basic concepts and history of Science, Technology, Engineering, and Mathematics",
            "learning_objectives": ["Understand STEM meaning", "Identify basic STEM careers"],
            "content_text": "# Introduction to STEM\n\n## What is STEM?\nSTEM is an acronym that stands for Science, Technology, Engineering, and Mathematics. These four disciplines are interconnected and form the foundation of modern innovation and problem-solving."
        }

    async def action_quit_app(self) -> None:
        """Quit the application."""
        self.exit()

    async def action_open_settings(self) -> None:
        """Open settings."""
        pass

    def compose(self):
        """Compose the UI layout."""
        yield Header()
        yield Container(
            Label("Welcome to sir9 - AI STEM Tutor", id="title"),
            Label("Built by Nenifix", id="brand"),
            Static(self.curriculum_data["content_text"], id="content"),
            Button("Start Learning", id="start_btn"),
            Button("View Quiz", id="quiz_btn"),
            id="main_content"
        )
        yield self.status_bar
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = "sir9 — Built by Nenifix"
        self.status_bar.update("Ready to learn. Press 's' for settings or 'q' to quit.")

    def on_start_btn_clicked(self) -> None:
        """Handle start learning button."""
        self.status_bar.update("Loading AI content...")
        self.query_one("#content", Static).update("Asking LM Studio to explain STEM...")

        async def get_explanation():
            response = await ask_lm_studio(
                "Explain what STEM is in 3 sentences for a student in Ghana.",
                "You are sir9, an AI STEM tutor for Ghanaian students. Use simple language and local examples."
            )
            self.query_one("#content", Static).update(response)
            self.status_bar.update("Ready. Press 's' for settings or 'q' to quit.")

        self.run_worker(get_explanation())

    def on_quiz_btn_clicked(self) -> None:
        """Handle quiz button."""
        self.status_bar.update("Loading quiz questions...")
        self.query_one("#content", Static).update("Quiz will show questions from curriculum here.")

if __name__ == "__main__":
    app = sir9UI()
    app.run()