#!/usr/bin/env bash
set -e

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$REPO/orchestra.py" install "$REPO"

BRAIN="$HOME/.config/opencode"
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if ! grep -q "$BRAIN" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Orchestra path" >> "$SHELL_RC"
    echo "export PATH=\"\$PATH:$BRAIN\"" >> "$SHELL_RC"
    echo "Added $BRAIN to your PATH in $SHELL_RC — restart your terminal or run source $SHELL_RC"
fi

python3 "$REPO/orchestra.py" doctor
