#!/usr/bin/env bash
# Deploy the bot code into /opt/rishehbot, install dependencies and (re)start the systemd service.

set -euo pipefail

BOT_TOKEN_ARG=${1:-}
DEPLOY_USER=${2:-}

APP_DIR=/opt/rishehbot
PY_BIN=$(cat "$APP_DIR/.python_bin" 2>/dev/null || echo python3)

sudo mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ ! -d .venv ]; then
  sudo -H "$PY_BIN" -m venv .venv
fi

sudo .venv/bin/pip install --upgrade pip
if [ -f requirements.txt ]; then
  sudo .venv/bin/pip install -r requirements.txt
fi

# Resolve BOT_TOKEN from arg, env, or existing file
if [ -n "$BOT_TOKEN_ARG" ]; then
  BOT_TOKEN_VALUE="$BOT_TOKEN_ARG"
elif [ -n "${BOT_TOKEN:-}" ]; then
  BOT_TOKEN_VALUE="$BOT_TOKEN"
elif [ -f "$APP_DIR/.env" ] && grep -q '^BOT_TOKEN=' "$APP_DIR/.env"; then
  BOT_TOKEN_VALUE=$(sed -n 's/^BOT_TOKEN=//p' "$APP_DIR/.env" | head -n1)
else
  echo "BOT_TOKEN not provided (arg/env) and not found in $APP_DIR/.env" >&2
  exit 1
fi

printf '%s\n' "BOT_TOKEN=$BOT_TOKEN_VALUE" | sudo tee "$APP_DIR/.env" >/dev/null

if [ -z "$DEPLOY_USER" ]; then
  DEPLOY_USER=$(whoami)
fi

if [ -f "$APP_DIR/deploy/rishehbot.service" ]; then
  sudo cp "$APP_DIR/deploy/rishehbot.service" /etc/systemd/system/rishehbot.service
  sudo sed -i "s#{{USER}}#$DEPLOY_USER#g" /etc/systemd/system/rishehbot.service
fi

sudo systemctl daemon-reload
sudo systemctl enable rishehbot.service || true
sudo systemctl restart rishehbot.service

exit 0
