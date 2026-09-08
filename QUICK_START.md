# Local Vision Agent Skill - Quick Start

The local-vision-agent skill is ready to use.

## Prerequisites
- Ollama installed and running (`ollama --version`)
- A vision model pulled (e.g., `ollama pull moondream2`)
- Python dependencies installed (`pip install opencv-python mss ollama pywin32`)

## Usage

Run the script directly:
```bash
cd C:\Users\ashis\AppData\Local\hermes\skills\personal\local-vision-agent
python scripts/vision_agent.py --source screen --model moondream --prompt "Describe what you see in this image in one sentence."
```

### Options
- `--source {webcam,screen}`: Image source (default: screen)
- `--model MODEL`: Ollama model name (default: moondream)
- `--prompt PROMPT`: Prompt for the vision model (default: "Describe what you see in this image in one sentence.")
- `--speak`: Speak the result using Windows TTS
- `--output {text,json}`: Output format (default: text)

## Examples
```bash
# Describe screen in one sentence
python scripts/vision_agent.py --source screen --model moondream --prompt "Describe what you see in this image in one sentence."

# Get JSON output
python scripts/vision_agent.py --source screen --model moondream --output json

# Use webcam (if available)
python scripts/vision_agent.py --source webcam --model moondream --prompt "What is in front of the camera?"

# Speak the description
python scripts/vision_agent.py --source screen --model moondream --speak
```

## Integration with Hermes
While there is no `hermes run local-vision-agent` command (the `run` subcommand does not exist in Hermes CLI), you can still use the skill by executing the script directly as shown above. The skill is fully functional and returns descriptions from the local vision LLM.

## Notes
- First inference may take a moment as the model loads into VRAM.
- Ensure your webcam is not in use by another application if using `--source webcam`.
- The skill supports JSON output for further processing in automation workflows.