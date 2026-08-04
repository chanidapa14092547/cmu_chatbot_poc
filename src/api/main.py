import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic_engine.bot_brain import process_message

load_dotenv()

app = FastAPI(title="CMU Chatbot POC")

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", ""))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET", ""))

def reply_line_message(reply_token: str, text: str):
    try:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=text)
        )
    except Exception as e:
        print(f"Error replying to LINE: {e}")

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    try:
        # Check signature and handle event
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    
    # Process message through AI Brain
    bot_reply = process_message(user_text)
    
    # Send reply back to LINE
    reply_line_message(event.reply_token, bot_reply)

@app.get("/")
def root():
    return {"status": "ok", "message": "CMU Chatbot Webhook is running!"}
