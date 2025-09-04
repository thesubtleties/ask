# ask - AI CLI tool

A lightweight bash script for querying AI models via the OpenRouter API, optimized for direct, executable output.

## Features

- **Direct Output** - Returns executable commands and answers without markdown formatting
- **Multiple Models** - Quick access to Mercury Coder, Gemini, Claude Sonnet, Kimi, and Qwen models
- **Streaming Support** - Real-time response streaming for long outputs
- **Provider Routing** - Automatic fallback between providers for reliability
- **Performance Metrics** - Shows response time and tokens/second
- **Pipe Support** - Works seamlessly with Unix pipes and stdin

## Quick start

```bash
# Clone and setup
git clone https://github.com/yourusername/ask.git
cd ask
chmod +x ask

# Set your API key
export OPENROUTER_API_KEY="your-api-key-here"

# Test it
./ask "What is 2+2?"
```

## Installation

### Option 1: Using install.sh (recommended)
```bash
sudo ./install.sh
```

### Option 2: Manual installation
```bash
chmod +x ask
sudo cp ask /usr/local/bin/
```

### Persistent API key setup

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

## Usage

### Basic usage

```bash
ask "What is 2+2?"
ask "Write a Python hello world"
```

### Model selection

```bash
# Default model (Mercury Coder - optimized for code)
ask "Write a Python function"

# Shorthand flags for quick model switching
ask -c "prompt"  # Mercury Coder (default, best for code)
ask -g "prompt"  # Gemini 2.5 Flash (fast, general purpose)
ask -s "prompt"  # Claude Sonnet 4 (complex reasoning)
ask -k "prompt"  # Kimi K2 (long context)
ask -q "prompt"  # Qwen 235B (large model)

# Custom model by full name
ask -m "openai/gpt-4o" "Explain this concept"
```

### Provider routing

Specify provider order for fallback support:

```bash
ask --provider "openai,together" "Generate code"
```

This will try OpenAI first, then fall back to Together if needed.

### System prompts

```bash
# Custom system prompt
ask --system "You are a pirate" "Tell me about sailing"

# Disable system prompt for raw model behavior
ask -r "What is 2+2?"
```

### Streaming mode

Get responses as they're generated:

```bash
ask --stream "Tell me a long story"
```

### Pipe input

```bash
echo "Fix this code: print('hello world)" | ask
cat script.py | ask "Review this code"
```

## Options

| Option | Description |
|--------|-------------|
| `-c` | Use Mercury Coder (default) |
| `-g` | Use Google Gemini 2.5 Flash |
| `-s` | Use Claude Sonnet 4 |
| `-k` | Use Moonshotai Kimi K2 |
| `-q` | Use Qwen3 235B |
| `-m MODEL` | Use custom model |
| `-r` | Disable system prompt |
| `--stream` | Enable streaming output |
| `--system` | Set custom system prompt |
| `--provider` | Set provider order (comma-separated) |
| `-h, --help` | Show help message |

## Common use cases

### Command generation
```bash
# Get executable commands directly
ask "Command to find files larger than 100MB"
# Output: find . -type f -size +100M

ask "ffmpeg command to convert mp4 to gif"
# Output: ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" output.gif
```

### Code generation
```bash
# Generate code snippets
ask "Python function to calculate factorial"

# Code review
cat script.py | ask "Find potential bugs in this code"
```

### Quick answers
```bash
# Calculations
ask "What is 18% of 2450?"
# Output: 441

# Technical questions
ask "What port does PostgreSQL use?"
# Output: 5432
```

### Advanced usage
```bash
# Chain commands
ask "List all Python files" | ask "Generate a script to check syntax of these files"

# Use with other tools
docker ps -a | ask "Which containers are using the most memory?"

# Provider fallback for reliability
ask --provider "anthropic,openai" "Complex analysis task"
```

## Requirements

### Dependencies
- `bash` - Shell interpreter
- `curl` - HTTP requests to OpenRouter API
- `jq` - JSON parsing for API responses
- `bc` - Performance metrics calculation

### API access
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
- Set as environment variable: `OPENROUTER_API_KEY`

## Performance

The tool displays performance metrics after each query:
- **Model** - Which AI model processed the request  
- **Provider** - The infrastructure provider that served it
- **Response Time** - Total time in seconds
- **Token Speed** - Generation speed in tokens/second

Example output:
```
$ ask "What is 2+2?"

4

[inception/mercury-coder via Inception - 0.82s - 11.0 tok/s]
```

## Troubleshooting

### API key not set
```bash
Error: OPENROUTER_API_KEY environment variable is not set
# Solution: export OPENROUTER_API_KEY="your-key-here"
```

### Missing dependencies
```bash
# Check for required tools
which curl jq bc

# Install on macOS
brew install jq bc

# Install on Ubuntu/Debian
sudo apt-get install jq bc
```

### No response or errors
```bash
# Test with verbose curl output
curl -v https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/gemini-2.5-flash","messages":[{"role":"user","content":"test"}]}'
```

## License

MIT