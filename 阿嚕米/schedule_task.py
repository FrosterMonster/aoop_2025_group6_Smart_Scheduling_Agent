"""Simple runner to plan and schedule a weekly task.

Usage (PowerShell example):
$env:DRY_RUN = '1'; C:/path/to/.venv/Scripts/python.exe schedule_task.py --summary "讀電子學" --hours 4

The runner respects DRY_RUN and will print planned results.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime

from calendar_tools import plan_week_schedule

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, help="Event summary / task name, e.g. '讀電子學'")
    parser.add_argument("--hours", type=float, required=True, help="Total hours to schedule for the week (e.g. 4)")
    parser.add_argument("--chunk", type=float, default=2.0, help="Preferred chunk size in hours (default 2)")
    parser.add_argument("--calendar", default="primary", help="Calendar ID (default primary)")
    args = parser.parse_args()

    print(f"DRY_RUN={os.environ.get('DRY_RUN')}. Planning task: '{args.summary}' for {args.hours} hours (chunk={args.chunk}h)")
    planned = plan_week_schedule(args.summary, args.hours, calendar_id=args.calendar, chunk_hours=args.chunk)

    if not planned:
        print("沒有可用時段或未排入任何活動。請檢查日曆權限或調整時間視窗。")
        return

    print(f"已排入 {len(planned)} 個時段 (總時數目標 {args.hours} 小時):")
    for i, p in enumerate(planned, 1):
        s = p['start'].strftime('%Y-%m-%d %H:%M')
        e = p['end'].strftime('%Y-%m-%d %H:%M')
        print(f"{i}. {s} -> {e}  -> {p['result']}")

if __name__ == '__main__':
    main()