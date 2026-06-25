"""
sir9tui v2 — Persistent storage with SQLite + JSON.
Built by Nenifix

SQLite: User profiles, quiz attempts, progress tracking
JSON:   Curriculum content, user settings, session history
"""
import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class Sir9Database:
    """
    SQLite database for persistent user progress and quiz results.
    sir9tui v2 — Built by Nenifix
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = Path.home() / ".local" / "share" / "sir9" / "sir9.db"
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                last_login TEXT DEFAULT (datetime('now')),
                total_score INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                selected_option INTEGER NOT NULL,
                is_correct INTEGER NOT NULL,
                timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                completion_percent REAL DEFAULT 0.0,
                questions_answered INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                last_accessed TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, module_id)
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_name TEXT NOT NULL,
                badge_description TEXT DEFAULT '',
                awarded_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_attempts(user_id);
            CREATE INDEX IF NOT EXISTS idx_progress_user ON user_progress(user_id);
        """)
        self.conn.commit()

    def create_user(self, username: str, full_name: str = "") -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, full_name) VALUES (?, ?)",
                (username, full_name)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            return cursor.fetchone()[0]

    def get_user(self, username: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_user_stats(self, user_id: int, correct: int = 0, total: int = 0):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users SET 
                total_score = total_score + ?,
                total_questions = total_questions + ?,
                correct_answers = correct_answers + ?,
                last_login = datetime('now')
            WHERE id = ?
        """, (correct, total, correct, user_id))
        self.conn.commit()

    def record_quiz_attempt(self, user_id: int, module_id: int, question_id: int,
                            selected_option: int, is_correct: bool):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO quiz_attempts (user_id, module_id, question_id, selected_option, is_correct)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, module_id, question_id, selected_option, int(is_correct)))

        # Update progress
        cursor.execute("""
            INSERT INTO user_progress (user_id, module_id, questions_answered, last_accessed)
            VALUES (?, ?, 1, datetime('now'))
            ON CONFLICT(user_id, module_id) DO UPDATE SET
                questions_answered = questions_answered + 1,
                last_accessed = datetime('now')
        """, (user_id, module_id))

        self.conn.commit()
        self.update_user_stats(user_id, correct=int(is_correct), total=1)

    def get_user_progress(self, user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT up.*, m.title as module_title
            FROM user_progress up
            LEFT JOIN (SELECT id, title FROM (SELECT 1 as id, 'Introduction to STEM' as title)) m
            ON up.module_id = m.id
            WHERE up.user_id = ?
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_user_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT qa.*, m.title as module_title
            FROM quiz_attempts qa
            LEFT JOIN (SELECT id, title FROM (SELECT 1 as id, 'Introduction to STEM' as title)) m
            ON qa.module_id = m.id
            WHERE qa.user_id = ?
            ORDER BY qa.timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def award_badge(self, user_id: int, badge_name: str, badge_description: str = ""):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO achievements (user_id, badge_name, badge_description)
            VALUES (?, ?, ?)
        """, (user_id, badge_name, badge_description))
        self.conn.commit()

    def get_achievements(self, user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM achievements WHERE user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self, user_id: int) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {}
        return dict(user)

    def close(self):
        self.conn.close()
