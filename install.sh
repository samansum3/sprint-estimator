#!/bin/bash
# Installs Sprint Estimator as a clickable app on Ubuntu.
# Usage: run this script from inside the sprint-estimator folder:
#   chmod +x install.sh && ./install.sh

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/sprint-estimator.desktop"

mkdir -p "$HOME/.local/share/applications"

sed "s|__APP_DIR__|$APP_DIR|g" "$APP_DIR/sprint-estimator.desktop" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"
chmod +x "$APP_DIR/app.py"

# Also drop a copy on the Desktop if it exists, so it shows as an icon there too
if [ -d "$HOME/Desktop" ]; then
  cp "$DESKTOP_FILE" "$HOME/Desktop/sprint-estimator.desktop"
  chmod +x "$HOME/Desktop/sprint-estimator.desktop"
fi

# Refresh the application menu cache if the tool is available
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" || true
fi

echo "Installed."
echo "Find 'Sprint Estimator' in your applications menu, or double-click the icon on your Desktop."
echo "(If double-clicking the Desktop icon shows a security prompt, right-click it and choose 'Allow Launching' - this is a one-time Ubuntu/Nautilus requirement for new .desktop files.)"
