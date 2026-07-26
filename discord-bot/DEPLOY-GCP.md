# Deploy the bot on Google Cloud (cheapest way)

We run the bot on a **single `e2-micro` VM** — the machine itself is in Google
Cloud's **Always Free** tier. A tiny always-on VM is the right shape for a
Discord bot (it holds an open gateway connection), and `systemd` keeps it alive
24/7 and restarts it after crashes or reboots.

### What it costs
- **VM (`e2-micro` in a free region):** $0 — Always Free.
- **External IPv4 address:** ~**$3/month**. Since 2024 Google bills in-use
  external IPv4s. This is the only real cost; there's no simpler way to give the
  bot outbound internet.
- **New GCP accounts get $300 free credit for 90 days**, which covers that.

So: **~$3/month** after the trial credit (or $0 during it).

---

## One-time prep (on your Mac)

Set some variables (pick a free-tier region: `us-central1`, `us-east1`, or `us-west1`):

```bash
export PROJECT=YOUR_PROJECT_ID       # from console.cloud.google.com (create one if needed)
export ZONE=us-central1-a
gcloud auth login
gcloud config set project "$PROJECT"
gcloud services enable compute.googleapis.com
```

## 1. Create the VM

```bash
gcloud compute instances create sprite-bot \
  --zone="$ZONE" \
  --machine-type=e2-micro \
  --image-family=debian-12 --image-project=debian-cloud \
  --boot-disk-size=10GB --boot-disk-type=pd-standard
```

No firewall rules are needed — the bot only makes **outbound** connections, so
nothing is exposed to the internet.

## 2. Copy the bot files up

From inside the `discord-bot/` folder on your Mac:

```bash
gcloud compute scp bot.py requirements.txt sprites.json deploy/setup-on-vm.sh \
  sprite-bot:~ --zone="$ZONE"
```

## 3. Install it as a 24/7 service

```bash
gcloud compute ssh sprite-bot --zone="$ZONE" --command="bash ~/setup-on-vm.sh"
```

It will **prompt you to paste your bot token** (input hidden), then start the
service. You should see `active (running)`.

Done — the bot is now online 24/7, survives reboots, and auto-restarts on crash.

---

## Everyday commands (run over SSH)

```bash
gcloud compute ssh sprite-bot --zone="$ZONE"        # get a shell on the VM
sudo journalctl -u sprite-bot -f                    # live logs
sudo systemctl restart sprite-bot                   # restart
sudo systemctl stop sprite-bot                      # stop
```

## Updating the bot later (new sprites.json / bot.py)

Re-copy the changed files and re-run the setup script (it keeps your token):

```bash
gcloud compute scp bot.py sprites.json deploy/setup-on-vm.sh sprite-bot:~ --zone="$ZONE"
gcloud compute ssh sprite-bot --zone="$ZONE" --command="bash ~/setup-on-vm.sh"
```

User collections are stored in `/opt/sprite-bot/collections.json` on the VM and
persist across restarts and updates.

## Turning it off / avoiding charges

```bash
gcloud compute instances stop sprite-bot   --zone="$ZONE"   # pause (stops IP charge too)
gcloud compute instances delete sprite-bot --zone="$ZONE"   # remove entirely
```
