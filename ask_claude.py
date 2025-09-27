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
DEFAULT_SYSTEM_PROMPT = """You are a direct answer assistant. Your responses must be minimal and direct.

For commands: Output only the command syntax
For questions: Output only the answer
For code: Output only the code

Never include:
- Explanations or reasoning
- Markdown formatting or code blocks
- Multiple options or alternatives
- Introductory or concluding text"""


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


def run_query(prompt, model='haiku', system_prompt=None, raw_mode=False, allow_tools=False):
    """Run a query against Claude CLI directly."""
    start_time = time.time()

    # Build command - using -p for print mode (non-interactive)
    cmd = ['claude', '-p']

    # Add model
    if model:
        cmd.extend(['--model', model])

    # Optionally allow limited tools for file/search operations
    if allow_tools:
        cmd.extend(['--allowed-tools', 'Bash,Read,Grep,Glob'])

    # Add system prompt unless raw mode
    # Note: --system-prompt is undocumented but replaces the entire prompt
    if not raw_mode and system_prompt:
        cmd.extend(['--system-prompt', system_prompt])
    elif not raw_mode:
        cmd.extend(['--system-prompt', DEFAULT_SYSTEM_PROMPT])

    # Add the prompt
    cmd.append(prompt)

    try:
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        if result.returncode != 0:
            print(f"Error: Claude CLI failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        # Output the response
        response = result.stdout.strip()
        print(response)

        # Show metadata to stderr
        elapsed = time.time() - start_time

        # Try to extract cost from stderr if available
        cost_str = ""
        if "Cost:" in result.stderr:
            # Try to parse cost from stderr
            for line in result.stderr.split('\n'):
                if 'Cost:' in line or '$' in line:
                    import re
                    match = re.search(r'\$([0-9.]+)', line)
                    if match:
                        cost_str = f" - ${match.group(1)}"
                        break

        print(f"\n[Claude {model.capitalize()} - {elapsed:.2f}s{cost_str}]", file=sys.stderr)

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
                        help='Model to use (default: from config or haiku)')
    parser.add_argument('-r', '--raw', action='store_true',
                        help='Raw mode - no system prompt')
    parser.add_argument('-t', '--tools', action='store_true',
                        help='Allow limited tools (Bash, Read, Grep, Glob)')
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

    # Run the query
    run_query(
        prompt=prompt,
        model=model,
        system_prompt=args.system,
        raw_mode=args.raw,
        allow_tools=args.tools
    )


if __name__ == '__main__':
    main()