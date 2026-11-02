# Intraday Scanner v3.1 — All Three SOP Strategies, Fully Automated

(AutoPoi zone marking + guaranteed 15:10 square-off)

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

## 1. What's new in v3.0 / v3.1 — three strategy engines + end-of-day automation

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
| **Discipline caps** | SOP 3.4 / Phase V: max 2 concurrent positions, max 3 entries/day (config: `max_concurrent_positions`, `max_trades_per_day`). |

### What stays manual (deliberately, per the SOP)
* **Type 04** rules — still a placeholder in the SOP itself; nothing to encode.
* **H4 POI zones** — automated since v3.1 (AutoPoi engine, see §Strategy 3);
  `poi_zones.csv` is now an OPTIONAL override for zones you want to force.
* **Final trade approval** — the scanner alerts, you verify in the broker
  terminal and fire the order (the SOP 12-point checklist stays yours).
* **Sector-correlation check** and the **regime choice** of which strategy to
  favour — journal checklist items.

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
python scanner.py --selftest # built-in test suite (23 checks)
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

Anything you delete from `config.json` is merged back from built-in defaults,
so the journal keeps working even with an old config file.

## 7. Files in this package

```
scanner.py              scanner + 3 strategy engines + trade journal (v3.1)
journal.py              standalone journal updater & report
config.json             all settings
universe_nifty100.txt   NIFTY 100 symbols (edit freely; # comments)
START_SCANNER.bat       morning launcher (Windows)
UPDATE_JOURNAL.bat      journal refresh launcher (Windows)
poi_zones_auto.csv      generated every morning by AutoPoi (do not edit)
poi_zones.csv           OPTIONAL manual zone overrides for Strategy 3
journal/                created automatically on first run
```

## 8. Troubleshooting

* **`NSE blocked (HTTP 403)`** — normal on server IPs; the scanner switches
  to Yahoo-only automatically. Nothing to do.
* **`yfinance not available`** — run `pip install yfinance`.
* **A symbol shows "may be delisted"** — index names change (e.g. Tata Motors
  split into TMPV/TMCV; LTIMindtree became LTM). Edit
  `universe_nifty100.txt`; unknown symbols are skipped harmlessly.
* **Journal verdicts look stale** — run `python journal.py`; it back-fills
  from history and rewrites the affected days.
* **Deleted a journal file by accident** — just re-run; missing files are
  recreated, and open-trade state is rebuilt from the CSV.

## 9. Version history

* **v3.1** — current release: Strategy 3 fully automated — the AutoPoi engine
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
