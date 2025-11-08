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
