#!/usr/bin/env bash
# Run this ON the Google Cloud VM (after copying bot.py, requirements.txt,
# sprites.json and this script into your home dir). It installs:
#   1. The bot + sync API as a systemd service (runs 24/7, auto-restarts).
#   2. Caddy as a reverse proxy in front of the API, with automatic free
#      HTTPS (via sslip.io — no domain purchase needed) so the website
#      (served over HTTPS from GitHub Pages) can call it without being
#      blocked by the browser's mixed-content rules.
# Safe to re-run — it updates the app and restarts both services.
set -euo pipefail

APP=/opt/sprite-bot
SRC="$(cd "$(dirname "$0")" && pwd)"
EXTERNAL_IP="$(curl -s -H 'Metadata-Flavor: Google' \
  'http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip')"
DOMAIN="${EXTERNAL_IP}.sslip.io"

echo "==> Installing system packages (python venv + pip)…"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip curl gnupg debian-keyring debian-archive-keyring apt-transport-https

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
Environment=PYTHONUNBUFFERED=1
ExecStart=${APP}/venv/bin/python ${APP}/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

echo "==> Enabling + starting bot service…"
sudo systemctl daemon-reload
sudo systemctl enable --now sprite-bot
sleep 2
sudo systemctl --no-pager --lines=0 status sprite-bot || true

echo "==> Installing Caddy (reverse proxy + automatic HTTPS)…"
if ! command -v caddy >/dev/null 2>&1; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
    | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
    | sudo tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y -qq caddy
fi

echo "==> Writing Caddyfile for https://${DOMAIN} …"
sudo tee /etc/caddy/Caddyfile >/dev/null <<CADDY
${DOMAIN} {
	reverse_proxy 127.0.0.1:8080
}
CADDY
sudo systemctl enable --now caddy
sudo systemctl restart caddy
sleep 2
sudo systemctl --no-pager --lines=0 status caddy || true

echo
echo "✅ Done. The bot + sync API run 24/7 and survive reboots."
echo "   Sync API URL:   https://${DOMAIN}/api"
echo "   Bot logs:       sudo journalctl -u sprite-bot -f"
echo "   Caddy logs:     sudo journalctl -u caddy -f"
echo "   Restart bot:    sudo systemctl restart sprite-bot"
echo "   Restart proxy:  sudo systemctl restart caddy"
