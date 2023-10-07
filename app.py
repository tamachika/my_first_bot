from email import message
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from chat import chat_completion

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

def is_prime(i):
    if i <= 1:
        return False
    for j in range(2, int(i**0.5) + 1):
        if i % j == 0:
            return False
    return True

@app.route('/')
def index():
    return 'You call index()'


@app.route("/push_sample")
def push_sample():
    """プッシュメッセージを送る"""
    user_id = os.environ["USER_ID"]
    line_bot_api.push_message(user_id, TextSendMessage(text="Hello World!"))

    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    """Messaging APIからの呼び出し関数"""
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    i = int(event.message.text)
    if type(i) == int:
        if i <= 1:
            return False
        ans = "素数です"
        for j in range(2, int(i**0.5) + 1):
            if i % j == 0:
                ans = "合成数です"
                break
        line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=f"{event.message.text}は{ans}"))
    if event.message.text > "あ":
         reply_message = chat_completion(event.message.text)   
         line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=reply_message))
    

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)