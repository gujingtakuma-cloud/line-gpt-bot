# app.py
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessageEvent, TextMessage
from dotenv import load_dotenv
import os
import openai

# .env を読み込む
load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LINE API
messaging_api = MessagingApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAI API
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers.get("X-Line-Signature")

    try:
        handler.handle(body, signature)
    except Exception:
        abort(400)
    return "OK"

# メッセージハンドラー
@handler.add(TextMessageEvent)
def handle_text(event: TextMessageEvent):
    user_text = event.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # あるいは "gpt-3.5-turbo"
            messages=[{"role": "user", "content": user_text}]
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        reply_text = f"エラーが発生しました: {str(e)}"

    messaging_api.reply_message(
        event.reply_token,
        TextMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
