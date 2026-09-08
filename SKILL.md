---
name: local-vision-agent
description: "Local vision agent: describe webcam/screen via Ollama."
version: 0.2.0
author: Hermes Agent
category: personal
tags: [vision, ollama, webcam, screen, moondream2, qwen-vl]
---
# Local Vision Agent Skill

## Objective
Enable Hermes to use a local multimodal LLM (e.g., Moondream2, Qwen2.5-VL) via Ollama to capture images from webcam or screen and return a textual description, optionally spoken via Windows TTS.

## Collected Information
- **Vision models suitable for low VRAM (RTX 2050 4GB):**
  - Moondream2 (~1.8B) – ~2GB VRAM, good for simple description, OCR.
  - Qwen2.5-VL-7B (quantized) – ~4-5GB VRAM, strong OCR, multilingual.
  - LLaVA-1.5-7B – ~6-8GB VRAM, strong general vision-language understanding.
  - MiniCPM-V 2.6 (8B) – ~6-8GB VRAM, excellent for document and screenshot understanding.
  - Gemma-3-Vision-2B – ~2-3GB VRAM, efficient zero-shot VQA.
  - Phi-3-Vision-3.8B – ~4-5GB VRAM, balanced reasoning and vision.

- **Installation steps:**
  1. Install Ollama from https://ollama.com/download/windows and verify with `ollama --version`.
  2. Pull a vision model, e.g., `ollama pull moondream2`.
  3. Install Python dependencies: `pip install opencv-python mss ollama pywin32`.

- **Script functionality (vision_agent.py):**
  - Captures a frame from webcam (`cv2.VideoCapture(0)`) or primary monitor (using `mss`).
  - Encodes the frame as JPEG base64.
  - Sends to Ollama via `ollama.generate(model=..., prompt=..., images=[b64])`.
  - Returns the model's description.
  - Optional Windows TTS via `win32com.client.Dispatch("SAPI.SpVoice")`.
  - Supports `--output json` for machine-readable results.

## Detailed Implementation Plan
This plan follows the **writing‑plans** skill conventions: each task is bite-sized (≈2‑5 minutes), includes exact file paths, complete code/command examples, and verification steps.

> **For Hermes:** Use the `subagent-driven-development` skill to execute this plan task‑by‑task with two‑stage review (spec compliance then code quality).

### Phase 0: Preparation
**Task 0: Create skill folder and initial files**
- **Objective:** Set up the skill directory structure with placeholder SKILL.md and scripts/ folder.
- **Files:**
  - Create: `C:/Users/ashis/AppData/Local/hermes/skills/personal/local-vision-agent/SKILL.md`
  - Create: `C:/Users/ashis/AppData/Local/hermes/skills/personal/local-vision-agent/scripts/`
- **Step 1:** Create the directory if it does not exist.
- **Step 2:** Write a minimal SKILL.md with name, description, version.
- **Step 3:** Create an empty `scripts/` folder.
- **Verification:** List the folder contents to confirm both files/folder exist.
- **Commit:** `git add .` and `git commit -m "feat(local-vision-agent): initialize skill folder"` (if using Git; otherwise skip).

### Phase 1: Environment Verification
**Task 1: Verify Ollama installation and pull model**
- **Objective:** Confirm Ollama is available and pull the default vision model (moondream2).
- **Files:** None (uses terminal commands).
- **Step 1:** Run `ollama --version` and capture output.
- **Step 2:** Run `ollama pull moondream2` and wait for completion.
- **Verification:** 
  - `ollama --version` prints a version string (e.g., `ollama version 0.5.0`).
  - After pull, `ollama list` shows `moondream2` with a size.
- **Commit:** No code changes; optionally log the output to a file `setup.log`.

### Phase 2: Python Dependencies
**Task 2: Install required Python packages**
- **Objective:** Install OpenCV, MSS, Ollama Python client, and PyWin32 for TTS.
- **Files:** None (uses pip).
- **Step 1:** Run `pip install opencv-python mss ollama pywin32`.
- **Verification:** 
  - `python -c "import cv2, mss, ollama, win32com.client; print('All imports OK')"` succeeds without error.
- **Commit:** Log installed versions to `requirements.txt` via `pip freeze > requirements.txt`.

### Phase 3: Script Development (TDD‑style)
**Task 3: Write skeleton script with argument parsing**
- **Objective:** Create `scripts/vision_agent.py` that parses CLI arguments and exits with a usage message.
- **Files:** 
  - Create: `scripts/vision_agent.py`
- **Step 1:** Write a minimal script containing imports, `argparse` setup for `--source`, `--model`, `--prompt`, `--speak`, `--output`, and a `main()` that prints parsed args.
- **Step 2:** Run `python scripts/vision_agent.py --help` to verify help output.
- **Verification:** Help text includes all defined arguments and defaults.
- **Commit:** `git add scripts/vision_agent.py` and commit.

**Task 4: Implement webcam capture function**
- **Objective:** Add `capture_webcam()` that returns a frame or exits on error.
- **Files:** Modify: `scripts/vision_agent.py`
- **Step 1:** Write the function as per the script (using `cv2.VideoCapture(0)`).
- **Step 2:** Add a call to `capture_webcam()` in `main()` when `--source webcam` is selected, storing the frame.
- **Step 3:** Run the script with `--source webcam` (assuming a webcam is present) and verify it does not crash; optionally display the frame with `cv2.imshow` for a brief moment and close.
- **Verification:** No exceptions; a frame is retrieved (can be checked by printing its shape).
- **Commit:** Update the file and commit.

**Task 5: Implement screen capture function**
- **Objective:** Add `capture_screen()` that returns a frame from the primary monitor.
- **Files:** Modify: `scripts/vision_agent.py`
- **Step 1:** Write the function using `mss` as previously shown.
- **Step 2:** Update `main()` to call this function when `--source screen`.
- **Step 3:** Run the script with `--source screen` and verify it returns a frame (print shape).
- **Verification:** Frame shape matches monitor resolution (width × height × 3).
- **Commit:** Update and commit.

**Task 6: Implement image encoding and Ollama call**
- **Objective:** Add `describe_image(frame, model, prompt)` that encodes the frame and queries Ollama.
- **Files:** Modify: `scripts/vision_agent.py`
- **Step 1:** Write the function: encode frame to JPEG base64, call `ollama.generate`.
- **Step 2:** In `main()`, after capturing frame, call `describe_image` and store the result.
- **Step 3:** Run the script with a dummy model (if Ollama not ready) to test encoding; better to test with actual model after pull.
- **Verification:** The function returns a non‑empty string; no exceptions.
- **Commit:** Update and commit.

**Task 7: Add optional TTS and JSON output**
- **Objective:** Implement `speak_text(text)` and `--output json` formatting.
- **Files:** Modify: `scripts/vision_agent.py`
- **Step 1:** Write `speak_text` using `win32com.client.Dispatch("SAPI.SpVoice")`.
- **Step 2:** In `main()`, if `--speak` flag is set, call `speak_text(description)`.
- **Step 3:** If `--output json`, produce a JSON object with source, model, prompt, description and print it indented.
- **Verification:** 
  - With `--speak`, audio is heard (if speakers enabled).
  - With `--output json`, output is valid JSON (can be checked with `python -m json.tool`).
- **Commit:** Update and commit.

**Task 8: Add error handling and exit codes**
- **Objective:** Ensure the script exits with clear messages and non‑zero codes on failure.
- **Files:** Modify: `scripts/vision_agent.py`
- **Step 1:** Wrap capture and description steps in try/except, print error to stderr, `sys.exit(1)`.
- **Step 2:** Test error cases: unplug webcam, invalid model name.
- **Verification:** Script prints helpful message and exits with code 1.
- **Commit:** Update and commit.

### Phase 4: Integration with Hermes
**Task 9: Finalize SKILL.md with usage and dependencies**
- **Objective:** Complete the skill documentation with collected information, detailed plan, usage examples, and dependencies.
- **Files:** Modify: `SKILL.md`
- **Step 1:** Replace placeholder content with the full SKILL.md (as drafted in this plan).
- **Step 2:** Ensure the description fits the 60‑character limit.
- **Verification:** View the rendered SKILL.md via `skill_view(name='personal/local-vision-agent')` to confirm formatting.
- **Commit:** Update and commit.

**Task 10: Test the skill via Hermes CLI**
- **Objective:** Verify that `hermes run local-vision-agent describe` works as expected.
- **Files:** None (uses Hermes command).
- **Step 1:** Run `hermes run local-vision-agent describe --source screen --model moondream2 --prompt "Describe what you see."`.
- **Step 2:** Observe the description output.
- **Step 3:** Optionally add `--speak` to hear it.
- **Verification:** Skill returns a non‑empty description; no errors.
- **Commit:** Log the successful run to a file `test_run.txt` inside the skill folder.

### Phase 5: Cleanup and Documentation
**Task 11: Create a README‑style summary inside the skill folder**
- **Objective:** Provide a quick‑reference guide for future users.
- **Files:** Create: `README.md` (optional) or ensure SKILL.md is sufficient.
- **Step 1:** Copy the objective, usage, and dependencies into a concise format.
- **Verification:** File exists and is readable.
- **Commit:** Add and commit.

### Phase 6: Review and Finalize
**Task 12: Run final verification checklist**
- **Objective:** Ensure all tasks are complete and the skill is ready for use.
- **Checklist:**
  - [ ] Skill folder exists with SKILL.md and scripts/vision_agent.py.
  - [ ] Ollama is installed and model pulled.
  - [ ] Python dependencies installed.
  - [ ] Script captures webcam and screen correctly.
  - [ ] Script calls Ollama and returns description.
  - [ ] Optional TTS and JSON output work.
  - [ ] Error handling is in place.
  - [ ] SKILL.md contains objective, collected information, detailed plan, usage, dependencies.
  - [ ] Skill can be invoked via `hermes run local-vision-agent describe …`.
- **Verification:** All checklist items pass.
- **Commit:** Final commit `feat(local-vision-agent): complete skill implementation`.

## How to Execute This Plan
You can execute the plan manually, or ask Hermes to run it using the `subagent‑driven‑development` skill:

```
hermes run subagent-driven-development --plan-file /path/to/this/plan.md
```

(If you save this plan as a markdown file, e.g., `C:/Users/ashis/AppData/Local/hermes/skills/personal/local-vision-agent/PLAN.md`, you can point to it.)

Each task will be dispatched to a fresh subagent with two‑stage review (spec compliance then code quality). Proceed only when both reviews approve.

## Notes
- The plan assumes a webcam is present for `--source webcam`; if not, that task can be skipped or marked as N/A.
- Adjust the default model in the script/SKILL.md if you prefer a different vision model (remember to pull it first).
- For improved performance on the RTX 2050, consider using 4‑bit quantized models (e.g., `qwen2.5-vl:7b-q4_0`).

## Usage

To run the local-vision-agent skill via Hermes CLI, use:

```bash
hermes run local-vision-agent [options]
```

Options are the same as the underlying script `scripts/vision_agent.py`:

```bash
hermes run local-vision-agent --source webcam --model moondream2 --prompt "Describe the scene."
```

For detailed options, run:

```bash
hermes run local-vision-agent --help
```

## References
- Ollama documentation: https://ollama.com/
- Writing‑plans skill: `skill_view(name='software-development/writing-plans')`
- Subagent‑driven‑development skill: `skill_view(name='software-development/subagent-driven-development')`
- Grounded‑citations skill (for citing sources if needed): `skill_view(name='research/grounded-citations')`
