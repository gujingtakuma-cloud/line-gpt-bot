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
        user_state[user_id] = "waiting_question"
        reply_text = "何か聞きたいことはありますか。"
        print(f"Reply: {reply_text}")

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return

    # waiting_question
    if user_state.get(user_id) == "waiting_question":

        prompt = (
            "あなたはLINEの使い方に限定して回答する AI です。\n"
            "LINEに関係ない質問には次のように答えてください：\n"
            "「このAIはLINEの使い方に関する質問のみ受け付けています。」\n\n"
            f"ユーザーの質問: {text}"
        )

        try:
            print("Sending to Gemini...")
            result = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=[prompt]
            )
            ai_reply = result.text or "回答を取得できませんでした。"

        except Exception as e:
            ai_reply = f"AI応答エラー: {str(e)}"

        print(f"AI Reply: '{ai_reply}'")

        user_state.pop(user_id, None)

        if not ai_reply.strip():
            ai_reply = "回答が空でした。もう一度お試しください。"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_reply)
        )
        return



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
