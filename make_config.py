#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build config.json from environment variables (GitHub Actions Secrets).

Run inside the workflow before scanner.py / journal.py. Also usable
locally:  set the variables and run `python make_config.py`.

Secrets (all OPTIONAL - SOP Phase V defaults apply when absent):

  SCANNER_CAPITAL      account capital in rupees          (default 25000)
  SCANNER_RISK_PCT     risk per trade, percent of capital (default 0.25)
  SCANNER_RISK_RR      reward-to-risk ratio               (default 3)
  TELEGRAM_BOT_TOKEN   token from @BotFather              (default empty)
  TELEGRAM_CHAT_ID     your numeric chat id               (default empty)
  DATA_MODE            auto | nse | yahoo                 (default auto)

Telegram left empty = scanner runs fine, alerts just stay in the
Actions log instead of your phone. GitHub masks secret values in
logs automatically, and config.json is git-ignored so it can never
be committed by accident.
"""

import json
import os

DEFAULTS = {
    "data_mode": "auto",           # auto | nse | yahoo
    "universe_file": "universe_nifty100.txt",
    "scan_interval_min": 5,
    "scan_start": "09:30",
    "entry_cutoff": "13:30",
    "squareoff": "15:10",
    "capital": 25000,
    "risk_pct": 0.25,
    "rr": 3.0,
    "sl_buffer_pct": 0.10,
    "max_stop_pct": 1.5,
    "min_bars": 15,
    "min_price": 50,
    "min_turnover": 10000000,
    "min_range_pct": 0.40,
    "rvol_mult": 2.0,
    "min_bar_volume": 2000,
    "close_extreme_pct": 25,
}


def _num(name, cast, fallback):
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return fallback
    try:
        return cast(float(raw))
    except ValueError:
        print(f"[CONFIG] {name}={raw!r} is not a number - using {fallback}")
        return fallback


def build():
    cfg = dict(DEFAULTS)
    cfg["capital"] = _num("SCANNER_CAPITAL", int, cfg["capital"])
    cfg["risk_pct"] = _num("SCANNER_RISK_PCT", float, cfg["risk_pct"])
    cfg["rr"] = _num("SCANNER_RISK_RR", float, cfg["rr"])

    mode = (os.environ.get("DATA_MODE") or "auto").strip().lower()
    if mode not in ("auto", "nse", "yahoo"):
        print(f"[CONFIG] DATA_MODE={mode!r} invalid - using 'auto'")
        mode = "auto"
    cfg["data_mode"] = mode

    cfg["telegram"] = {
        "bot_token": (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip(),
        "chat_id": (os.environ.get("TELEGRAM_CHAT_ID") or "").strip(),
    }

    cfg["journal"] = {                # SOP circuit breakers
        "folder": "journal",
        "daily_loss_limit_R": -2.0,
        "daily_loss_limit_amt": 0,
        "max_consecutive_losses": 2,
    }
    return cfg


def main():
    cfg = build()
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print(f"[CONFIG] config.json built | capital Rs {cfg['capital']} | "
          f"risk {cfg['risk_pct']}% | RR 1:{cfg['rr']:g} | "
          f"data_mode {cfg['data_mode']} | telegram "
          f"{'ON' if cfg['telegram']['bot_token'] and cfg['telegram']['chat_id'] else 'OFF (log only)'}")


if __name__ == "__main__":
    main()
