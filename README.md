# ask - AI CLI Tool with Optional Claude Code Integration

A lightweight command-line tool for querying AI models via OpenRouter API, with optional Claude Code integration for direct access to Claude models.

## Features

- **Dual Backend Support**: OpenRouter (default) or Claude Code integration
- **Simple Usage**: Just type `ask` followed by your question
- **Multiple Models**: Quick shortcuts for various AI models
- **Direct Answers**: Optimized for command-line usage (no markdown, executable output)
- **Interactive Installer**: Choose your preferred setup during installation
- **Configurable**: Set default models and backends to match your workflow

## Quick Start

```bash
# Clone the repository
git clone https://github.com/kagisearch/ask.git
cd ask

# Run the interactive installer
./install.sh

# Choose your installation type:
# 1) OpenRouter only (original functionality)
# 2) Claude Code + OpenRouter (full integration)
```

## Installation Options

### Option 1: OpenRouter Only
- No additional dependencies required
- Uses your OpenRouter API key
- Access to Gemini, GPT-4, Qwen, and more

### Option 2: Claude Code Integration
- Requires Python 3.10+ and Node.js
- Installs Claude CLI (`npm install -g @anthropic-ai/claude-code`)
- Direct access to Claude Haiku, Sonnet, and Opus
- Falls back to OpenRouter if Claude is unavailable

## Usage

### With Claude Code Integration

```bash
# Use default model (configurable, defaults to Sonnet)
ask "Write hello world in Python"

# Force specific Claude models
ask -h "Quick calculation: 18% of 2450"  # Haiku (fast)
ask -s "Explain quantum computing"       # Sonnet (balanced)
ask -o "Complex reasoning task"          # Opus (powerful)

# Use OpenRouter models
ask -m "Generate code"                   # Mercury Coder
ask -g "General question"                # Gemini Flash
```

### With OpenRouter Only

```bash
# Set your API key
export OPENROUTER_API_KEY="your-key-here"

# Use default model (Mercury Coder)
ask "What is 2+2?"

# Use specific models
ask -g "Explain quantum computing"       # Gemini 2.5 Flash
ask -k "Process this document"          # Kimi K2
ask -q "Complex analysis"               # Qwen 235B
```

## Model Selection

| Flag | Model | Backend | Best For |
|------|-------|---------|----------|
| (none) | Configurable | Claude/OpenRouter | General use |
| `-h` | Claude Haiku | Claude Code | Fast, simple tasks |
| `-s` | Claude Sonnet | Claude Code | Balanced (default) |
| `-o` | Claude Opus | Claude Code | Complex reasoning |
| `-m` | Mercury Coder | OpenRouter | Code generation |
| `-g` | Gemini 2.5 Flash | OpenRouter | General purpose |
| `-k` | Kimi K2 | OpenRouter | Long context |
| `-q` | Qwen 235B | OpenRouter | Large model tasks |

## Configuration

### Default Claude Model (if Claude is installed)

Set your preferred default model in order of preference:

1. Command-line flag (`-h`, `-s`, `-o`)
2. Environment variable: `export ASK_DEFAULT_MODEL=haiku|sonnet|opus`
3. Config file: `~/.ask/config` with `default_model=haiku|sonnet|opus`
4. Falls back to `sonnet` if not configured

### Safety Features (Claude Code)

The Claude Code integration includes multiple safety layers:

1. **System Prompt Safety Rules**: Claude is instructed to never execute destructive commands
2. **Warning Prefixes**: Destructive commands are prefixed with `⚠️ DESTRUCTIVE:`
3. **Optional Turn Limiting**: Set `max_turns=1` in `~/.ask/config` to limit tool execution
4. **Explicit Consent**: Installer requires typing "yes" to acknowledge risks

⚠️ **Important**: LLMs can be unpredictable. While safety measures are in place, always review commands before execution.

To modify safety settings:
- Edit `~/.ask/config` for turn limits
- Edit `ask_claude.py` lines 40-46 to modify safety rules

### Requirements

**For OpenRouter:**
- `curl`, `jq`, `bc` (usually pre-installed)
- OpenRouter API key

**For Claude Code (optional):**
- Python 3.6+
- Node.js and npm
- Claude CLI: `npm install -g @anthropic-ai/claude-code`
- Active Claude Code subscription

## Common Options

```bash
# Custom system prompt
ask --system "You are a pirate" "Tell me about sailing"

# Disable system prompt (OpenRouter only)
ask -r -m "What is 2+2?"

# Streaming responses (OpenRouter only)
ask --stream "Tell me a long story"

# Pipe input
echo "Fix this code: print('hello world)" | ask
cat script.py | ask "Review this code"
```

## Examples

### Command Generation
```bash
# Get executable commands directly
ask "Command to find files larger than 100MB"
# Output: find . -type f -size +100M

ask "ffmpeg command to convert mp4 to gif"
# Output: ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" output.gif

# Safety: Destructive commands get warnings
ask "command to delete all files in /tmp/test"
# Output: ⚠️ DESTRUCTIVE: rm -rf /tmp/test/*
```

### Quick Answers
```bash
# Calculations
ask "What is 18% of 2450?"
# Output: 441

# Technical questions
ask "What port does PostgreSQL use?"
# Output: 5432
```

### Code Tasks
```bash
# Code review with Sonnet
cat script.py | ask -s "Find potential bugs"

# Quick fix with Haiku
echo "def func(x): return x/0" | ask -h "Fix this function"

# Complex refactoring with Opus
cat large_module.py | ask -o "Refactor for better performance"
```

## Why Use ask?

- **Fast**: Direct CLI calls with `-p` flag for non-interactive mode (~3-4s responses)
- **Flexible**: Switch between Claude and OpenRouter models with simple flags
- **Clean Output**: No markdown or formatting - just executable answers
- **Scriptable**: Perfect for automation and shell scripts
- **Cost-Effective**: Use cheaper models for simple tasks, powerful ones when needed

## Contributing

Pull requests are welcome! The installer is designed to be backwards-compatible, so OpenRouter-only users aren't affected by Claude Code integration.

## License

MIT