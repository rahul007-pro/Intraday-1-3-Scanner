#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone TRADE JOURNAL updater & reporter (companion to scanner.py v2.2).

Run this any time - ideally right after 15:10 IST, or the next morning:
  python journal.py

It will, with zero setup:
  1. auto-create journal/trade_journal.csv, daily_summary.csv,
     journal_state.json if they do not exist yet;
  2. back-fill the outcome of every OPEN trade from Yahoo price history
     (target hit -> WIN, stop hit -> LOSS, 15:10 -> EOD square-off), even
     for sessions when the PC/scanner was switched off;
  3. refresh the DayVerdict (SUCCESS / FAILED / FLAT) for every affected
     day in daily_summary.csv, including circuit-breaker flags;
  4. print a report: open trades, today's verdict, last 7 days, overall
     win rate and expectancy in R.

Windows users can simply double-click UPDATE_JOURNAL.bat.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import (VERSION, load_config, make_bar_provider, send_telegram,
                     TradeJournal)


def main():
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    print(f"Trade Journal updater - scanner v{VERSION}")
    cfg = load_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "config.json"))
    j = TradeJournal(base_dir=os.path.dirname(os.path.abspath(__file__)),
                     cfg=cfg, notify=send_telegram)
    try:
        j.catch_up(make_bar_provider(cfg))
    except Exception as e:
        print(f"[JOURNAL] history back-fill unavailable ({e}); "
              f"verdicts updated from local data only")
    print()
    print(j.report())
    print()
    print("Tip: open trade_journal.csv in Excel for the full trade-by-trade "
          "log, or daily_summary.csv for day verdicts.")


if __name__ == "__main__":
    main()
