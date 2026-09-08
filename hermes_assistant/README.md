# Hermes Assistant

An autonomous desktop AI companion that watches your screen and camera,
learns your behaviour, and proactively helps — without waiting to be asked.

---

## What It Does

- Floats on your desktop as a small animated avatar (always on top)
- Opens a separate chat window when you click it
- Connects to **OpenRouter** (API mode) or **Ollama** (local/offline mode)
- Remembers context across sessions via an indexed memory system
- Observes your screen and camera *(perception layer — coming in later phases)*
- Proactively suggests help when it notices something *(agent loop — coming in later phases)*

---

## Requirements

- Python 3.9 or higher
- Windows 10 / 11
- Internet connection (for API mode) **or** Ollama installed (for local mode)

---

## Installation

### Step 1 — Clone or download the project

```
git clone https://github.com/ash1407/hermes_vision.git
cd hermes_vision/hermes_assistant
```

Or if you have the folder already, just open a terminal inside `hermes_assistant/`.

### Step 2 — Create a virtual environment (recommended)

```
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```
pip install -r requirements.txt
```

> First install may take a few minutes — DeepFace and MediaPipe are large packages.

---

## Configuration

Open `config.json` in any text editor before running.

### Minimum setup for API mode

```json
{
  "mode": "api",
  "api": {
    "openrouter_key": "YOUR_OPENROUTER_KEY_HERE"
  }
}
```

Get a free OpenRouter key at → https://openrouter.ai/keys

### Minimum setup for local mode (Ollama)

1. Install Ollama → https://ollama.com/download
2. Pull the required models:
   ```
   ollama pull llava
   ollama pull mistral
   ```
3. Set mode in `config.json`:
   ```json
   {
     "mode": "local"
   }
   ```
   No API key needed.

---

## Running

```
python hermes_assistant.py
```

That's it. The avatar appears in the bottom-right corner of your screen.

---

## Using Hermes Assistant

### The Avatar

| Action | Result |
|---|---|
| **Click** the avatar | Opens / closes the chat window |
| **Drag** the avatar | Moves it anywhere on screen |
| Avatar **glows blue** | Idle, watching |
| Avatar **turns amber** | Thinking / processing your message |
| Avatar **turns green** | Speaking / responding |
| Avatar **turns orange** | Alert — proactive suggestion |
| Avatar **turns purple** | Detected you may be stressed |
| Avatar **flashes red** | Error caught on screen |
| Avatar **shrinks to dot** | No presence detected (you stepped away) |

### The Chat Window

| Action | Result |
|---|---|
| **Click avatar** | Opens chat window |
| **Type + Enter** or **→ button** | Sends your message |
| **Drag** the window header | Moves the chat window |
| **× button** | Closes chat window (avatar stays) |

### Changing the Agent Name

Open `config.json` and edit:
```json
"agent": {
  "name": "hermes_assistant"
}
```
Change `"hermes_assistant"` to anything you like. Restart the app to apply.

### Switching Between API and Local Mode

In `config.json`, change:
```json
"mode": "api"
```
to:
```json
"mode": "local"
```
No code changes needed. Restart the app.

### Changing Which Models Are Used

In `config.json`, under `"models"`:

```json
"models": {
  "vision": "google/gemini-flash-1.5",
  "reasoning": "qwen/qwen-vl-max",
  "summarization": "mistralai/mistral-7b-instruct",
  "local_vision": "llava",
  "local_reasoning": "mistral"
}
```

- `vision` — model used to describe screenshots (API mode)
- `reasoning` — model used for suggestions and chat (API mode)
- `summarization` — cheap model for memory summaries (API mode)
- `local_vision` — vision model when running Ollama
- `local_reasoning` — reasoning model when running Ollama

All model IDs for API mode come from → https://openrouter.ai/models

### Adjusting When Hermes Speaks Up

In `config.json`, under `"intervention"`:

```json
"intervention": {
  "error_visible_seconds": 120,
  "stuck_on_task_minutes": 15,
  "consecutive_negative_emotions": 3,
  "confidence_threshold": 0.72
}
```

| Key | Meaning | Lower = more interruptions |
|---|---|---|
| `error_visible_seconds` | How long an error must be on screen before Hermes mentions it | Yes |
| `stuck_on_task_minutes` | How long on the same task before Hermes checks in | Yes |
| `consecutive_negative_emotions` | Frustrated readings before Hermes responds | Yes |
| `confidence_threshold` | Overall sensitivity (0.0–1.0) | Yes |

### Moving the Windows

Drag either window to your preferred position. To save positions permanently, update `config.json`:

```json
"ui": {
  "avatar_position": {"x": 1800, "y": 950},
  "chat_position":   {"x": 1550, "y": 700}
}
```

---

## Project Structure

```
hermes_assistant/
├── hermes_assistant.py       ← entry point — run this
├── config.json               ← all settings, no code changes needed
├── requirements.txt
│
├── core/
│   ├── config_loader.py      ← reads/writes config.json
│   └── model_client.py       ← OpenRouter + Ollama abstraction
│
├── ui/
│   ├── avatar_widget.py      ← floating animated avatar
│   └── chat_window.py        ← dark-themed floating chat panel
│
├── memory/
│   ├── INDEX.json            ← master topic map (auto-managed)
│   ├── user/                 ← profile, behaviour, state log
│   ├── work/                 ← project and app context
│   ├── sessions/             ← daily summaries
│   ├── learnings/            ← inferred patterns
│   └── exploration/          ← phase A discoveries
│
├── perception/               ← screen + camera watchers (Phase 3)
├── reasoning/                ← agent loop + tools (Phase 4)
├── learning/                 ← exploration phase logic (Phase 5)
└── perception_audio/         ← microphone + STT (future)
```

---

## Phases — What Is Built and What Is Coming

| Phase | Status | What It Adds |
|---|---|---|
| **Phase 1** — Skeleton | ✅ Done | Floating UI, chat, model connection |
| **Phase 2** — Memory | 🔜 Next | Remembers across sessions, indexed recall |
| **Phase 3** — Perception | 🔜 | Screen watcher, camera, DeepFace expressions |
| **Phase 4** — Agent Loop | 🔜 | Proactive suggestions, tool calling, web search |
| **Phase 5** — Learning | 🔜 | Explores and maps your environment |
| **Phase 6** — Polish | 🔜 | Full avatar animations, settings panel |
| **Audio Phase** | 🔜 Future | Microphone, Whisper STT, wake word |

---

## Troubleshooting

**Black or invisible window**
→ Make sure PyQt5 is installed: `pip install PyQt5`

**`ModuleNotFoundError: No module named 'cv2'`**
→ Run: `pip install opencv-python`

**API mode returns an error about the key**
→ Check your `openrouter_key` in `config.json` is correct and has credits

**Ollama connection refused**
→ Make sure Ollama is running: open a terminal and run `ollama serve`

**Avatar appears off-screen**
→ Edit `avatar_position` in `config.json` to `{"x": 100, "y": 100}` and restart

**DeepFace install fails**
→ Install Visual C++ Build Tools first:
  https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## Full Project Plan

The complete architecture, research sources, model strategy, and build plan is in:

```
plan/hermes_assistant_plan.md
```

Also available online:
https://github.com/ash1407/hermes_vision/blob/main/plan/hermes_assistant_plan.md

---

## Built With

- [PyQt5](https://doc.qt.io/qtforpython) — desktop UI
- [OpenRouter](https://openrouter.ai) — API model access (100+ models, one key)
- [Ollama](https://ollama.com) — local model serving
- [DeepFace](https://github.com/serengil/deepface) — facial expression recognition
- [MediaPipe](https://github.com/google-ai-edge/mediapipe) — gaze detection
- [OpenCV](https://opencv.org) — webcam capture
- [mss](https://github.com/BoboTiG/python-mss) — screen capture
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search) — web search
