#!/bin/bash

# install.sh - Install ask CLI tool with optional Claude Code integration

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}    ask CLI Tool Installer${NC}"
echo -e "${BLUE}================================${NC}"
echo

# Check if scripts exist
if [ ! -f "ask" ]; then
    echo -e "${RED}Error: 'ask' script not found in current directory${NC}" >&2
    exit 1
fi

# Ask about Claude Code integration
echo -e "${GREEN}Installation Options:${NC}"
echo "1) OpenRouter only (original functionality)"
echo "2) Claude Code + OpenRouter (full integration)"
echo
read -p "Select installation type [1-2]: " -n 1 -r INSTALL_TYPE
echo
echo

INSTALL_CLAUDE=false
if [[ "$INSTALL_TYPE" == "2" ]]; then
    INSTALL_CLAUDE=true
    echo -e "${BLUE}Installing with Claude Code integration...${NC}"

    # Check for ask_claude.py
    if [ ! -f "ask_claude.py" ]; then
        echo -e "${RED}Error: 'ask_claude.py' script not found${NC}" >&2
        echo "Claude Code integration requires ask_claude.py"
        exit 1
    fi

    # Check for Python 3
    echo "Checking dependencies..."
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed${NC}" >&2
        echo "Claude Code integration requires Python 3+"
        exit 1
    fi

    # Check Python version (recommend 3.6+ for subprocess features)
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [ "$(echo "$PYTHON_VERSION < 3.6" | bc)" -eq 1 ]; then
        echo -e "${YELLOW}Warning: Python $PYTHON_VERSION detected. Python 3.6+ recommended${NC}"
    fi

    echo -e "${GREEN}✓ Python 3 found${NC}"

    # Check for Node.js and ask about Claude CLI
    if command -v npm &> /dev/null; then
        if ! command -v claude &> /dev/null; then
            echo
            read -p "Install Claude Code CLI (npm install -g @anthropic-ai/claude-code)? [Y/n]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                echo "Installing Claude Code CLI (may require sudo)..."
                sudo npm install -g @anthropic-ai/claude-code || {
                    echo -e "${YELLOW}Claude Code CLI installation failed or was skipped${NC}"
                    echo "To install manually: npm install -g @anthropic-ai/claude-code"
                }
            fi
        else
            echo -e "${GREEN}✓ Claude Code CLI already installed${NC}"
        fi
    else
        echo -e "${YELLOW}Note: npm not found. Claude Code CLI cannot be installed.${NC}"
        echo "To use Claude Code, install Node.js and run: npm install -g @anthropic-ai/claude-code"
    fi

    # Ask about default model preference
    echo
    echo -e "${GREEN}Default Model Configuration:${NC}"
    echo "Which model should be the default when using 'ask' with no flags?"
    echo "1) Claude Haiku (fastest, cheapest)"
    echo "2) Claude Sonnet (balanced - recommended)"
    echo "3) Claude Opus (most capable, slower)"
    echo "4) OpenRouter Mercury Coder"
    read -p "Select default [1-4] (or press Enter for Sonnet): " -n 1 -r DEFAULT_MODEL
    echo

    case "$DEFAULT_MODEL" in
        1) DEFAULT_MODEL_NAME="haiku" ;;
        3) DEFAULT_MODEL_NAME="opus" ;;
        4) DEFAULT_MODEL_NAME="openrouter" ;;
        *) DEFAULT_MODEL_NAME="sonnet" ;;  # Default to Sonnet
    esac

    if [[ "$DEFAULT_MODEL_NAME" != "openrouter" ]]; then
        echo -e "${BLUE}Setting default model to Claude $DEFAULT_MODEL_NAME${NC}"
        mkdir -p ~/.ask
        echo "default_model=$DEFAULT_MODEL_NAME" > ~/.ask/config
    else
        echo -e "${BLUE}Default will use OpenRouter${NC}"
    fi

    # Safety warnings for Claude Code integration
    echo
    echo -e "${RED}⚠️  IMPORTANT SAFETY INFORMATION ⚠️${NC}"
    echo -e "${YELLOW}Claude has access to execute commands on your system.${NC}"
    echo "The system prompt includes safety rules to prevent destructive actions,"
    echo "but LLMs can be unpredictable. The safety measures include:"
    echo
    echo "1. System prompt instructs Claude to NOT execute destructive commands"
    echo "2. Destructive commands will be prefixed with '⚠️ DESTRUCTIVE:'"
    echo "3. Optional: Limit to 1 turn to reduce tool execution risk"
    echo
    echo -e "${RED}Do you understand these risks and accept responsibility?${NC}"
    read -p "Type 'yes' to continue: " -r ACCEPT_RISK
    if [[ "$ACCEPT_RISK" != "yes" ]]; then
        echo -e "${RED}Installation cancelled for safety.${NC}"
        exit 1
    fi

    echo
    echo -e "${YELLOW}Additional Safety Option:${NC}"
    echo "Limiting Claude to 1 turn MAY prevent tool execution (not guaranteed)."
    echo "This makes responses faster but prevents counting files, etc."
    read -p "Enable 1-turn limit for extra safety? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p ~/.ask
        echo "max_turns=1" >> ~/.ask/config
        echo -e "${GREEN}✓ 1-turn limit enabled${NC}"
        echo "Note: This may cause errors for queries requiring file access."
    else
        echo "No turn limit set (Claude can use tools to answer questions)."
    fi

    echo
    echo -e "${BLUE}Safety configuration complete.${NC}"
    echo "To modify safety settings, edit: ~/.ask/config"
    echo "To remove safety prompt, edit: ask_claude.py (lines 40-46)"

else
    echo -e "${BLUE}Installing OpenRouter-only version...${NC}"
fi

echo

# Make executable
chmod +x ask
if [ "$INSTALL_CLAUDE" = true ] && [ -f "ask_claude.py" ]; then
    chmod +x ask_claude.py
fi

# Install to /usr/local/bin
echo "Installing scripts to /usr/local/bin/ (requires sudo)..."
sudo cp ask /usr/local/bin/

if [ "$INSTALL_CLAUDE" = true ] && [ -f "ask_claude.py" ]; then
    sudo cp ask_claude.py /usr/local/bin/
fi

echo
echo -e "${GREEN}✓ Installation complete!${NC}"
echo

# Optional: Get OpenRouter IPs (for OpenRouter users)
if [ "$INSTALL_CLAUDE" = false ] || [ -n "${OPENROUTER_API_KEY:-}" ]; then
    read -p "Optimize OpenRouter DNS (optional)? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Resolving OpenRouter DNS..."
        IPS=$(dig +short openrouter.ai 2>/dev/null | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || nslookup openrouter.ai 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$')

        if [ -n "$IPS" ]; then
            echo -e "${YELLOW}OpenRouter IP addresses:${NC}"
            echo "$IPS"
            echo
            echo "To improve OpenRouter performance, add to /etc/hosts:"
            echo "----------------------------------------"
            for IP in $IPS; do
                echo "$IP    openrouter.ai"
            done | head -1
            echo "----------------------------------------"
            echo
        fi
    fi
fi

# Show usage based on what was installed
echo -e "${GREEN}Usage:${NC}"

if [ "$INSTALL_CLAUDE" = true ]; then
    echo "  ask 'What is 2+2?'                    # Claude (default: $DEFAULT_MODEL_NAME)"
    echo "  ask -h 'Quick calculation'            # Claude Haiku (fast)"
    echo "  ask -s 'Explain quantum computing'    # Claude Sonnet"
    echo "  ask -o 'Complex analysis'             # Claude Opus"
    echo "  ask -m 'Generate some code'           # OpenRouter Mercury"
    echo "  ask --help                            # Show all options"
    echo
    echo -e "${GREEN}Configuration:${NC}"
    echo "Claude Code:"
    echo "  - Default model: ~/.ask/config or export ASK_DEFAULT_MODEL=haiku|sonnet|opus"
    echo "  - Requires Claude Code login: claude login"
    echo
    echo "OpenRouter (optional):"
    echo "  - Set API key: export OPENROUTER_API_KEY='your-key-here'"
else
    echo "  ask 'What is 2+2?'                    # Uses OpenRouter"
    echo "  ask -g 'Explain quantum computing'    # Gemini 2.5 Flash"
    echo "  ask --help                            # Show all options"
    echo
    echo -e "${GREEN}Configuration:${NC}"
    echo "Set your OpenRouter API key:"
    echo "  export OPENROUTER_API_KEY='your-key-here'"
fi

echo
echo -e "${BLUE}Installation complete! Enjoy using ask!${NC}"