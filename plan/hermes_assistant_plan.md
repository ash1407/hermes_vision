# Hermes Assistant — Full Project Plan

> Autonomous desktop AI companion that observes your screen and camera,
> learns your behaviour, proactively helps, and never needs to be commanded.

---

## Table of Contents

1. [Project Origin](#1-project-origin)
2. [Vision & Goals](#2-vision--goals)
3. [Research Sources](#3-research-sources)
4. [Similar Projects — Key Learnings](#4-similar-projects--key-learnings)
5. [OpenRouter Integration](#5-openrouter-integration)
6. [Architecture Overview](#6-architecture-overview)
7. [Memory System Design](#7-memory-system-design)
8. [Model Strategy](#8-model-strategy)
9. [Avatar & UI Design](#9-avatar--ui-design)
10. [Agent Loop & Tool Calling](#10-agent-loop--tool-calling)
11. [Intervention Logic](#11-intervention-logic)
12. [Two-Phase Learning Design](#12-two-phase-learning-design)
13. [Phased Build Plan](#13-phased-build-plan)
14. [Folder Structure](#14-folder-structure)
15. [Config Schema](#15-config-schema)
16. [Future — Audio Phase](#16-future--audio-phase)

---

## 1. Project Origin

| Item | Detail |
|---|---|
| Original repo | https://github.com/ash1407/hermes_vision |
| Original purpose | Local vision agent — webcam/screen → Ollama LLM → TTS |
| Core files | `vision_agent.py`, `skill.py`, `test_vision.py` |
| Original stack | OpenCV, mss, Ollama, Windows SAPI TTS |

The original project was a single-shot tool: capture image → send to local model → print/speak result.
This plan expands it into a persistent, autonomous, learning companion agent.

---

## 2. Vision & Goals

### What Hermes Assistant Does

- Floats on the desktop as a small animated avatar (always-on-top)
- Continuously observes the user's **screen** and **camera** without waiting for commands
- Understands **facial expressions** and user **emotional state**
- **Proactively suggests** — catches errors, offers help, surfaces relevant info
- **Searches the web autonomously** when it needs information
- **Learns from the user** over time — behaviour, preferences, work patterns
- Stores all learnings in an **indexed memory folder** — reads only what's relevant
- Supports both **local models (Ollama)** and **API models (OpenRouter)** via config toggle
- Name is `hermes_assistant` — **user-configurable** in settings

### What It Is NOT

- Not a command-only chatbot that waits to be asked
- Not a cloud-only service (fully local fallback always available)
- Not always interrupting — it decides when to speak based on confidence score

---

## 3. Research Sources

### Original Project
| Source | URL |
|---|---|
| hermes_vision repo | https://github.com/ash1407/hermes_vision |

### OpenRouter
| Source | URL |
|---|---|
| OpenRouter Docs | https://openrouter.ai/docs |
| OpenRouter Models Catalog | https://openrouter.ai/models |
| Vision / Multimodal Requests | https://openrouter.ai/docs/requests |
| Tool Calling Docs | https://openrouter.ai/docs/tool-calling |
| Agent SDK | https://openrouter.ai/docs/agents |

### GitHub — Similar Projects
| Project | Stars | URL | Key Insight |
|---|---|---|---|
| Eigent | 15.2k | https://github.com/camel-ai/eigent | Open source cowork desktop, multi-agent |
| Open Interpreter | ~55k | https://github.com/OpenInterpreter/open-interpreter | Harness abstraction, provider-agnostic model layer |
| AppAgent | ~5k | https://github.com/mnotgod96/AppAgent | Two-phase learning (explore → deploy), UI documentation |
| Skyvern | ~10k | https://github.com/Skyvern-AI/skyvern | Vision-first screen understanding, swarm reasoning |
| Workany | 1.5k | https://github.com/workany-ai/workany | Desktop agent for any task, TypeScript |
| Ouroboros | 1.3k | — | Persistent memory + autonomous loop as core |
| Windows Agent Arena | 895 | https://github.com/microsoft/WindowsAgentArena | Microsoft's OS-level agent benchmarking platform |
| Amadeus | 196 | — | Real-time multimodal agent, voice + visual |
| Atlas | 31 | — | Electron-based, multi-LLM, computer-use agent |
| Cetus | 143 | — | macOS-focused, local-first agent runtime |

### Libraries & Tools
| Library | Purpose | URL |
|---|---|---|
| PyQt5 / PySide6 | Floating desktop UI, animations | https://doc.qt.io/qtforpython |
| DeepFace | Facial expression recognition (local) | https://github.com/serengil/deepface |
| MediaPipe | Gaze detection, face mesh | https://github.com/google-ai-edge/mediapipe |
| OpenCV | Webcam capture | https://opencv.org |
| mss | Screen capture | https://github.com/BoboTiG/python-mss |
| Ollama | Local model serving | https://ollama.com |
| DuckDuckGo Search | Web search, no API key needed | https://github.com/deedy5/duckduckgo_search |
| Tavily | Web search, better results (key needed) | https://tavily.com |
| Whisper | Speech-to-text (audio phase) | https://github.com/openai/whisper |
| pyaudio | Microphone input (audio phase) | https://pypi.org/project/PyAudio |

---

## 4. Similar Projects — Key Learnings

### AppAgent — Two-Phase Design
AppAgent (Android UI automation) separates **exploration** from **deployment**.
- Phase A: agent explores and documents the environment
- Phase B: agent uses that documentation to act efficiently
- Agents reflect on previous actions before taking new ones
- Generates reusable knowledge bases — humans can manually correct them

**Applied to Hermes:** First 3-5 days = exploration (learn the user's apps, habits, layout).
Then shift to deployment (use learnings to suggest, intervene, assist).

### Open Interpreter — Harness Abstraction
- Model logic is completely separated from agent loop logic
- Users swap models with a config flag — no code changes
- Stores config and session state under `~/.openinterpreter`
- Provider-agnostic: OpenAI, Anthropic, Ollama all behind same interface

**Applied to Hermes:** `model_client.py` abstracts OpenRouter and Ollama behind one interface.
Rest of the codebase never imports a provider SDK directly.

### Skyvern — Vision-First
- Analyzes screenshots rather than DOM/code — resilient to UI changes
- Uses a swarm of agents to comprehend a page simultaneously
- Each agent has a narrow responsibility

**Applied to Hermes:** Screen understanding via vision model on screenshots, not screen-scraping APIs.
More reliable across any app, game, browser, or terminal.

### Ouroboros — Autonomous Loop as Core
- Persistent memory and autonomous operations are first-class, not add-ons
- Agent loop is always running, not triggered by user messages
- Self-creating: agent can spawn sub-tasks

**Applied to Hermes:** Agent loop runs in a background thread always. User chat is one input
channel among several (screen signals, camera signals are others).

---

## 5. OpenRouter Integration

OpenRouter provides a **single OpenAI-compatible endpoint** for dozens of models.
One API key. Automatic fallbacks. Tool calling. Streaming. Vision.

### Endpoint
```
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer <OPENROUTER_API_KEY>
```

### Vision Request Format
```python
{
  "model": "google/gemini-flash-1.5",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "What is on this screen?"},
      {
        "type": "image_url",
        "image_url": {
          "url": "data:image/jpeg;base64,<base64_encoded_image>",
          "detail": "auto"
        }
      }
    ]
  }],
  "stream": True
}
```

### Tool Calling Format
```python
{
  "model": "qwen/qwen-vl-max",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "web_search",
        "description": "Search the web for information",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {"type": "string"}
          },
          "required": ["query"]
        }
      }
    }
  ]
}
```

### Recommended Models via OpenRouter

| Task | Model ID | Cost (per 1M tokens) | Why |
|---|---|---|---|
| Screen analysis (fast) | `google/gemini-flash-1.5` | $0.075 in / $0.30 out | Fast, cheap, excellent vision |
| Deep reasoning + suggestions | `qwen/qwen-vl-max` | $2 in / $6 out | 1M context, strong vision + text |
| Memory summarization | `mistralai/mistral-7b-instruct` | ~$0.06 in / $0.06 out | Very cheap for text tasks |
| Local fallback (offline) | `llava` via Ollama | Free | No internet, full privacy |
| Local reasoning fallback | `mistral` via Ollama | Free | No internet, full privacy |

---

## 6. Architecture Overview

```
config.json  ←  name, mode, models, thresholds, API keys
     │
     ▼
hermes_assistant.py  ←  entry point, boots all layers

┌──────────────────────────────────────────────────────┐
│  PERCEPTION LAYER                                    │
│  screen_watcher.py   → screenshot on meaningful Δ   │
│  camera_watcher.py   → 30s heartbeat + gaze trigger  │
│  DeepFace            → emotion, presence (local)     │
│  MediaPipe           → gaze direction (local)        │
│  signal_queue.py     → thread-safe async queue       │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│  MODEL LAYER  (harness abstraction)                  │
│  model_client.py                                     │
│    ├── OpenRouterClient  (API mode)                  │
│    │     ├── vision_model   → Gemini Flash           │
│    │     └── reasoning_model → Qwen VL Max           │
│    └── OllamaClient  (local mode)                    │
│          ├── llava  (vision)                         │
│          └── mistral  (reasoning)                    │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│  AGENT LOOP  (tool-calling based, always running)    │
│  agent_loop.py                                       │
│  Tools the model can call:                           │
│    read_memory(topic)     → INDEX → relevant files   │
│    write_memory(data)     → stores new learning      │
│    web_search(query)      → DuckDuckGo / Tavily      │
│    get_screen()           → latest screen signal     │
│    get_user_state()       → emotion + presence       │
│    send_message(text)     → push to floating chat UI │
│  should_intervene()       → 0.0–1.0 scorer           │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│  MEMORY LAYER  (indexed, never read-all)             │
│  memory/                                             │
│    INDEX.json          ← topic → file + summary      │
│    user/               ← profile, habits, state log  │
│    work/               ← projects, apps              │
│    sessions/           ← daily summaries             │
│    learnings/          ← patterns, mistakes          │
│    exploration/        ← phase A discoveries         │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│  UI LAYER                                            │
│  avatar_widget.py    ← 80x80 floating face, PyQt5   │
│  chat_window.py      ← separate floating chat window │
│  settings_panel.py   ← name, model, thresholds      │
└──────────────────────────────────────────────────────┘
```

---

## 7. Memory System Design

### Core Principle
The agent **never reads all memory files**. It always:
1. Reads `INDEX.json` first
2. Picks the 2-3 most relevant files for the current context
3. Reads only those files

### INDEX.json Schema
```json
{
  "version": 1,
  "entries": [
    {
      "topic": "python debugging habits",
      "file": "work/apps/vscode.md",
      "summary": "User frequently debugs Python, often leaves print statements, uses VSCode debugger rarely",
      "tags": ["python", "debugging", "vscode"],
      "last_updated": "2026-09-08T14:23:00"
    },
    {
      "topic": "user work schedule",
      "file": "user/behavior.md",
      "summary": "Starts coding around 10am, takes breaks at 1pm, most productive 3-6pm",
      "tags": ["schedule", "habits", "productivity"],
      "last_updated": "2026-09-07T18:00:00"
    }
  ]
}
```

### Folder Structure
```
memory/
  INDEX.json                   ← master topic map
  user/
    profile.md                 ← role, preferences, work style
    behavior.md                ← habits, routines, timing patterns
    state_log.json             ← rolling 7-day emotion/presence log
  work/
    projects/
      <project_name>.md        ← per-project context, stack, recent files
    apps/
      vscode.md
      chrome.md
      terminal.md
  sessions/
    2026-09-08.md              ← auto-generated daily summary
  learnings/
    patterns.md                ← inferred habits (weekly generation)
    mistakes.md                ← recurring errors agent has noticed
  exploration/
    apps_discovered.md         ← phase A: what apps the user has
    layout_map.md              ← phase A: typical screen layouts
```

### What Gets Written vs Ignored

| Observation | Write to memory? |
|---|---|
| Same error seen 3+ times across sessions | Yes → `learnings/mistakes.md` |
| User opens same app sequence every morning | Yes → `user/behavior.md` |
| One-off unusual action | No — session memory only |
| User explicitly says "remember this" | Always yes |
| Random browsing | No |
| Project-specific file patterns | Yes → `work/projects/` |

---

## 8. Model Strategy

### Local Mode (Ollama)
One instance handles all tasks:
- `llava` → vision (screen + camera descriptions)
- `mistral` → reasoning, suggestions, memory summaries
- DeepFace → facial expressions (Python library, not Ollama)

### API Mode (OpenRouter)
Two models, each optimised for its job:
- `google/gemini-flash-1.5` → screen vision (runs every few seconds, must be cheap + fast)
- `qwen/qwen-vl-max` → deep reasoning, proactive suggestions (runs only when needed)
- `mistralai/mistral-7b-instruct` → memory summarisation (cheapest option)
- DeepFace → facial expressions (always local, never sent to API)

### Switching Modes
```json
{
  "mode": "api",
  "models": {
    "vision": "google/gemini-flash-1.5",
    "reasoning": "qwen/qwen-vl-max",
    "summarization": "mistralai/mistral-7b-instruct",
    "local_vision": "llava",
    "local_reasoning": "mistral"
  }
}
```
Change `"mode"` to `"local"` — zero code changes.

---

## 9. Avatar & UI Design

### Avatar Widget
- Size: 80×80px floating window
- Position: bottom-right corner (user-draggable, position saved)
- Always on top: `Qt.WindowStaysOnTopHint`
- Frameless + transparent background: `Qt.FramelessWindowHint`
- Click → opens separate floating chat window

### Avatar States

| State | Eyes | Colour | Animation |
|---|---|---|---|
| Idle | Half-closed | Soft blue | Slow blink |
| Watching | Normal open | Neutral white | Subtle pupil drift |
| Thinking | Spinning pupils | Amber | Processing spin |
| Speaking | Animated | Bright green | Mouth / text pulse |
| Alert / Suggest | Wide open | Orange | Small bounce |
| User stressed | Concerned shape | Soft purple | Gentle pulse |
| Error caught | Alarmed | Red flash | Quick shake |
| User away | Minimised | — | Shrinks to 12px dot |

### Chat Window (Separate Floating)
- Frameless, dark-themed, semi-transparent
- Draggable, independent of avatar position
- Header shows agent name (`hermes_assistant` by default)
- Settings gear icon → opens settings panel
- Slides open when agent speaks, stays open until user closes it

### Settings Panel
- Agent name (editable text field)
- Mode toggle: Local ↔ API
- Model selection dropdowns (per task)
- Intervention thresholds (sliders)
- Memory viewer (read-only index listing)
- Reset memory button

---

## 10. Agent Loop & Tool Calling

### How the Loop Works

```
Signal arrives (screen Δ or camera heartbeat)
           ↓
Build context prompt:
  "Screen shows: <screen_summary>
   User state: <emotion>, <gaze>
   Time: <timestamp>"
           ↓
Load relevant memory:
  read INDEX.json → pick top 2-3 relevant files → read them
           ↓
Send to reasoning model with tools available
           ↓
Model decides which tools to call:
  → read_memory("topic")        get more context
  → web_search("query")         look something up
  → get_screen()                re-analyse screen
  → get_user_state()            check emotion again
  → send_message("suggestion")  speak up to user
  → write_memory({...})         store new learning
  → do nothing                  stay silent
           ↓
Execute tool calls, feed results back to model
           ↓
Model produces final response or stays silent
           ↓
If send_message called → avatar animates, chat window opens
If write_memory called → INDEX.json updated
```

### Tools Definition

```python
TOOLS = [
    {
        "name": "read_memory",
        "description": "Read relevant memory files for a topic. Always call this before making suggestions.",
        "parameters": {"topic": "string — what context you need"}
    },
    {
        "name": "write_memory",
        "description": "Store a new learning or observation to memory.",
        "parameters": {"category": "user|work|learning", "content": "string", "tags": ["string"]}
    },
    {
        "name": "web_search",
        "description": "Search the web. Use when you see an error you cannot explain or user asks something unknown.",
        "parameters": {"query": "string"}
    },
    {
        "name": "get_screen",
        "description": "Get the latest screen capture analysis.",
        "parameters": {}
    },
    {
        "name": "get_user_state",
        "description": "Get current facial expression, emotion, and presence status.",
        "parameters": {}
    },
    {
        "name": "send_message",
        "description": "Send a message to the user's floating chat window. Only call when you have something genuinely useful to say.",
        "parameters": {"text": "string", "priority": "low|normal|high"}
    }
]
```

---

## 11. Intervention Logic

### Threshold Triggers (any one fires intervention)

| Trigger | Default Threshold | Config Key |
|---|---|---|
| Error visible on screen | 120 seconds | `error_visible_seconds` |
| Stuck on same file/task | 15 minutes | `stuck_on_task_minutes` |
| Consecutive frustrated/confused readings | 3 readings | `consecutive_negative_emotions` |
| Destructive action detected | Immediate | `destructive_action_immediate` |
| User looks directly at camera | Immediate | `gaze_trigger_immediate` |
| User explicitly types in chat | Always | — |

### Intervention Scorer (0.0 – 1.0)

```python
def should_intervene(signals: list[Signal], memory: dict) -> float:
    score = 0.0
    if error_on_screen_duration > config.error_visible_seconds:
        score += 0.4
    if stuck_duration > config.stuck_on_task_minutes * 60:
        score += 0.3
    if consecutive_negative_emotions >= config.consecutive_negative_emotions:
        score += 0.2
    if destructive_action_detected:
        score += 0.5
    if gaze_at_camera:
        score = 1.0  # always respond
    return min(score, 1.0)

# Only intervene if score >= config.confidence_threshold (default: 0.72)
```

### Config
```json
{
  "intervention": {
    "error_visible_seconds": 120,
    "stuck_on_task_minutes": 15,
    "consecutive_negative_emotions": 3,
    "destructive_action_immediate": true,
    "gaze_trigger_immediate": true,
    "confidence_threshold": 0.72
  }
}
```

---

## 12. Two-Phase Learning Design

Borrowed from AppAgent. Solves the cold-start problem.

### Phase A — Exploration (Days 1–5)
Agent focuses on **mapping the user's environment**:
- What applications are installed and in use
- Typical screen layouts per app
- File system structure (visible paths)
- Work rhythm (active hours, break patterns)
- Frequent error types
- Writing style and tone from chat

All discoveries written to `memory/exploration/`.
At end of Phase A, agent generates initial `user/profile.md` and `user/behavior.md`.

### Phase B — Deployment (Day 6 onwards)
Agent shifts to **using what it learned**:
- Suggestions based on known patterns
- Memory retrieval is now fast (INDEX is populated)
- Only re-explores when something genuinely new appears (new app, new project)

Both phases coexist — exploration never fully stops, but its weight drops from 80% to 10% after day 5.

### Phase Flag in Memory
```json
{
  "phase": "deployment",
  "exploration_complete": true,
  "phase_switched_date": "2026-09-13"
}
```

---

## 13. Phased Build Plan

### Week 1 — Skeleton
**Goal:** running agent, floating UI, basic chat working

- [ ] `config.json` with full schema
- [ ] `config_loader.py` — reads and validates config
- [ ] `model_client.py` — abstracts OpenRouter + Ollama behind one interface
- [ ] `avatar_widget.py` — 80x80 PyQt5 floating face (static, no animation yet)
- [ ] `chat_window.py` — separate floating window, basic send/receive
- [ ] `hermes_assistant.py` — boots everything, wires layers together
- [ ] Test: send message in chat, get response from OpenRouter model

**Deliverable:** you can type to Hermes and get a response. It floats on your desktop.

---

### Week 2 — Memory System
**Goal:** agent remembers things across sessions, retrieves selectively

- [ ] `memory/INDEX.json` — initial empty schema
- [ ] `memory/reader.py` — query INDEX, return top N relevant file contents
- [ ] `memory/writer.py` — validate + write new learnings, update INDEX
- [ ] `memory/summarizer.py` — end-of-session → daily summary file
- [ ] Integration test: write a learning, close app, reopen, confirm it's recalled

**Deliverable:** Hermes remembers facts across restarts.

---

### Week 3 — Perception Loop
**Goal:** agent watches screen and camera without being asked

- [ ] `perception/screen_watcher.py` — delta-triggered screenshot + basic description
- [ ] `perception/camera_watcher.py` — 30s heartbeat capture
- [ ] `perception/deepface_reader.py` — emotion + presence from camera frame
- [ ] `perception/gaze_detector.py` — MediaPipe gaze direction
- [ ] `perception/signal_queue.py` — thread-safe queue feeding agent loop
- [ ] Test: open app with an error on screen, confirm signal is generated

**Deliverable:** Hermes is watching. Signals flow into the queue.

---

### Week 4 — Agent Loop & Tools
**Goal:** agent decides what to do with what it sees

- [ ] `reasoning/agent_loop.py` — main loop, reads queue, calls model with tools
- [ ] `reasoning/tools.py` — all tool implementations (memory, search, screen, state, message)
- [ ] `reasoning/intervention_scorer.py` — 0.0-1.0 scorer
- [ ] `reasoning/web_search.py` — DuckDuckGo integration
- [ ] Test: leave a Python error on screen for 2+ minutes, confirm agent surfaces it

**Deliverable:** Hermes proactively suggests something without being asked.

---

### Week 5 — Exploration Phase
**Goal:** agent maps environment on first run, populates memory

- [ ] `learning/explorer.py` — phase A logic, discovers apps + layout + habits
- [ ] `learning/phase_manager.py` — tracks phase A vs B, manages transition
- [ ] Auto-generate `user/profile.md` from first 3 sessions
- [ ] Test: run for 3 days, inspect generated memory files for accuracy

**Deliverable:** After a few days of use, memory is meaningfully populated.

---

### Week 6 — Polish & Avatar Animations
**Goal:** agent feels alive, settings work, name is configurable

- [ ] Avatar state machine wired to signals (all 8 states animated)
- [ ] `ui/settings_panel.py` — name, mode, model, thresholds
- [ ] Name `hermes_assistant` shown in chat header, editable
- [ ] Window positions saved and restored
- [ ] Minimise to dot when user steps away (gaze/presence = gone)

**Deliverable:** Full polished experience. Feels like a companion, not a tool.

---

### Future — Audio Phase
**Goal:** Hermes can hear and speak naturally

- [ ] `perception/mic_listener.py` — microphone capture via pyaudio
- [ ] `perception/whisper_stt.py` — local speech-to-text (Whisper)
- [ ] `perception/tone_analyzer.py` — calm / stressed / excited from audio features
- [ ] Wake word: "hey hermes" triggers immediate attention
- [ ] TTS responses via Windows SAPI (already in original `vision_agent.py`)
- [ ] Voice tone feeds into intervention scorer (stressed voice = higher score)

---

## 14. Folder Structure

```
hermes_assistant/
│
├── hermes_assistant.py          ← entry point
├── config.json                  ← user configuration
│
├── core/
│   ├── config_loader.py
│   └── model_client.py          ← OpenRouter + Ollama abstraction
│
├── perception/
│   ├── screen_watcher.py
│   ├── camera_watcher.py
│   ├── deepface_reader.py
│   ├── gaze_detector.py
│   └── signal_queue.py
│
├── reasoning/
│   ├── agent_loop.py
│   ├── tools.py
│   ├── intervention_scorer.py
│   └── web_search.py
│
├── memory/
│   ├── INDEX.json
│   ├── reader.py
│   ├── writer.py
│   ├── summarizer.py
│   ├── user/
│   │   ├── profile.md
│   │   ├── behavior.md
│   │   └── state_log.json
│   ├── work/
│   │   ├── projects/
│   │   └── apps/
│   ├── sessions/
│   ├── learnings/
│   └── exploration/
│
├── learning/
│   ├── explorer.py
│   └── phase_manager.py
│
├── ui/
│   ├── avatar_widget.py
│   ├── chat_window.py
│   └── settings_panel.py
│
└── perception_audio/            ← future audio phase
    ├── mic_listener.py
    ├── whisper_stt.py
    └── tone_analyzer.py
```

---

## 15. Config Schema

```json
{
  "agent": {
    "name": "hermes_assistant",
    "version": "0.1.0"
  },
  "mode": "api",
  "models": {
    "vision": "google/gemini-flash-1.5",
    "reasoning": "qwen/qwen-vl-max",
    "summarization": "mistralai/mistral-7b-instruct",
    "local_vision": "llava",
    "local_reasoning": "mistral"
  },
  "api": {
    "openrouter_key": "",
    "ollama_base_url": "http://localhost:11434"
  },
  "perception": {
    "screen_delta_threshold": 0.05,
    "screen_capture_interval_seconds": 3,
    "camera_heartbeat_seconds": 30,
    "gaze_trigger_enabled": true
  },
  "intervention": {
    "error_visible_seconds": 120,
    "stuck_on_task_minutes": 15,
    "consecutive_negative_emotions": 3,
    "destructive_action_immediate": true,
    "gaze_trigger_immediate": true,
    "confidence_threshold": 0.72
  },
  "memory": {
    "max_index_entries": 500,
    "session_summary_on_exit": true,
    "state_log_days": 7
  },
  "ui": {
    "avatar_position": {"x": 1800, "y": 950},
    "chat_position": {"x": 1600, "y": 700},
    "always_on_top": true,
    "minimize_when_away": true
  },
  "learning": {
    "exploration_phase_days": 5,
    "current_phase": "exploration"
  }
}
```

---

## 16. Future — Audio Phase

| Component | Library | Purpose |
|---|---|---|
| Microphone input | `pyaudio` | Capture audio stream |
| Speech-to-text | `openai/whisper` (local) | Transcribe user speech |
| Tone analysis | custom on audio features | Detect calm / stressed / excited |
| Wake word | `pvporcupine` or keyword matching | "hey hermes" trigger |
| Text-to-speech | Windows SAPI (already in project) | Agent speaks responses |
| Tone → scorer | feeds `intervention_scorer.py` | Stressed voice raises intervention score |

Audio adds a full parallel input channel. The signal queue already supports it — just add a `MicSignal` type.

---

*Plan compiled: 2026-09-08*
*Original repo: https://github.com/ash1407/hermes_vision*
