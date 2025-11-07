# app.py
from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessage
from dotenv import load_dotenv
import os
import openai

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

messaging_api = MessagingApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_data(as_text=True)
    events = messaging_api.parse_events_from(body)

    for event in events:
        if isinstance(event.message, TextMessage):
            user_text = event.message.text
            # ChatGPT に問い合わせ
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_text}]
            )
            reply_text = response.choices[0].message.content

            messaging_api.reply_message(
                event.reply_token,
                TextMessage(text=reply_text)
            )

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
