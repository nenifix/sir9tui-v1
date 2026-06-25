# sir9tui — Technical Stack Report
> June 24, 2026 | Built by Nenifix

---

## Language & Runtime
- **Python 3.14** (system Python at `C:\Users\ai9\AppData\Local\Microsoft\WindowsApps\python3.exe`)

## TUI Framework
- **Textual** v0.62 — Terminal UI framework (`pip install textual`)
- **Rich** v15.0 — Text rendering engine (dependency of textual)
- **markdown-it-py** v4.2 — Markdown rendering in TUI

## AI / LLM Backend
- **LM Studio** — Local LLM server at `http://127.0.0.1:1234`
- **Model in use**: `liquid/lfm2.5-1.2b` (~20s per response)
- **API**: OpenAI-compatible `/v1/chat/completions` endpoint
- **Other models available**: `google/gemma-3-1b`, `qwen/qwen3-1.7b`, `glm-ocr`, `text-embedding-nomic-embed-text-v1.5`

## Storage (Dual Persistence)

### SQLite (`sir9.db`)
Location: `%USERPROFILE%\.local\share\sir9\sir9.db`

| Table | Purpose |
|-------|---------|
| `users` | User profiles, scores, accuracy stats |
| `quiz_attempts` | Per-question answers (user_id, module_id, question_id, correct) |
| `user_progress` | Module completion %, questions answered |
| `achievements` | Badges awarded to users |

### JSON (`sir9_store.json` + `curriculum.json`)
Location: `%USERPROFILE%\.local\share\sir9\`

| File | Purpose |
|------|---------|
| `sir9_store.json` | User settings, session history, app config |
| `curriculum.json` | Curriculum modules, questions, content |

## Architecture
```
┌─────────────────────────────────────────────┐
│              sir9tui (Textual TUI)           │
│              app.py + app.tcss               │
├─────────────────────────────────────────────┤
│  ask_lm_studio()  │  Curriculum  │  Database │
│  (HTTP async)     │  (JSON)      │  (SQLite) │
├─────────────────┬───────────────┼───────────┤
│  LM Studio API   │  JSON files   │  sir9.db  │
│  (127.0.0.1:1234)│  (~/.local/) │           │
└─────────────────┴───────────────┴───────────┘
```

## Files in Project
| File | Purpose |
|------|---------|
| `app.py` | Main TUI application with LM Studio integration |
| `app.tcss` | Terminal CSS styles |
| `database.py` | SQLite layer (users, progress, quiz) |
| `curriculum.py` | Quiz engine + JSON store + Sir9JSONStore |
| `sir9tui.bat` | Windows batch launcher |
| `sir9tui.ps1` | PowerShell launcher script |
| `sir9tui.cmd` | Alternative CMD launcher |

## Dependencies (pip)
```
textual>=0.62
rich>=15.0
markdown-it-py>=2.1.0
```

## LM Studio Connection Test
| Test | Result |
|------|--------|
| API reachable | ✅ `http://127.0.0.1:1234` |
| Models loaded | ✅ 5 models |
| Embedding (nomic-embed) | ✅ 768-dim in 11s |
| Chat (lfm2.5-1.2b) | ✅ ~20s |
| Chat (gemma-3-1b) | ⚠️ >60s on CPU |

## How to Launch
```powershell
# Method 1: PowerShell function (after restart)
sir9tui

# Method 2: Batch file
C:\Users\ai9\Desktop\neni9\sir9tui\sir9tui.bat

# Method 3: Direct
cd C:\Users\ai9\Desktop\neni9\sir9tui
python app.py
```

---
**sir9tui v2** — Built by Nenifix 🇬🇭
