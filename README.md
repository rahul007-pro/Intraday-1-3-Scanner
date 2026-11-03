# Intraday Scanner v3.2.1 — All Three SOP Strategies, Fully Automated

(Self-learning journal + AutoPoi zone marking + guaranteed 15:10 square-off)

Companion tool to the **Top 3 Intraday Strategies & Scanners SOP (Rev 2.1)**.
Scans the NIFTY 100 every 5 minutes for **all three SOP strategies**
(Fibonacci Extension Continuation, Momentum + Volume Breakout, Five-Timeframe
CHoCH — both directions), sizes them to the SOP risk model, and keeps a
**trade journal that writes itself** — including an automatic verdict of
whether each day's trades **SUCCEEDED or FAILED**.

> ⚠️ **Doctrine (unchanged):** this tool only *alerts*. It never places
> orders. Every signal must be verified in your broker terminal and must pass
> the SOP 12-point checklist before you act. You are the risk manager.

---

## 1. What's new in v3.0 → v3.2 — three strategy engines, self-learning, end-of-day automation

> **v3.2 highlights:** the scanner now **self-learns** — it studies the last 30 closed
> trades in the journal (overall, per-strategy, per-direction, per-hour, and the last-10
> moving trend) and **benches statistically weak strategies/directions** with printed
> reasons (snapshot in `journal/learning_state.json`, daily 🧠 Telegram digest after the
> close). Hard caps: **max 10 trades/day** (config `max_trades_per_day`, one-time DAILY
> CAP notice) and **no trades or signals after 13:30 IST** for any strategy
> (`entry_cutoff`, engine-wide). Details: SOP Chapter 5.

| Change | Detail |
|---|---|
| **Strategy 2 aligned to SOP Table 7** | EMA-9 vs EMA-20 (was EMA20/50), RSI(14) > 55 / < 45 added, breakout = prior 3-bar high/low, volume ≥ 1.5× prior-20 avg **and** ≥ 100,000 shares, price band ₹50–2,000, stop floor = max(0.30%, 1.5× ATR-14), capital-price rejection + cost hurdle (3R ≥ cost + ₹50). |
| **Strategy 1 engine (NEW)** | Fibonacci Extension Continuation — Mother Fib from the opening impulse, Level-1 close activation with VWAP/EMA-20 context gate, Types 01/02/03 golden-pocket zones, 2R+1G trigger, green-range ≥ 0.30% filter, 5-candle expiry, zone invalidation, full short mirror. Setup tags: `S1_FIB_T01/T02/T03`. |
| **Strategy 3 engine (FULLY AUTOMATED in v3.1)** | Five-Timeframe CHoCH — scanner computes W1/D1 bias itself (both must agree); **the AutoPoi engine marks the H4 POI zones for you every morning** (writes `poi_zones_auto.csv` — no manual entry); scanner automates POI tap → H1 confirmation (CHoCH/pin bar/engulfing) → M15 confirmation close → stop beyond POI extreme → target at nearest opposing POI if ≥ 2R else 3R. Floating price never trades. Setup tag: `S3_CHOCH`. |
| **One position per instrument** | SOP 3.4: if any trade is open on a symbol, no second signal (any strategy) fires for it. |
| **15:05 square-off directive** | Telegram: "close all N open MIS positions NOW" — the SOP's trader square-off time. |
| **Guaranteed 15:10 auto square-off** | Every open trade of the day is force-finalized at the best known price (NSE LTP → last 5m close), journal + day verdict updated immediately. Runs in continuous mode AND in `--once`/cloud mode. |
| **Clean session exit** | Scanning stops at 15:10; after the EOD square-off + report the console closes by itself (Task-Scheduler friendly). `exit_after` 15:35 is a hard safety net; config: `auto_exit_after_close`. |
| **SOP 4.1 sizing guards on every setup** | Capital-price rejection (required capital > ₹25,000 ⇒ the trade is skipped, never shrunk) and the cost hurdle (3R value must beat ₹50 cost + ₹50). |
| **Discipline caps** | SOP 3.4 / Phase V: max 2 concurrent positions, max 10 trades/day since v3.2 (config: `max_concurrent_positions`, `max_trades_per_day`). |

### What stays manual (deliberately, per the SOP)
* **Type 04** rules — still a placeholder in the SOP itself; nothing to encode.
* **H4 POI zones** — automated since v3.1 (AutoPoi engine, see §Strategy 3);
  `poi_zones.csv` is now an OPTIONAL override for zones you want to force.
* **Final trade approval** — the scanner alerts, you verify in the broker
  terminal and fire the order (the SOP 12-point checklist stays yours).
* **Sector-correlation check** and the **regime choice** of which strategy to
  favour — journal checklist items.

---

## 1a. What's new in v3.2 — the scanner learns from its own trades

| Change | Detail |
|---|---|
| **Self-learning engine** | Every scan cycle the scanner studies the **last 30 closed trades** in `trade_journal.csv`: overall win rate and net R, per-strategy form (S1/S2/S3), LONG vs SHORT form, entry-hour form, and the **recent-10 "moving trend"**. |
| **Benching rules (transparent, rule-based)** | A strategy family is **benched** — emits no signals — when it has 8+ closed trades with win rate < 30% **or** net R ≤ −2R, or when its recent form collapses (< 20% WR over 6+ of the last 10 trades). A **direction** (LONG/SHORT) is benched at < 25% WR over 10+ trades. Every gate prints its reason; the top healthy performer is tagged in the EOD report. |
| **Adaptive, not permanent** | Gates re-compute after **every closed trade** (a benched family can earn its way back the same day) and reset next morning from the fresh journal. Open trades of a benched family are still monitored to their normal outcome. |
| **`journal/learning_state.json`** | The learning snapshot: stats, gates, reasons, digest log. Committed by the cloud workflow, so **learning persists across cloud runs**. |
| **Self-learning report** | Appended to the EOD console output and pushed to Telegram once a day (🧠 digest): overall/recent form, per-strategy table, benched items with reasons. |
| **Daily cap raised to 10** | `max_trades_per_day` = 10 (was 3). After 10 trades in a day: one 🛑 Telegram notice, then no more signals — open trades keep being monitored and square off at 15:10 as usual. |
| **Engine-wide 13:30 cutoff** | "No entries after 13:30 IST" was enforced inside Strategy 2 only; it now filters **all** strategies (an S1/S3 confirmation landing at 13:35 is dropped). |

Tune every threshold or switch the learner off entirely via
`config.json → self_learning` (`"enabled": false` = fixed behaviour).

---

## 1b. What was new in v2.2 — the trade journal

| Item | What it does |
|---|---|
| `journal/trade_journal.csv` | One row per confirmed trade — created automatically on first run. Columns: entry, SL, target, qty, risk, exit, result (`WIN`/`LOSS`/`FLAT`), P&L in R and ₹, exit reason. |
| `journal/daily_summary.csv` | One row per trading day — rebuilt automatically after **every** closed trade. Shows wins/losses, net R, net ₹, circuit-breaker flag and the **DayVerdict**. |
| `journal/journal_state.json` | Open-trade state. Survives restarts and crashes; the CSV remains the source of truth (state is rebuilt from it if deleted). |

### How outcomes update themselves
Every scan cycle (and every `journal.py` run), each OPEN trade is checked
against its stop and target using **closed 5-minute bars**:

* Price hits **target** → `TARGET_HIT` → **WIN +3R**
* Price hits **stop** → `STOP_HIT` → **LOSS −1R**
* One 5m bar touches **both** → counted as **LOSS** (conservative — we assume
  the stop was hit first; better to understate a good day than overstate one)
* Nothing hit by **15:10 IST** → `EOD_SQUAREOFF` at the last traded price

The signal bar itself can never trigger an outcome (the 0.10% stop buffer
sits beyond its extreme), so tracking starts from the next bar.

### The DayVerdict — "did the trades fail today?"
`daily_summary.csv` answers that directly:

| Verdict | Meaning |
|---|---|
| `SUCCESS` | Day closed with **net positive R** |
| `FAILED` | Day closed with **net negative R**, **or** a circuit breaker tripped |
| `FLAT` | Net zero |
| `SUCCESS*` / `FAILED*` | Provisional — trades still open or session still running (final after 15:10) |
| `PENDING*` | Trades opened, none closed yet |

Circuit breakers (from the SOP, configurable in `config.json → journal`):
* **2 consecutive losses** in a day → breaker trips
* **Day loss ≤ −2.0R** → breaker trips
* Optional ₹-based limit: `daily_loss_limit_amt` (0 = disabled)

When the breaker trips you get a Telegram/console warning and the scanner
**stops issuing new signals** for the rest of the day (open trades are still
monitored). The final verdict is also pushed to Telegram once the day is done.

### Missed a session? No problem
Open trades persist. The next time you run the scanner or `journal.py`, the
outcome is **back-filled from price history** (target/stop/EOD), and the
day's verdict is refreshed — even if your PC was off the whole session.

---

## 1c. What's new in v3.2.1 — the universe updates itself

NIFTY 100 members change whenever NSE re-balances the index or a company
delists / gets suspended (Tata Motors → TMPV/TMCV, LTIMindtree → LTM, etc.).
The old static `universe_nifty100.txt` then kept producing data errors for
dead symbols until you edited it by hand.

The scanner now refreshes its own universe **at startup, at most once every
7 days** (`universe_refresh.days`), from, in order:

1. **Official NSE constituents CSV** — authoritative; works from home IPs
   (blocked from GitHub/datacenter IPs),
2. **Wikipedia NIFTY 50 + NIFTY Next 50 tables** — no API key, reachable
   from GitHub Actions runners, updated by editors on re-balance day,
3. **the existing file** — always kept as the last-resort fallback.

A successful refresh rewrites `universe_nifty100.txt`, caches the result in
`universe_cache.json` (the cloud workflow commits both), prints and
Telegram-alerts the `+ added / − removed` diff once. Sanity guard: a fetched
list is used only when it holds 80–120 symbols. Any failure is non-fatal —
the current file stays in use and the next attempt happens in the next
window. To freeze the file, set `universe_refresh.enabled: false`.

---

## 2. Quick start (Windows)

1. Install Python 3.10+ (tick *Add to PATH*).
2. Put this folder anywhere (e.g. `D:\intraday_scanner`).
3. Double-click **`START_SCANNER.bat`** in the morning (before 09:15 IST).
   First run auto-installs `yfinance`. Keep the window open during market
   hours. Ctrl+C to stop — the journal state is saved.
4. After 15:10 (or any time), double-click **`UPDATE_JOURNAL.bat`** to refresh
   outcomes and print the journal report.

CLI equivalents:

```
python scanner.py            # continuous 5-min scan loop
python scanner.py --once     # one scan cycle, then a journal report
python scanner.py --journal  # journal update + report only (no scanning)
python scanner.py --selftest # built-in test suite (26 checks)
python journal.py            # standalone journal updater/reporter
```

## 3. Signal logic — Strategy 2 (SOP Table 7, both directions)

| Gate | LONG | SHORT |
|---|---|---|
| Trend | close > VWAP, EMA-9 > EMA-20 | close < VWAP, EMA-9 < EMA-20 |
| Momentum | RSI(14) > 55 | RSI(14) < 45 |
| Breakout | close > highest high of prior three 5m candles | close < lowest low |
| Volume surge | ≥ 1.5× average of prior 20 bars **and** ≥ 100,000 shares | same |
| Candle quality | bullish, closes in top 25% of range | bearish, bottom 25% |
| Universe | ₹50 ≤ price ≤ ₹2,000, day turnover ≥ ₹1 cr | same |
| Stop floor | risk/share ≥ max(0.30% of entry, 1.5× ATR-14) — else skip | same |
| Time window | 09:30 – 13:30 IST (SOP entry cutoff) | same |
| Stop | bar low − 0.10% buffer (rounded **down** to ₹0.05) | bar high + 0.10% buffer (rounded **up**) |
| Target | entry + 3 × risk (1:3 fixed) | entry − 3 × risk |
| Sizing | qty = floor(risk budget ÷ risk/share); **rejected** if qty × entry > capital or 3R value < round-trip cost + ₹50 | same |

### Strategy 1 — how the scanner draws the Fib (deterministic)
* Mother leg **C → A**: C = lowest low from the session open to the day's
  highest-high bar (mirrored for a bearish opening); A = that extreme.
  Level-1 = A + (A−C), 1.618 ext = A + 1.618×(A−C), 0.236 = A − 0.236×(A−C).
* Activation = a 5m **close** beyond Level-1 (wick doesn't count) with the
  SOP context gate (above VWAP + rising EMA-20 for longs; mirrored shorts).
* Type 01 zone = 0.5–0.618 retrace of (new post-activation swing high ← its
  origin pullback); Type 02 = 0.5–0.618 of (C → 1.618 extreme); Type 03 =
  ±0.05-leg band around the Mother 0.236 level.
* Trigger = 2R+1G fully inside the zone (green range ≥ 0.30% of close),
  buy-stop at green high + ₹0.05, SL below green low, void if not filled
  within 5 candles or if a candle closes beyond the zone's stop side.
* Verify the zones on your own chart — the SOP's Fib tool discipline still
  applies before acting on any S1 alert.

### Strategy 3 — fully automated zone marking (v3.1)
Every morning, on the first scan cycle, the **AutoPoi** engine builds the
H4 zone map for the whole universe and writes `poi_zones_auto.csv`:

1. Closed Yahoo 1-hour bars are grouped into two H4 candles per NSE
   session (09:15-13:15, 13:15-15:30 IST) — history up to the previous
   close only, so the map is fixed for the whole day (SOP discipline).
2. Fractal swing highs (k=2 confirmed) become SUPPLY zones (`SHORT`:
   body-top..high of the pivot candle); swing lows become DEMAND zones
   (`LONG`: low..body-bottom).
3. Zones that a later H4 candle CLOSED through are discarded (broken).
   Zones taller than `s3_poi_max_zone_pct` (2%) or further than
   `s3_poi_proximity_pct` (6%) from the last close are dropped; only the
   nearest `s3_poi_max_per_side` (2) per side are kept.
4. The W1/D1 bias gate is applied up-front: BULL symbols keep demand
   zones, BEAR symbols keep supply zones, disagreement = no Strategy 3
   that symbol today (SOP Step 2). A Telegram summary tells you how many
   zones survived before 09:30.
5. Zones carry today's date and expire at midnight; a fresh map is
   generated next session. Restarts are safe — the day's map is written
   exactly once (idempotent).

**Manual overrides (optional):** add rows to `poi_zones.csv` and they are
merged on top of the automatic map:
```
symbol,side,zone_low,zone_high[,date]
RELIANCE,LONG,1285.00,1298.50,2026-10-22
HDFCBANK,SHORT,1712.00,1725.00
```
`side LONG` = demand zone, `SHORT` = supply zone. Leave `date` empty for a
standing zone. Set `s3_auto_poi: false` in config.json to go back to
fully manual zone marking.

Risk model defaults: capital ₹25,000, 0.25% risk (₹62.50) per trade — the
**Phase V** configuration. Move to Phase S by setting `"risk_pct": 1.0`.

### Data modes (`config.json → data_mode`)
* **auto** (default): try NSE's one-request NIFTY-100 snapshot for tick-level
  candidate detection; confirm candidates with Yahoo 5m bars. If NSE blocks
  your IP (common on cloud/datacenter IPs; home broadband usually works),
  silently falls back to Yahoo-only.
* **nse**: force NSE fast lane (falls back if blocked).
* **yahoo**: never touch NSE (Yahoo bars for all 100 stocks each cycle).

Yahoo data can lag a few minutes — one more reason signals are *alerts, not
entries*. Forming bars are never used; only closed 5m bars confirm.

## 4. Telegram alerts (optional)

1. Create a bot with @BotFather → copy the bot token.
2. Get your chat id (message @userinfobot).
3. Fill `telegram.bot_token` and `telegram.chat_id` in `config.json`.

You'll then receive: confirmed signals, every trade outcome (✅/❌ with R and
₹), circuit-breaker warnings, and the end-of-day verdict.

## 5. Reading the journal in Excel

* **trade_journal.csv** — filter `Status = OPEN` for live positions; `Result`
  tells you instantly if a trade failed; `PnL_R` is the honest metric
  (independent of position size). `ExitReason` explains *how* it ended.
* **daily_summary.csv** — your day-by-day report card. A healthy Phase V
  1:3 system shows ~30%+ win rate and positive average R per trade.
* Both files open cleanly in Excel (UTF-8 CSV, one header row).

## 6. Configuration reference (`config.json`)

| Key | Default | Meaning |
|---|---|---|
| `data_mode` | auto | nse / yahoo / auto |
| `scan_interval_min` | 5 | scan cadence |
| `scan_start` / `entry_cutoff` / `squareoff` | 09:30 / 13:30 / 15:10 | SOP session rules |
| `capital` / `risk_pct` | 25000 / 0.25 | Phase V sizing |
| `rr` | 3.0 | fixed reward:risk |
| `sl_buffer_pct` | 0.10 | stop buffer beyond the bar extreme |
| `max_stop_pct` | 1.5 | skip bars with stops wider than this |
| `rvol_mult` / `min_bar_volume` | 1.5 / 100000 | SOP Strategy 2 volume gates |
| `min_price` / `max_price` | 50 / 2000 | SOP universe band |
| `min_turnover` / `min_range_pct` | 1e7 / 0.40 | liquidity & staleness |
| `min_stop_pct` / `atr_stop_mult` | 0.30 / 1.5 | SOP stop floor: max(0.30%, 1.5×ATR-14) |
| `s1_enabled` | true | Strategy 1 (Fib continuation) engine |
| `impulse_min_pct` / `fib_tol_pct` / `trigger_expiry_bars` | 0.5 / 0.2 / 5 | Strategy 1 tuning |
| `s3_enabled` / `s3_auto_poi` | true / true | Strategy 3 engine + automatic H4 zone marking |
| `poi_auto_file` / `poi_file` | poi_zones_auto.csv / poi_zones.csv | generated map / optional manual overrides |
| `s3_poi_max_zone_pct` / `s3_poi_proximity_pct` / `s3_poi_max_per_side` | 2.0 / 6.0 / 2 | zone height cap / distance cap / nearest-N kept per side |
| `squareoff_alert` / `squareoff` | 15:05 / 15:10 | trader directive / auto-finalize |
| `exit_after` / `auto_exit_after_close` | 15:35 / true | clean end-of-session exit |
| `cost_estimate` | 50 | round-trip cost for the SOP cost hurdle |
| `journal.folder` | journal | where the CSVs live |
| `journal.daily_loss_limit_R` | −2.0 | breaker: day loss limit |
| `journal.max_consecutive_losses` | 2 | breaker: loss streak |
| `journal.daily_loss_limit_amt` | 0 | optional ₹ limit (0 = off) |
| `max_trades_per_day` / `max_concurrent_positions` | 10 / 2 | daily trade cap (v3.2) / concurrent positions |
| `self_learning.enabled` | true | v3.2 learner on/off |
| `self_learning.lookback_trades` / `recent_trades` | 30 / 10 | studied window / moving-trend tail |
| `self_learning.min_trades_to_gate` | 8 | min sample before a strategy can be benched |
| `self_learning.block_setup_wr_below` / `block_setup_r_below` | 30 / −2.0 | bench a strategy: WR% floor / net-R floor |
| `self_learning.min_recent_trades` / `recent_form_wr_below` | 6 / 20 | recent-form collapse bench |
| `self_learning.min_direction_trades` / `block_direction_wr_below` | 10 / 25 | LONG/SHORT bench rule |
| `universe_refresh.enabled` | true | v3.2.1 weekly NIFTY 100 auto-update on/off |
| `universe_refresh.days` | 7 | refresh at most once per N days |
| `universe_refresh.min_symbols` / `max_symbols` | 80 / 120 | sanity guard: reject fetched lists outside this range |

Anything you delete from `config.json` is merged back from built-in defaults,
so the journal keeps working even with an old config file.

## 7. Files in this package

```
scanner.py              scanner + 3 strategy engines + self-learning +
                        trade journal + universe auto-refresh (v3.2.1)
journal.py              standalone journal updater, learner refresh & report
config.json             all settings
universe_nifty100.txt   NIFTY 100 symbols - auto-refreshed weekly since
                        v3.2.1 (still editable when universe_refresh is off)
universe_cache.json     auto-refresh bookkeeping (last attempt/update, source)   
START_SCANNER.bat       morning launcher (Windows)
UPDATE_JOURNAL.bat      journal refresh launcher (Windows)
poi_zones_auto.csv      generated every morning by AutoPoi (do not edit)
poi_zones.csv           OPTIONAL manual zone overrides for Strategy 3
journal/                created automatically on first run:
                        trade_journal.csv, daily_summary.csv,
                        journal_state.json, learning_state.json (v3.2)
```

## 8. Troubleshooting

* **`NSE blocked (HTTP 403)`** — normal on server IPs; the scanner switches
  to Yahoo-only automatically. Nothing to do.
* **`yfinance not available`** — run `pip install yfinance`.
* **A symbol shows "may be delisted"** — index members change (e.g. Tata
  Motors split into TMPV/TMCV; LTIMindtree became LTM). Since v3.2.1 the
  scanner fixes this itself: at the next startup past the 7-day window it
  re-fetches the official constituents and rewrites the universe file (you
  get a Telegram message with the +/- diff). To force an immediate refresh,
  delete `universe_cache.json` and restart the scanner. Unknown symbols are
  still skipped harmlessly in the meantime.
* **Journal verdicts look stale** — run `python journal.py`; it back-fills
  from history and rewrites the affected days.
* **Deleted a journal file by accident** — just re-run; missing files are
  recreated, and open-trade state is rebuilt from the CSV.

## 9. Version history

* **v3.2.1** — current release: universe auto-refresh — the scanner now
  updates `universe_nifty100.txt` itself at most once every 7 days from the
  official NSE constituents CSV (home IPs) or Wikipedia NIFTY 50 + Next 50
  (cloud runners), with an 80–120 symbol sanity guard, a `+/-` diff alert on
  Telegram, and `universe_cache.json` bookkeeping (committed by the cloud
  workflow). Delisted/replaced symbols stop erroring without manual edits.
  26-test self-test suite.
* **v3.2** — self-learning engine (studies the last 30
  closed trades, benches statistically losing strategies/directions with
  transparent rules, `journal/learning_state.json` snapshot + daily 🧠
  Telegram digest), daily trade cap raised to 10, engine-wide 13:30 entry
  cutoff.
* **v3.1** — Strategy 3 fully automated — the AutoPoi engine
  marks H4 supply/demand zones every morning from Yahoo 1h history (no manual
  zone entry), config keys for AutoPoi tuning, 23-test self-test suite.
* **v3.0** — three strategy engines, SOP 4.1 capital/cost guards, discipline
  caps, 15:05 directive, hardened 15:10 square-off (NSE LTP → last 5m close →
  journal.py fallback), weekend exit.
* **v2.3** — intermediate build: strategy engines designed; only the 15:10
  loop-break + EOD finalize shipped in the .py many users ran (v2.2.1).
* **v2.2** — integrated self-generating trade journal: automatic outcome
  tracking (WIN/LOSS/EOD), live day verdicts (SUCCESS/FAILED/FLAT), SOP
  circuit-breaker enforcement, restart-proof state, history back-fill,
  Telegram outcome alerts, `journal.py` + `UPDATE_JOURNAL.bat`.
* **v2.1** — short-side mirror signals, NSE batch fast lane with Yahoo
  fallback, two-layer tick→bar pipeline.
* **v1.0** — long-only momentum breakout scanner, CSV signal log.

## 10. Disclaimer

Educational tooling only — not investment advice. Intraday trading carries a
high risk of loss. Past behaviour of any scan does not guarantee future
results. Verify every signal against your broker's live data before acting.
