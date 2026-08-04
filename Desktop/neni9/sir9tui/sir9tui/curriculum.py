"""
Curriculum + quiz engine for sir9 — offline AI STEM tutor.
Built by Nenifix v2 — SQLite + JSON persistence
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import random


class Sir9JSONStore:
    """
    JSON-based storage for user settings, session history, and app config.
    Complements SQLite (which handles structured quiz/progress data).
    """

    def __init__(self, store_path: str = None):
        if store_path is None:
            self.store_path = Path.home() / ".local" / "share" / "sir9" / "sir9_store.json"
        else:
            self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict:
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"users": {}, "sessions": [], "settings": {}, "app_config": {"version": "2.0.0"}}

    def save(self):
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_user_settings(self, username: str) -> Dict:
        return self.data.get("users", {}).get(username, {}).get("settings", {
            "theme": "dark", "language": "en",
            "notifications_enabled": True, "sound_enabled": True
        })

    def set_user_setting(self, username: str, key: str, value: Any):
        if "users" not in self.data:
            self.data["users"] = {}
        if username not in self.data["users"]:
            self.data["users"][username] = {"settings": {}, "profile": {}}
        self.data["users"][username]["settings"][key] = value
        self.save()

    def get_user_profile(self, username: str) -> Dict:
        return self.data.get("users", {}).get(username, {}).get("profile", {
            "full_name": username, "avatar": "default", "bio": "",
            "joined_at": datetime.now().isoformat()
        })

    def set_user_profile(self, username: str, profile: Dict):
        if "users" not in self.data:
            self.data["users"] = {}
        if username not in self.data["users"]:
            self.data["users"][username] = {"settings": {}, "profile": {}}
        self.data["users"][username]["profile"].update(profile)
        self.save()

    def log_session(self, username: str, session_data: Dict):
        if "sessions" not in self.data:
            self.data["sessions"] = []
        entry = {
            "username": username,
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "questions_answered": session_data.get("questions_answered", 0),
            "correct_count": session_data.get("correct_count", 0),
            "modules_accessed": session_data.get("modules_accessed", []),
            "device": session_data.get("device", "desktop")
        }
        self.data["sessions"].append(entry)
        if len(self.data["sessions"]) > 100:
            self.data["sessions"] = self.data["sessions"][-100:]
        self.save()
        return len(self.data["sessions"]) - 1

    def end_session(self, session_index: int):
        if 0 <= session_index < len(self.data.get("sessions", [])):
            self.data["sessions"][session_index]["ended_at"] = datetime.now().isoformat()
            self.save()

    def get_app_setting(self, key: str, default: Any = None) -> Any:
        return self.data.get("app_config", {}).get(key, default)

    def set_app_setting(self, key: str, value: Any):
        if "app_config" not in self.data:
            self.data["app_config"] = {}
        self.data["app_config"][key] = value
        self.save()

    def export_all(self) -> str:
        return json.dumps(self.data, indent=2, ensure_ascii=False)

    def get_session_count(self, username: str) -> int:
        return sum(1 for s in self.data.get("sessions", []) if s.get("username") == username)


@dataclass
class Question:
    id: int
    module_id: int
    question_text: str
    options: List[str]
    correct_option: int
    explanation: str
    difficulty: str
    learning_objective: str


@dataclass
class Module:
    id: int
    title: str
    description: str
    difficulty: str
    estimated_time_minutes: int
    learning_objectives: List[str]
    questions: List[Question]
    content_text: str
    related_concepts: List[str]


class Curriculum:
    """
    Manages curriculum, quizzes, and question bank.
    """

    def __init__(self, curriculum_path: str = None):
        if curriculum_path is None:
            self.curriculum_path = Path.home() / ".local" / "share" / "sir9" / "curriculum.json"
        else:
            self.curriculum_path = Path(curriculum_path)

        self.curriculum_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.curriculum_path.exists():
            self._create_default_curriculum()

        self.modules: Dict[int, Module] = {}
        self.questions_by_module: Dict[int, List[Question]] = {}

        self._load_curriculum()

    def _create_default_curriculum(self) -> None:
        curriculum_data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "modules": [
                {
                    "id": 1,
                    "title": "Introduction to STEM",
                    "description": "Basic concepts and history of Science, Technology, Engineering, and Mathematics",
                    "difficulty": "beginner",
                    "estimated_time_minutes": 30,
                    "learning_objectives": [
                        "Understand what STEM means",
                        "Identify basic STEM careers",
                        "Recognize STEM in daily life"
                    ],
                    "questions": [
                        {
                            "id": 1, "module_id": 1,
                            "question_text": "What does the acronym STEM stand for?",
                            "options": [
                                "Science, Technology, Engineering, Mathematics",
                                "Software, Technology, Electronics, Mechanics",
                                "Science, Technology, Engineering, Medicine",
                                "Social, Technical, Economic, Mathematical"
                            ],
                            "correct_option": 0,
                            "explanation": "STEM stands for Science, Technology, Engineering, and Mathematics.",
                            "difficulty": "easy",
                            "learning_objective": "Understand STEM acronym definition"
                        },
                        {
                            "id": 2, "module_id": 1,
                            "question_text": "Which of these is NOT typically considered a STEM field?",
                            "options": ["Biology", "Chemistry", "History", "Physics"],
                            "correct_option": 2,
                            "explanation": "History is generally considered a humanities discipline rather than a core STEM field.",
                            "difficulty": "medium",
                            "learning_objective": "Distinguish between STEM and non-STEM fields"
                        },
                        {
                            "id": 3, "module_id": 1,
                            "question_text": "Which STEM field is primarily concerned with the study of living organisms?",
                            "options": ["Physics", "Chemistry", "Biology", "Mathematics"],
                            "correct_option": 2,
                            "explanation": "Biology is the branch of science that deals with the study of living organisms.",
                            "difficulty": "easy",
                            "learning_objective": "Identify major STEM disciplines"
                        }
                    ],
                    "content_text": "# Introduction to STEM\n\n## What is STEM?\nSTEM is an acronym that stands for Science, Technology, Engineering, and Mathematics. These four disciplines are interconnected and form the foundation of modern innovation and problem-solving.\n\n## Why STEM Matters\nSTEM education is crucial because it develops critical thinking, problem-solving skills, and prepares students for careers in growing fields.\n\n## STEM in Daily Life\nYou encounter STEM every day:\n- **Science**: Understanding how things work\n- **Technology**: Using computers and smartphones\n- **Engineering**: Building and designing solutions\n- **Mathematics**: Calculating and measuring\n\n## Career Opportunities\n- **Scientists**: Researchers\n- **Engineers**: Designers and problem-solvers\n- **Technologists**: Software developers\n- **Mathematicians**: Analysts, data scientists",
                    "related_concepts": ["Science", "Technology", "Engineering", "Mathematics"]
                }
            ]
        }

        with open(self.curriculum_path, "w", encoding="utf-8") as f:
            json.dump(curriculum_data, f, indent=2)

    def _load_curriculum(self) -> None:
        try:
            with open(self.curriculum_path, "r", encoding="utf-8") as f:
                curriculum_data = json.load(f)
            self.modules.clear()
            self.questions_by_module.clear()
            for module_data in curriculum_data.get("modules", []):
                raw_questions = module_data.get("questions", [])
                questions = [
                    Question(
                        id=q.get("id"),
                        module_id=q.get("module_id", module_data.get("id")),
                        question_text=q.get("question_text", ""),
                        options=list(q.get("options", [])),
                        correct_option=q.get("correct_option", 0),
                        explanation=q.get("explanation", ""),
                        difficulty=q.get("difficulty", "medium"),
                        learning_objective=q.get("learning_objective", ""),
                    )
                    for q in raw_questions
                ]
                module = Module(
                    id=module_data.get("id"),
                    title=module_data.get("title", "Untitled"),
                    description=module_data.get("description", ""),
                    difficulty=module_data.get("difficulty", "beginner"),
                    estimated_time_minutes=module_data.get("estimated_time_minutes", 30),
                    learning_objectives=list(module_data.get("learning_objectives", [])),
                    questions=questions,
                    content_text=module_data.get("content_text", ""),
                    related_concepts=list(module_data.get("related_concepts", [])),
                )
                self.modules[module.id] = module
                self.questions_by_module[module.id] = questions
        except Exception as e:
            print(f"Error loading curriculum: {e}")
            self.modules = {}
            self.questions_by_module = {}

    def get_modules(self) -> List[Dict[str, Any]]:
        modules = []
        for module in self.modules.values():
            modules.append({
                "id": module.id, "title": module.title,
                "description": module.description, "difficulty": module.difficulty,
                "estimated_time_minutes": module.estimated_time_minutes,
                "learning_objectives": module.learning_objectives,
                "question_count": len(module.questions),
                "related_concepts": module.related_concepts
            })
        return sorted(modules, key=lambda x: x["id"])

    def get_module(self, module_id: int) -> Optional[Dict[str, Any]]:
        if module_id not in self.modules:
            return None
        module = self.modules[module_id]
        return {
            "id": module.id, "title": module.title,
            "description": module.description, "difficulty": module.difficulty,
            "estimated_time_minutes": module.estimated_time_minutes,
            "learning_objectives": module.learning_objectives,
            "questions": [
                {"id": q.id, "question_text": q.question_text, "options": q.options,
                 "correct_option": q.correct_option, "explanation": q.explanation,
                 "difficulty": q.difficulty, "learning_objective": q.learning_objective}
                for q in module.questions
            ],
            "content_text": module.content_text,
            "related_concepts": module.related_concepts
        }

    def get_questions_for_module(self, module_id: int) -> List[Dict[str, Any]]:
        if module_id not in self.questions_by_module:
            return []
        questions = self.questions_by_module[module_id]
        return [
            {"id": q.id, "module_id": q.module_id, "question_text": q.question_text,
             "options": q.options, "correct_option": q.correct_option,
             "explanation": q.explanation, "difficulty": q.difficulty,
             "learning_objective": q.learning_objective}
            for q in questions
        ]

    def check_answer(self, module_id: int, question_id: int, answer: Any) -> Dict[str, Any]:
        if module_id not in self.questions_by_module:
            return {"correct": False, "error": f"Module {module_id} not found"}
        questions = self.questions_by_module[module_id]
        question = None
        for q in questions:
            if q.id == question_id:
                question = q
                break
        if not question:
            return {"correct": False, "error": f"Question {question_id} not found"}
        is_correct = False
        if isinstance(answer, str) and answer.isdigit():
            answer_index = int(answer) - 1
        elif isinstance(answer, int):
            answer_index = answer
        else:
            try:
                answer_index = question.options.index(answer)
            except ValueError:
                return {"correct": False, "correct_answer": question.correct_option,
                        "user_answer": answer, "explanation": question.explanation,
                        "is_match": False, "message": "Your answer doesn't match any option"}
        if isinstance(question.correct_option, str) and question.correct_option.isdigit():
            correct_index = int(question.correct_option) - 1
        else:
            correct_index = question.correct_option
        is_correct = answer_index == correct_index
        return {
            "correct": is_correct,
            "correct_option": question.correct_option,
            "user_option": answer if isinstance(answer, int) else int(answer) - 1,
            "explanation": question.explanation if is_correct else None,
            "difficulty": question.difficulty,
            "learning_objective": question.learning_objective,
            "message": "Correct!" if is_correct else "Incorrect."
        }

    def get_random_questions(self, module_id: int, count: int = 5) -> List[Dict[str, Any]]:
        if module_id not in self.questions_by_module:
            return []
        questions = self.questions_by_module[module_id]
        if len(questions) < count:
            count = len(questions)
        selected_indices = random.sample(range(len(questions)), count)
        return [
            {"id": questions[idx].id, "module_id": questions[idx].module_id,
             "question_text": questions[idx].question_text, "options": questions[idx].options,
             "correct_option": questions[idx].correct_option, "explanation": questions[idx].explanation,
             "difficulty": questions[idx].difficulty, "learning_objective": questions[idx].learning_objective}
            for idx in selected_indices
        ]

    def get_questions_by_difficulty(self, module_id: int, difficulty: str) -> List[Dict[str, Any]]:
        if module_id not in self.questions_by_module:
            return []
        questions = self.questions_by_module[module_id]
        filtered = [q for q in questions if q.difficulty == difficulty]
        return [
            {"id": q.id, "module_id": q.module_id, "question_text": q.question_text,
             "options": q.options, "correct_option": q.correct_option,
             "explanation": q.explanation, "difficulty": q.difficulty,
             "learning_objective": q.learning_objective}
            for q in filtered
        ]

    def get_difficulties_for_module(self, module_id: int) -> List[str]:
        if module_id not in self.questions_by_module:
            return []
        questions = self.questions_by_module[module_id]
        return sorted(list(set(q.difficulty for q in questions)))

    def close(self) -> None:
        self.modules.clear()
        self.questions_by_module.clear()
