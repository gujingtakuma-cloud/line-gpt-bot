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

    if not isinstance(event.message, TextMessage):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="テキストを送信してください。")
        )
        return

    user_id = event.source.user_id
    text = (event.message.text or "").strip()

    # --- リッチメニュー HELP ---
    if text.lower() == "AIに相談":
        user_state[user_id] = "waiting_question"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("何か聞きたいことはありますか。")
        )
        if user_state.get(user_id) == "waiting_question":
            rule = (
                "あなたはLINEの使い方に限定して回答するAIです。"
                "LINEに関係ない質問には「このAIはLINEの使い方に関する質問のみ受け付けています。」と答えてください。\n\n"
            )
            prompt = rule + f"ユーザーの質問: {text}"
            try:
                result = client.models.generate_content(
                    model=MODEL,
                    contents=[prompt]
                )
                reply = result.text if result.text else "回答を取得できませんでした。"
            except Exception as e:
                reply = f"AI応答エラー: {str(e)}"
                user_state.pop(user_id, None)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply)
                )
                return



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
