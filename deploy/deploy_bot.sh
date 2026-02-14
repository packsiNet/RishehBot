#!/usr/bin/env bash
# Deploy the bot code into /opt/risheh-bot, install dependencies and (re)start the systemd service.

set -euo pipefail

BOT_TOKEN=${1:-}
DEPLOY_USER=${2:-}

if [ -z "$BOT_TOKEN" ]; then
  echo "BOT_TOKEN is required as first argument" >&2
  exit 1
fi

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

sudo bash -c "cat > $APP_DIR/.env <<EOF
BOT_TOKEN=$BOT_TOKEN
EOF"

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
