#!/usr/bin/env python3
"""
Claude CLI integration for ask - direct CLI calls for fast responses.
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path


# Direct answer system prompt - replaces default entirely
DEFAULT_SYSTEM_PROMPT = """You are a command-line assistant responding directly in the terminal.

Your output will be displayed raw in the terminal or potentially piped to other commands.

RESPONSE RULES:
- Output ONLY the direct answer
- Commands: bare executable syntax (no $ prefix, no markdown)
- Questions: minimal factual answer
- Numbers: just the value
- Paths/names: just the text
- Everything must be copy-pasteable (no quotes around answers)
- User will directly paste your output into terminal or other commands

AVAILABLE TOOLS (automatically available):
- Bash: Execute commands to get real answers (counts, searches, checks)
- Read: Read file contents to answer questions about code
- Grep: Search for patterns across files
- Glob: Find files by pattern
- WebSearch: Search the web for current information
- WebFetch: Fetch and analyze web page content

TOOL USAGE:
- Use tools when asked "how many", "find", "search", "check", "list"
- Use web tools for current events, news, documentation lookups
- Verify facts instead of guessing
- Count/measure rather than estimate

SAFETY RULES - CRITICAL:
- NEVER execute destructive commands (rm -rf, dd, mkfs, format, etc.)
- NEVER modify system files (/etc, /sys, /boot, etc.)
- NEVER execute commands with sudo/su
- If asked for destructive commands, OUTPUT the command but DO NOT execute
- For destructive commands, prefix response with: "⚠️ DESTRUCTIVE: "
- User must manually review and execute dangerous commands themselves

NEVER OUTPUT:
- Markdown code blocks (```)
- Explanations or reasoning
- Multiple alternatives
- Headers or formatting
- "Here is" or "The answer is" phrases

Remember: User can pipe your output directly to bash or other commands."""


def get_default_model():
    """Get the default model from environment or config."""
    # Check environment variable first
    default = os.environ.get('ASK_DEFAULT_MODEL', '').lower()
    if default in ['haiku', 'sonnet', 'opus']:
        return default

    # Check config file
    config_file = Path.home() / '.ask' / 'config'
    if config_file.exists():
        try:
            with open(config_file) as f:
                for line in f:
                    if line.strip().startswith('default_model='):
                        model = line.split('=', 1)[1].strip().lower()
                        if model in ['haiku', 'sonnet', 'opus']:
                            return model
        except:
            pass

    # Default to sonnet for better quality (similar speed to haiku)
    return 'sonnet'


def get_max_turns():
    """Get max_turns setting from config (safety feature)."""
    config_file = Path.home() / '.ask' / 'config'
    if config_file.exists():
        try:
            with open(config_file) as f:
                for line in f:
                    if line.strip().startswith('max_turns='):
                        turns = line.split('=', 1)[1].strip()
                        return int(turns)
        except:
            pass
    return None  # No limit by default


def is_web_enabled():
    """Check if web search is enabled in config."""
    config_file = Path.home() / '.ask' / 'config'
    if config_file.exists():
        try:
            with open(config_file) as f:
                for line in f:
                    if line.strip().startswith('enable_web='):
                        value = line.split('=', 1)[1].strip().lower()
                        return value == 'true'
        except:
            pass
    return False  # Disabled by default for safety


def run_query(prompt, model='haiku', system_prompt=None, max_turns=None):
    """Run a query against Claude CLI directly."""
    import json
    start_time = time.time()

    # Detect if we should stream (output is going to a terminal)
    use_streaming = sys.stdout.isatty()

    # Build command - using -p for print mode (non-interactive)
    cmd = ['claude', '-p']

    # Add model
    if model:
        cmd.extend(['--model', model])

    # Add turn limit if specified (safety feature)
    if max_turns is not None:
        cmd.extend(['--max-turns', str(max_turns)])

    # Check if web search is enabled
    if is_web_enabled():
        # Allow web tools by listing all tools we want
        cmd.extend(['--allowed-tools', 'Bash,Read,Grep,Glob,WebSearch,WebFetch'])

    # Add streaming options if outputting to terminal
    if use_streaming:
        cmd.extend(['--output-format', 'stream-json', '--include-partial-messages', '--verbose'])

    # Note: Tools are available by default in -p mode

    # Add system prompt (--system-prompt replaces the entire prompt)
    if system_prompt:
        cmd.extend(['--system-prompt', system_prompt])
    else:
        cmd.extend(['--system-prompt', DEFAULT_SYSTEM_PROMPT])

    # Add the prompt
    cmd.append(prompt)

    try:
        if use_streaming:
            # Streaming mode - show response in real-time
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )

            total_cost = 0
            response_lines = []

            # Process each JSON line as it arrives
            for line in process.stdout:
                try:
                    data = json.loads(line)

                    # Extract text from content_block_delta events
                    if data.get('type') == 'stream_event':
                        event = data.get('event', {})
                        if event.get('type') == 'content_block_delta':
                            delta = event.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                text = delta.get('text', '')
                                print(text, end='', flush=True)
                                response_lines.append(text)

                    # Get cost from final result
                    elif data.get('type') == 'result':
                        total_cost = data.get('total_cost_usd', 0)

                except json.JSONDecodeError:
                    continue

            process.wait()
            if response_lines:
                print()  # Final newline

            # Show metadata
            elapsed = time.time() - start_time
            cost_str = f" - ${total_cost:.4f}" if total_cost else ""
            print(f"\n[Claude {model.capitalize()} - {elapsed:.2f}s{cost_str}]", file=sys.stderr)

        else:
            # Non-streaming mode (for piping/capturing)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"Error: Claude CLI failed: {result.stderr}", file=sys.stderr)
                sys.exit(1)

            # Output the response
            response = result.stdout.strip()
            print(response)

            # Show metadata to stderr
            elapsed = time.time() - start_time
            print(f"\n[Claude {model.capitalize()} - {elapsed:.2f}s]", file=sys.stderr)

    except subprocess.TimeoutExpired:
        print("Error: Claude CLI timed out after 30 seconds", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Query Claude via CLI')
    parser.add_argument('prompt', nargs='?', help='The prompt to send')
    parser.add_argument('-m', '--model', choices=['haiku', 'sonnet', 'opus'],
                        help='Model to use (default: from config or sonnet)')
    parser.add_argument('--system', help='Custom system prompt')

    args = parser.parse_args()

    # Get prompt from args or stdin
    if args.prompt:
        prompt = args.prompt
    else:
        if sys.stdin.isatty():
            print("Error: No prompt provided. Pipe input or provide as argument.", file=sys.stderr)
            sys.exit(1)
        prompt = sys.stdin.read().strip()

    # Determine model
    model = args.model or get_default_model()

    # Get max_turns from config (safety feature)
    max_turns = get_max_turns()

    # Run the query
    run_query(
        prompt=prompt,
        model=model,
        system_prompt=args.system,
        max_turns=max_turns
    )


if __name__ == '__main__':
    main()