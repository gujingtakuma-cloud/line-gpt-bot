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

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "models/gemini-2.0-flash"

user_mode = {}  # {user_id: True/False}


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()

    if user_text == "AIに相談":
        user_mode[user_id] = True
        reply = "何か聞きたいことはありますか。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    if user_mode.get(user_id, False):

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_text
            )
            ai_reply = response.text or "（空の応答でした）"
        except Exception as e:
            ai_reply = f"AI応答エラー: {str(e)}"

        # 回答を返す
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_reply)
        )

        user_mode[user_id] = False
        return

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=default_reply))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
