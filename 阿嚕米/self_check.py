from calendar_time_parser import parse_nl_time
import pytz

examples = [
    "今天晚上 8 點",
    "明天下午 2 點到 3 點",
    "2025-11-03 20:00",
    "下週一上午 10 點",
]

tz = pytz.timezone('Asia/Taipei')

for ex in examples:
    dt = parse_nl_time(ex)
    print(f"Input: {ex}")
    if dt is None:
        print("  -> 無法解析")
    else:
        # normalize to Asia/Taipei and print formatted
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)
        print("  -> Parsed (ISO):", dt.isoformat())
        print("  -> Formatted :", dt.strftime('%Y-%m-%d %H:%M:%S'))
    print()
