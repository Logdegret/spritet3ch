#!/usr/bin/env bash
# Run this ON the Google Cloud VM (after copying bot.py, requirements.txt,
# sprites.json and this script into your home dir). It installs the bot as a
# systemd service so it runs 24/7 and restarts automatically after crashes or
# reboots. Safe to re-run (it updates the app and restarts the service).
set -euo pipefail

APP=/opt/sprite-bot
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "==> Installing system packages (python venv + pip)…"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip

echo "==> Copying app to $APP …"
sudo mkdir -p "$APP"
sudo cp "$SRC/bot.py" "$SRC/requirements.txt" "$SRC/sprites.json" "$APP/"

echo "==> Building virtualenv…"
[ -d "$APP/venv" ] || sudo python3 -m venv "$APP/venv"
sudo "$APP/venv/bin/pip" install --quiet --upgrade pip
sudo "$APP/venv/bin/pip" install --quiet -r "$APP/requirements.txt"

# Store the token in a root-only env file (kept out of the service file + git).
if [ ! -f /etc/sprite-bot.env ]; then
  echo
  read -rsp "Paste your Discord bot token (input hidden): " TOKEN; echo
  echo "DISCORD_TOKEN=${TOKEN}" | sudo tee /etc/sprite-bot.env >/dev/null
  sudo chmod 600 /etc/sprite-bot.env
  echo "==> Token saved to /etc/sprite-bot.env (chmod 600)."
else
  echo "==> Reusing existing /etc/sprite-bot.env (token already set)."
fi

echo "==> Writing systemd service…"
sudo tee /etc/systemd/system/sprite-bot.service >/dev/null <<UNIT
[Unit]
Description=Fortnite Sprite Locker Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${APP}
EnvironmentFile=/etc/sprite-bot.env
ExecStart=${APP}/venv/bin/python ${APP}/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

echo "==> Enabling + starting service…"
sudo systemctl daemon-reload
sudo systemctl enable --now sprite-bot
sleep 2
sudo systemctl --no-pager --lines=0 status sprite-bot || true

echo
echo "✅ Done. The bot now runs 24/7 and survives reboots."
echo "   Live logs:     sudo journalctl -u sprite-bot -f"
echo "   Restart:       sudo systemctl restart sprite-bot"
echo "   Stop:          sudo systemctl stop sprite-bot"
