# Run the Scanner in the Cloud — GitHub Actions (Free)

Run the v3.1 intraday scanner (all 3 SOP strategies) + self-updating trade journal on GitHub's
servers, so signals and journal updates happen **even when your home PC
is switched off**. This setup costs **$0 forever** on a public repository
(unlimited Actions minutes).

```
  09:30 - 15:29 IST   one scan cycle every 5 minutes (Mon-Fri)
  15:35 IST           end-of-day journal finalization + day verdict
  every run           journal/*.csv committed back into the repo
                      (your trade history lives on GitHub, viewable anytime)
```

---

## 1. What's in this folder

| File | Purpose |
|------|---------|
| `.github/workflows/scanner.yml` | The automation: schedule, two jobs, journal auto-commit |
| `.github/scripts/commit_journal.sh` | Commits journal files back to the repo (with race handling + daily keepalive commit) |
| `make_config.py` | Builds `config.json` from GitHub Secrets at every run — your token/capital never live in the repo |
| `scanner.py` / `journal.py` / `universe_nifty100.txt` / `README.md` | Scanner v3.1, same as your local zip |
| `requirements.txt` | Python dependencies (yfinance, pandas) |
| `config.example.json` | Reference copy of all settings (for local runs) |

## 2. One-time setup (about 10 minutes)

### Step 1 — Create the repository
1. Sign up / log in at **github.com** (free account).
2. Click **+** (top-right) → **New repository**.
3. Name: `intraday-scanner` · Visibility: **Public** · **Do NOT** tick
   "Add a README" (empty repo).
4. Click **Create repository**.

### Step 2 — Upload these files
From your PC (needs [git](https://git-scm.com) installed, or use GitHub
Desktop):

```bash
cd intraday_scanner_cloud
git init
git add .
git commit -m "scanner v3.1 + cloud automation"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/intraday-scanner.git
git push -u origin main
```

> Public repo = free unlimited minutes. Your trade journal CSVs will be
> publicly visible in the repo. If you prefer privacy, use a **Private**
> repo instead and apply the one-line change in section 8 — still free
> (2,000 free minutes/month covers it).

### Step 3 — Add your Secrets
Repo page → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**, for each row:

| Secret name | Value | Required? |
|-------------|-------|-----------|
| `SCANNER_CAPITAL` | your capital, e.g. `25000` | recommended |
| `SCANNER_RISK_PCT` | risk %, e.g. `0.25` (Phase V) | recommended |
| `TELEGRAM_BOT_TOKEN` | bot token from @BotFather | optional |
| `TELEGRAM_CHAT_ID` | your numeric chat id | optional |
| `SCANNER_RISK_RR` | reward:risk, e.g. `3` | optional (default 3) |
| `DATA_MODE` | `auto` (default) / `yahoo` | optional |

**Telegram alerts (5 min, recommended):**
1. In Telegram, message **@BotFather** → `/newbot` → copy the token.
2. Start a chat with your new bot (send it any message).
3. Message **@userinfobot** → it shows your **Id** (that's the chat id).
4. Add both as secrets. Test by running the workflow manually (Step 4) —
   you should get a scan report on your phone.

Without Telegram secrets everything still works — reports just appear in
the Actions log instead of your phone.

### Step 4 — Test it now
Repo page → **Actions** tab → **Intraday Scanner** → **Run workflow** →
mode `scan` → **Run workflow**.

After ~2 minutes open the run: you should see
`[CONFIG] config.json built ...`, then either
`[DATA] NSE fast lane OK` or `[DATA] NSE blocked/failed; Yahoo-only mode`
(**Yahoo-only is expected from GitHub's datacenter IPs** — the scanner
runs fully on Yahoo 5-minute bars), then `[SCAN] ...` lines and a journal
report. First run also creates `journal/` and commits it — refresh the
repo home page to see the files.

## 3. What happens every trading day (IST)

| Time | What runs | What you get |
|------|-----------|--------------|
| 09:30-15:29, every ~5 min | `scanner.py --once` | Telegram alerts for confirmed signals, SL/target hits, circuit breaker, day verdict; journal updated each cycle |
| 15:35 | `journal.py` | Back-fills any trade that resolved while nothing was running, finalizes `EOD` square-offs, writes the final **DayVerdict (SUCCESS/FAILED/FLAT)** |
| after every run | commit step | `journal/trade_journal.csv`, `daily_summary.csv`, `journal_state.json` pushed to the repo |

**Reading your journal:** open the files on github.com directly, or
`git pull` locally / download from the repo web page. Open trades show
`Status = OPEN`; completed trades show `WIN / LOSS / EOD` with P&L in R
and rupees. `daily_summary.csv` holds one verdict row per day — the
phase-validation record you'll review with the SOP.

## 4. Honest caveats (know these)

- **Cron delays:** GitHub's scheduler can start a run 5-15 min late at
  busy periods. Fine for this strategy (5-min bars + broker-terminal
  verification anyway) — but alerts are not tick-precise.
- **NSE fast lane:** GitHub runner IPs are usually blocked by NSE
  (HTTP 403). The scanner auto-switches to Yahoo-only — signals confirm
  on closed 5-minute bars, which is the same lane your bar confirmation
  always used. Nothing to configure.
- **NSE holidays / weekends:** cron still fires; the scanner detects
  "weekend / no fresh bars" and exits in seconds. Harmless no-ops.
- **Never auto-disabled:** GitHub switches scheduled workflows off after
  60 days of repo inactivity — the daily `.heartbeat` commit prevents
  that automatically.
- **First signal after a gap:** if a trade was open when the previous
  session ended, the next run back-fills its outcome from Yahoo history
  before scanning — no orphan rows.

## 5. Home PC vs cloud — pick ONE primary

Do **not** run the home-PC scanner and the cloud scanner at the same
time: you'd get duplicate Telegram alerts and two writers on the same
journal. Recommended pattern:

- **Home PC as primary** (lower latency, NSE fast lane usually works) —
  keep your 9:15 Task Scheduler job.
- **Cloud as backup** — when traveling or the PC must stay off: cancel
  the home Task Scheduler task for those days (or just shut the PC —
  then run `UPDATE_JOURNAL.bat` once you're back, it reconciles with the
  cloud data... but simplest is: those days, let the cloud own the day).

The journal merges cleanly because trades are deduped by `TradeID` and
the CSV is rebuilt from source-of-truth rows.

## 6. Changing settings later

- Capital / risk / RR / Telegram: edit the **Secrets** (Settings →
  Secrets and variables → Actions) — no code change, applies next run.
- Strategy filters: edit `scanner.py` `DEFAULT_CONFIG` → commit → push.
- Schedule: edit the two `cron:` lines in
  `.github/workflows/scanner.yml` → commit → push.

## 7. Troubleshooting

| Symptom | Fix |
|---------|-----|
| No runs in Actions tab | Schedule only starts after the file is on the **default branch**; also check Actions aren't disabled (Actions tab → enable). |
| Run fails at `pip install` | Transient PyPI hiccup — re-run the job. |
| `NSE fast lane` never shows OK | Expected on GitHub IPs. Yahoo-only is the normal cloud mode. |
| No Telegram message | Check both secrets exist with no extra spaces; make sure you sent your bot a message first. |
| Journal didn't update | Open the run log — if the commit step says "No journal changes", there was genuinely nothing to record. |
| Want to stop everything | Actions tab → Intraday Scanner → ⋯ → **Disable workflow**. |

## 8. Private-repo variant (still free)

Private = 2,000 free minutes/month. Each scan run uses ~1.5-2 min, so
switch the scan cron from every 5 to every 15 minutes — edit
`.github/workflows/scanner.yml`:

```yaml
    - cron: '*/15 4-9 * * 1-5'   # was: '*/5 4-9 * * 1-5'
```

(~1,400 min/month.) Keep the 15:35 `journal.py` job as is — it's one
run per day. Fewer cycles = slightly later first detection of a 5-minute
breakout, but signal logic itself is unchanged (bars are 5-min either
way).
