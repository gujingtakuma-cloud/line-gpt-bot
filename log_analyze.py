from collections import Counter

counts = Counter()

with open("logs/app.log", encoding="utf-8") as f:
    for line in f:
        if "AI_SUCCESS" in line:
            counts["AI_SUCCESS"] += 1
        elif "AI_ERROR" in line:
            counts["AI_ERROR"] += 1
        elif "INVALID_SIGNATURE" in line:
            counts["INVALID_SIGNATURE"] += 1
        elif "NON_TEXT" in line:
            counts["NON_TEXT"] += 1
        elif "BLOCKED_QUESTION" in line:
            counts["BLOCKED_QUESTION"] += 1

print(counts)
