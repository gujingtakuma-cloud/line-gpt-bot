import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "models/gemini-2.5-flash"

# 状態管理
user_state = {}  # {user_id: "waiting_question"}


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):

    print("=== EVENT RECEIVED ===")
    print(event)
    print("======================")

    if not isinstance(event.message, TextMessage):
        print("Non-text message received")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="テキストを送ってください。")
        )
        return

    user_id = event.source.user_id
    text = (event.message.text or "").strip()

    print(f"User ID: {user_id}")
    print(f"Received text: '{text}'")
    print(f"User state: {user_state.get(user_id)}")

    # HELP
    if text == "AIに相談":
        user_state[user_id] = {"mode": "waiting", "count": 2}
        reply_text = "何か聞きたいことはありますか。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return


    # waiting_question
    state = user_state.get(user_id)
    if state and state.get("mode") == "waiting":

        prompt = (
            "あなたはLINEの使い方を回答する親切な AI です。\n\n"
            f"ユーザーの質問: {text}"
        )

        try:
            result = client.models.generate_content(
                model=MODEL,
                contents=[prompt]
            )
            ai_reply = result.text or "回答を取得できませんでした。"
        except Exception as e:
            ai_reply = f"AI応答エラー: {str(e)}"

        # 回数を減らす
        state["count"] -= 1

        # 回数終了
        if state["count"] <= 0:
            user_state.pop(user_id, None)
            ai_reply += "\n\n🎉 相談回数が終了しました。また聞きたい場合は「AIに相談」と入力してください。"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_reply)
        )
        return

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
