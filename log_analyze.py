import matplotlib.pyplot as plt
from collections import Counter

log_file = "logs/app.log"

# カウント用
counter = Counter()

# ログを読む
with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        if "AI_SUCCESS" in line:
            counter["正常応答"] += 1
        elif "AI_ERROR" in line:
            counter["AIエラー"] += 1
        elif "INVALID_SIGNATURE" in line:
            counter["不正署名"] += 1
        elif "NON_TEXT" in line:
            counter["非テキスト"] += 1

labels = list(counter.keys())
values = list(counter.values())

# 棒グラフ
plt.bar(labels, values)
plt.title("セキュリティ・安定性検証結果")
plt.ylabel("発生回数")
plt.xlabel("イベント種別")
plt.tight_layout()
plt.show()
