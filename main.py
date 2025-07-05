import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError
from contextlib import asynccontextmanager

TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

application = ApplicationBuilder().token(TOKEN).build()

async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("请输入时间，例如 /countdown 10分钟")
        return
    time_text = args[0].replace("分钟", "").replace("分", "")
    try:
        minutes = int(time_text)
        await update.message.reply_text(f"✅ 开始倒数 {minutes} 分钟！")
    except ValueError:
        await update.message.reply_text("❌ 时间格式错误，请输入整数分钟，例如 /countdown 10分钟")

application.add_handler(CommandHandler("countdown", countdown))

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await application.bot.delete_webhook()
        await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
        await application.bot.set_my_commands([
            BotCommand("countdown", "倒数计时（例如 /countdown 10分钟）")
        ])
        logging.info("✅ Webhook 和指令注册成功")
    except Exception as e:
        logging.error(f"❌ 设置 Webhook 失败: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except TelegramError as e:
        logging.error(f"处理更新出错: {e}")
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Bot is running"}
