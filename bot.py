# bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import logging
import os

# 🛠️ اطلاعات شخصی (از محیط متغیرهای Render خوانده می‌شوند)
BOT_TOKEN = os.getenv("BOT_TOKEN")             # مقدار: توکن ربات
TARGET_CHAT = os.getenv("TARGET_CHAT")         # مقدار: یوزرنیم کانال/گروه (مثلاً @mgclubscreencaptures)
TARGET_TOPIC_ID = int(os.getenv("TARGET_TOPIC_ID", "0"))  # مقدار: ID تاپیک، پیش‌فرض 0 (جنرال)

# 🪵 تنظیم لاگینگ برای دیباگ (می‌توانید سطحش را به ERROR تغییر دهید در محیط اصلی)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    این تابع وقتی ربات فیلم دریافت می‌کند فراخوانی می‌شود.
    1. ویدیو را به گروه/کانال TARGET_CHAT فوروارد می‌کند.
    2. لینک پیام فورواردشده را به کاربر ارسال می‌کند.
    """
    if not update.message:
        return

    user = update.message.from_user
    video = update.message.video

    if not video:
        # اگر پیامی غیر از ویدیو ارسال شد، اعلام خطا یا اطلاع دهید
        await update.message.reply_text("❌ فقط فایل ویدیویی قابل پذیرش است.")
        return

    # فورواردِ پیام ویدیو به TARGET_CHAT (و تاپیک مشخص شده)
    forwarded_message = await update.message.forward(
        chat_id=TARGET_CHAT,
        message_thread_id=TARGET_TOPIC_ID  # اگر ID تاپیک را 0 (جنرال) گذاشتید، همان جنرال است
    )

    # ساخت لینک مستقیم پست (برای گروه‌های Public)
    # فرمت: https://t.me/<chat_username_without_@>/<message_id>
    chat_username = TARGET_CHAT.lstrip("@")
    message_id = forwarded_message.message_id
    message_link = f"https://t.me/{chat_username}/{message_id}"

    # نام و آیدی فرستنده
    if user.username:
        name = f"{user.full_name} (@{user.username})"
    else:
        name = user.full_name

    # ارسال پیام پاسخ به فرستنده با لینک پست
    await update.message.reply_text(
        f"✅ ویدیوی شما با موفقیت ارسال شد.\n"
        f"👤 فرستنده: {name}\n"
        f"🔗 لینک پست در کانال/گروه: {message_link}"
    )

if __name__ == "__main__":
    # ساخت اپلیکیشن ربات با توکن از متغیر محیطی
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # فقط پیام‌های نوع ویدیو را هندل می‌کنیم
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # اجرای ربات به‌صورت Polling (کامل ً آنلاین می‌ماند)
    app.run_polling()
