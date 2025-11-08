import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

client = genai.Client(api_key=GEMINI_API_KEY)

session = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
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

    if user_text == "使い方モード":
        session[user_id] = "awaiting_question"
        reply = "使い方相談モードです。質問を1つ送ってください。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if session.get(user_id) == "awaiting_question":
        session[user_id] = None
        try:
            ai_res = client.models.generate_content(
                model="models/gemini-pro",
                contents=user_text
            )
            reply_text = ai_res.text or "応答を取得できませんでした。"
        except Exception as e:
            reply_text = "AI応答エラー: " + str(e)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

    ai_res = client.models.generate_content(
        model="models/gemini-pro",
        contents=user_text
    )
    reply_text = ai_res.text or "応答できませんでした。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
