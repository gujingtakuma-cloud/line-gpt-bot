import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
from dotenv import load_dotenv
import threading  # バックグラウンド用

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'  # LINEに即返す

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # バックグラウンドでOpenAI APIを呼び出す
    threading.Thread(target=reply_gpt, args=(event.reply_token, user_text)).start()

def reply_gpt(reply_token, user_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_text}],
            temperature=0.7,
            request_timeout=60  # タイムアウト長めに設定
        )
        reply_text = response['choices'][0]['message']['content']
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=reply_text)
        )
    except Exception as e:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Sorry, there was an error processing your request.")
        )
        print("Error:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def reply_gpt(reply_token, user_text):
    try:
        if not openai.api_key:
            print("Error: OPENAI_API_KEY is not set!")
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="API key is missing!")
            )
            return

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_text}],
            temperature=0.7,
            request_timeout=60
        )
        reply_text = response['choices'][0]['message']['content']
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=reply_text)
        )
    except Exception as e:
        print("Error:", e)  # Render のログで確認
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"Error: {str(e)}")
        )
