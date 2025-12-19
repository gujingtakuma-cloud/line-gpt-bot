import matplotlib.pyplot as plt
print("LOG: AI_SUCCESS")
log_count = {
    "AI_SUCCESS": 0,
    "AI_ERROR": 0,
    "INVALID_SIGNATURE": 0,
    "NON_TEXT": 0,
    "BLOCKED_QUESTION": 0
}

log_count["AI_SUCCESS"] += 1
log_count["AI_ERROR"] += 1
log_count["NON_TEXT"] += 1
labels = ["正常応答", "AIエラー", "不正署名", "非テキスト", "ブロック"]
values = [
    log_count["AI_SUCCESS"],
    log_count["AI_ERROR"],
    log_count["INVALID_SIGNATURE"],
    log_count["NON_TEXT"],
    log_count["BLOCKED_QUESTION"]
]

plt.bar(labels, values)
plt.title("セキュリティ・安定性検証結果")
plt.ylabel("発生回数")
plt.show()
