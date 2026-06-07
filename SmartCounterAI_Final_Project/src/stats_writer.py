import csv
import os
from datetime import datetime


def save_events_csv(csv_path, events, summary):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerow(["SmartCounterAI - Counting Events"])
        writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])

        writer.writerow([
            "frame",
            "time_sec",
            "track_id",
            "class_name",
            "direction",
            "line",
            "total_count",
            "class_count",
        ])

        for event in events:
            writer.writerow([
                event["frame"],
                event["time_sec"],
                event["track_id"],
                event["class_name"],
                event["direction"],
                event["line"],
                event["total_count"],
                event["class_count"],
            ])

        writer.writerow([])
        writer.writerow(["Summary"])
        writer.writerow(["Total", summary.get("total", 0)])
        writer.writerow(["Line Mode", summary.get("line_mode", "")])
        writer.writerow(["Line X", summary.get("line_x", "")])
        writer.writerow(["Line Y", summary.get("line_y", "")])

        writer.writerow([])
        writer.writerow(["By Class"])
        for key, value in summary.get("by_class", {}).items():
            writer.writerow([key, value])

        writer.writerow([])
        writer.writerow(["By Direction"])
        for key, value in summary.get("by_direction", {}).items():
            writer.writerow([key, value])
