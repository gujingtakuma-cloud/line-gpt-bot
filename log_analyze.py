from collections import Counter
import matplotlib.pyplot as plt
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

labels = ["正常応答", "AIエラー", "不正署名", "非テキスト", "ブロック"]
values = [
    counts["AI_SUCCESS"],
    counts["AI_ERROR"],
    counts["INVALID_SIGNATURE"],
    counts["NON_TEXT"],
    counts["BLOCKED_QUESTION"]
]

plt.bar(labels, values)
plt.title("セキュリティ・安定性検証結果")
plt.ylabel("発生回数")
plt.show()
