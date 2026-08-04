# sir9tui — Offline AI STEM Tutor

> **Built by Godwin Appiah (Neni), Founder of Nenifix**
>
> A terminal AI STEM tutor for students. Fully offline-first: it teaches with built-in
> answers when no AI server is present, and unlocks live AI tutoring the moment an
> LM Studio / OpenAI-compatible server is running on `127.0.0.1:1234`.

---

## Quick Install (pip)

```bash
pip install git+https://github.com/nenifix/sir9tui-v1.git
```

Then launch:
```bash
sir9tui
```

No LM Studio? It still works — sir9 falls back to built-in offline answers.

---

## Portable Windows build

A ready-to-run **portable Windows 10/11 ZIP** (bundled Python, no install needed):

1. Download `sir9tui-portable-win64-v1.1.0.zip` (see Releases)
2. Extract anywhere, e.g. `C:\sir9tui`
3. Double-click `sir9tui.cmd` — done.

---

## Features (v1.1.0)

- **Interactive Terminal UI** — Clean, navigable interface built with Textual
- **AI-Powered Learning (optional)** — Connects to LM Studio for intelligent tutoring responses
- **Offline Mode (default)** — Built-in local answer bank when no AI server is running
- **Quiz Engine** — Real multiple-choice flow with scoring; answer by pressing `1-4`
- **Progress Tracking** — SQLite database tracks user scores, accuracy, and completion
- **Persistent Storage** — JSON files for settings, session history, curriculum
- **Working Settings + Modules screens** (were stubs in v1.0.0)
- **Portable launchers** — `.cmd` / `.bat` / `.ps1` use relative paths (no hardcoded machine paths)

---

## Screenshots

```
┌─────────────────────────────────────────────────────────┐
│              sir9 — Built by Nenifix                     │
│                                                         │
│   Welcome to sir9 - AI STEM Tutor                       │
│   Built by Nenifix · offline-first                      │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ # Introduction to STEM                            │  │
│  │ ## What is STEM?                                  │  │
│  │ STEM is an acronym that stands for Science,       │  │
│  │ Technology, Engineering, and Mathematics...       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  [ Start Learning ]  [ View Quiz ]  [ Modules ]          │
│                                                         │
│  Q  Quit  S  Settings  M  Modules  1-4  Answer          │
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

### 2. LM Studio (optional)

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

### Option 1: pip install (Recommended)

```bash
pip install git+https://github.com/nenifix/sir9tui-v1.git
sir9tui
```

### Option 2: Extract and Run

1. **Extract** the ZIP file to any folder (e.g., `C:\sir9tui`)
2. **Install dependencies:**
```bash
cd C:\sir9tui
pip install textual rich
```
3. **Launch the app:**
```bash
python -m sir9tui.main
```

### Option 3: Portable Windows ZIP

See **Portable Windows build** above — bundled Python, just double-click `sir9tui.cmd`.

### Option 4: PowerShell Module

1. Copy the module to your PowerShell modules folder:
```powershell
$moduleDir = "$env:USERPROFILE\Documents\PowerShell\Modules\sir9tui"
Copy-Item "sir9tui.psm1" -Destination "$moduleDir\sir9tui.psm1"
```
2. Launch from any PowerShell window:
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
| `s` | Open Settings |
| `m` | List modules (type a module number to open) |
| `1-4` | Answer quiz options |
| Mouse | Click buttons and navigate |

### First Launch

1. Launch sir9tui (`sir9tui` or double-click `sir9tui.cmd`)
2. **Click "Start Learning"** to get an explanation (AI if LM Studio is up, offline otherwise)
3. **Click "View Quiz"** to test your knowledge — answer with keys `1-4`
4. **Press `m`** to browse modules; **`s`** for settings/status

### AI Mode (optional)

1. Install LM Studio from [lmstudio.ai](https://lmstudio.ai)
2. Load a model (e.g. `liquid/lfm2.5-1.2b`, `qwen3-1.7b`)
3. Start the local server (default port 1234)
4. Run sir9tui — it auto-detects the server and uses live AI answers.

Without LM Studio, sir9 uses its built-in offline answer bank.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              sir9tui (Textual TUI)           │
│              main.py + app.tcss             │
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
├── main.py              # Main TUI application (canonical entry)
├── app.py               # Backward-compatible alias for main.py
├── app.tcss             # Terminal CSS styles
├── curriculum.py        # Quiz engine + JSON store + Sir9JSONStore
├── database.py          # SQLite database layer
├── sir9tui.bat          # Windows batch launcher
├── sir9tui.ps1          # PowerShell launcher script
├── sir9tui.psm1         # PowerShell module
├── sir9tui.cmd          # Alternative CMD launcher
├── TECH_STACK_REPORT.md # Technical documentation
└── README.md            # This file
```

---

## Troubleshooting

### "Textual not found"
```bash
pip install textual rich
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
