# sir9tui — AI STEM Tutor

> **Built by Godwin Appiah (Neni), Founder of Nenifix**
>
> An offline AI-powered terminal tutor that teaches students STEM concepts using a local LLM via LM Studio.

---

## Quick Install (pip)

```bash
pip install git+https://github.com/nenifix/sir9tui-v1.git
```

Then launch:
```bash
sir9tui
```

---

## Features

- **Interactive Terminal UI** — Clean, navigable interface built with Textual
- **AI-Powered Learning** — Connects to LM Studio for intelligent tutoring responses
- **Quiz Engine** — Built-in curriculum with multiple-choice questions
- **Progress Tracking** — SQLite database tracks user scores, accuracy, and completion
- **Persistent Storage** — JSON files for settings, session history, and curriculum
- **Offline-First** — Works without internet (LM Studio runs locally)

---

## Screenshots

```
┌─────────────────────────────────────────────────────────┐
│              sir9 — Built by Nenifix                     │
│                                                         │
│   Welcome to sir9 - AI STEM Tutor                       │
│   Built by Nenifix                                      │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ # Introduction to STEM                            │  │
│  │ ## What is STEM?                                  │  │
│  │ STEM is an acronym that stands for Science,       │  │
│  │ Technology, Engineering, and Mathematics...       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  [ Start Learning ]  [ View Quiz ]  [ My Progress ]     │
│                                                         │
│  Q  Quit  S  Settings                                   │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before installing sir9tui, ensure you have:

### 1. Python 3.11+

Download from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

### 2. LM Studio

Download from [lmstudio.ai](https://lmstudio.ai/)

- Install and launch LM Studio
- Download at least one model (recommended: `liquid/lfm2.5-1.2b`)
- Start the server (default port: 1234)

Verify LM Studio is running:
```bash
curl http://127.0.0.1:1234/v1/models
```

---

## Installation

### Option 1: Extract and Run (Simplest)

1. **Extract** the ZIP file to any folder (e.g., `C:\sir9tui`)

2. **Install dependencies:**
```bash
cd C:\sir9tui
pip install textual
```

3. **Launch the app:**
```bash
python app.py
```

### Option 2: Using the Launcher (Windows)

1. **Extract** the ZIP file

2. **Double-click** `sir9tui.bat` on your Desktop

3. Or open CMD/PowerShell and run:
```bash
C:\path\to\sir9tui\sir9tui.bat
```

### Option 3: PowerShell Module (Recommended)

1. **Extract** the ZIP file to `C:\sir9tui`

2. **Copy the module** to your PowerShell modules folder:
```powershell
$moduleDir = "$env:USERPROFILE\Documents\PowerShell\Modules\sir9tui"
Copy-Item "C:\sir9tui\sir9tui.psm1" -Destination "$moduleDir\sir9tui.psm1"
```

3. **Launch from any PowerShell window:**
```powershell
Import-Module sir9tui
sir9tui
```

---

## Usage

### Navigation

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `s` | Open Settings (login, theme) |
| Mouse | Click buttons and navigate |

### First Launch

1. **Start LM Studio** and ensure a model is loaded
2. **Launch sir9tui:**
   ```bash
   python app.py
   ```
3. **Press `s`** for settings and enter a username
4. **Click "Start Learning"** to get AI explanations from LM Studio
5. **Click "View Quiz"** to test your knowledge
6. **Click "My Progress"** to see your stats

### Settings

- **Username** — Creates a user profile for progress tracking
- **Theme** — Dark/Light mode (stored in JSON)
- **Language** — Interface language preference

---

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

### Storage

| Type | Location | Purpose |
|------|----------|---------|
| SQLite | `%USERPROFILE%\.local\share\sir9\sir9.db` | Users, quiz attempts, progress |
| JSON | `%USERPROFILE%\.local\share\sir9\sir9_store.json` | Settings, sessions |
| JSON | `%USERPROFILE%\.local\share\sir9\curriculum.json` | Curriculum content |

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| TUI Framework | Textual v0.62 |
| AI Backend | LM Studio (local LLM) |
| Database | SQLite (built-in) |
| Config | JSON files |

---

## File Structure

```
sir9tui/
├── app.py              # Main TUI application
├── app.tcss            # Terminal CSS styles
├── curriculum.py       # Quiz engine + JSON store + Sir9JSONStore
├── database.py         # SQLite database layer
├── app.tcss            # UI styling
├── sir9tui.bat         # Windows batch launcher
├── sir9tui.ps1         # PowerShell launcher script
├── sir9tui.psm1        # PowerShell module
├── sir9tui.cmd         # Alternative CMD launcher
├── TECH_STACK_REPORT.md # Technical documentation
└── README.md           # This file
```

---

## Troubleshooting

### "Textual not found"
```bash
pip install textual
```

### "LM Studio not responding"
- Ensure LM Studio is running
- Check port 1234 is open: `netstat -an | findstr 1234`
- Verify model is loaded in LM Studio

### "Model timed out"
- First response is slow (~20-60s) as model loads into memory
- Use a smaller model like `liquid/lfm2.5-1.2b` for faster responses
- Ensure your computer has enough RAM (8GB+ recommended)

### "ImportError: ComposeResult"
- This is fixed in the current version — ensure you have the latest files
- If using an older version, run: `pip install --upgrade textual`

---

## About

**sir9tui** was developed by **Godwin Appiah** (also known as **Neni**), founder of **Nenifix** — a Ghana-based AI Brand Engineering company.

Nenifix is building **Neni9**, a complete AI ecosystem including:
- Neni9 Linux Distribution
- Neni9 PC & Laptops
- Neni9 Smartphones & Tablets
- Neni9 Ecommerce Platform
- Neni9 Mobile Apps
- **God9** — The flagship AI tutor (this app)

---

## License

MIT License — Free to use, modify, and distribute.

## Support

For issues and feature requests, contact:
- **Email**: info@nenifix.com
- **WhatsApp**: +233 53 751 1886
- **Website**: https://nenifix.com

---

**Built with love by Godwin Appiah 🇬🇭**
