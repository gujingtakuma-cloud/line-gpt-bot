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

# Gemini API クライアント
client = genai.Client(api_key=GEMINI_API_KEY)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_text
        )
        reply_text = response.text if response.text else "返答が取得できませんでした。"
    except Exception as e:
        print("Gemini API error:", e)
        reply_text = "エラーが発生しました。しばらくしてからもう一度お試しください。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

session = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text

    # モード開始
    if user_text == "AIに相談":
        session[user_id] = "use_help"
        reply = "質問をどうぞ。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 回答
    if session.get(user_id) == "use_help":
        # AIに渡す
        ...
        reply_text = "（AIの回答）"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        # 解除
        session[user_id] = None
        return

