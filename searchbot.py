import os
from telethon import TelegramClient
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from telethon.tl.functions.users import GetFullUserRequest

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
bot_token = os.environ["BOT_TOKEN"]

tg = TelegramClient("session", api_id, api_hash)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("اكتب:\n/search @username أو /search user_id")
        return

    query = context.args[0].replace("@", "")
    await update.message.reply_text(f"🔍 جاري جمع المعلومات عن: {query}")
    await tg.start()

    # معلومات الحساب
    try:
        user = await tg(GetFullUserRequest(query))
        u = user.users[0]
        text = (
            f"👤 الاسم: {u.first_name or ''} {u.last_name or ''}\n"
            f"🔗 اليوزر: @{u.username}\n"
            f"🆔 ID: {u.id}\n"
            f"🤖 بوت: {'نعم' if u.bot else 'لا'}\n\n"
        )
    except:
        text = "❌ لم أستطع جلب معلومات الحساب.\n\n"

    # البحث في القنوات والمجموعات العامة
    result = await tg(SearchRequest(
        peer='t.me',
        q=query,
        filter=InputMessagesFilterEmpty(),
        limit=50,
        offset_id=0,
        add_offset=0,
        max_id=0,
        min_id=0,
        hash=0
    ))

    places = {}
    for msg in result.messages:
        try:
            chat = await msg.get_chat()
            name = chat.title
            link = f"https://t.me/{chat.username}" if chat.username else "بدون رابط عام"
            places[name] = link
        except:
            pass

    if places:
        text += "📍 القنوات والمجموعات العامة:\n\n"
        for name, link in places.items():
            text += f"{name}\n{link}\n\n"
    else:
        text += "❌ لا توجد نتائج عامة."

    await update.message.reply_text(text)

app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler("search", search))

print("Bot running...")
app.run_polling()