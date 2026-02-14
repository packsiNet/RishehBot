#!/usr/bin/env bash
# Install prerequisites for running the Telegram bot as a systemd service.

set -euo pipefail

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required on the target server" >&2
  exit 1
fi

sudo mkdir -p /opt/rishehbot /var/log/rishehbot

if [ -f /etc/os-release ]; then
  . /etc/os-release
else
  ID=unknown
fi

case "$ID" in
  ubuntu|debian)
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg lsb-release rsync git sqlite3
    if apt-cache policy python3.11 >/dev/null 2>&1; then
      sudo apt-get install -y python3.11 python3.11-venv python3-pip
      PY_BIN=python3.11
    else
      sudo apt-get install -y python3 python3-venv python3-pip
      PY_BIN=python3
    fi
    ;;
  centos|rhel|amzn|fedora)
    if command -v dnf >/dev/null 2>&1; then PM=dnf; else PM=yum; fi
    sudo $PM install -y python3 python3-virtualenv git rsync
    PY_BIN=python3
    ;;
  *)
    echo "Unknown distro $ID, attempting generic Python3 install..." >&2
    if ! command -v python3 >/dev/null 2>&1; then
      echo "python3 is required" >&2
      exit 1
    fi
    PY_BIN=python3
    ;;
esac

sudo bash -c "echo $PY_BIN > /opt/rishehbot/.python_bin"

exit 0
