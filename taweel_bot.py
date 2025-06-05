print("📦 بدأ تشغيل الملف...")

import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
from flask import Flask
import threading
import telegram.error
import asyncio

# 🔐 توكن البوت (يتم استرجاعه من متغيرات البيئة)
TOKEN = os.getenv("BOT_TOKEN") or "7596059153:AAEeVzWhDKc-1xGm6iUE6q1g8P9aSCWSV6Q"

# 📣 معرف جروب النقاش المرتبط بالقناة
CHANNEL_USERNAME = -1002677388715

# حالة السؤال عن الرمز أو علم التعبير
ASKING_QUESTION = 3

# إعداد Flask لفتح المنفذ
app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Bot is running", 200

# بدء المحادثة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["سؤال عن معنى رمز أو الإجابة على سؤال المعبر", "رؤيا"], ["إلغاء"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌙️ مرحبًا بك في بوت (هذا تأويل رؤياي)!")
    await update.message.reply_text("اختر نوع الخطوة:", reply_markup=reply_markup)
    return ConversationHandler.END

# إظهار معرف الشات
async def show_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"Chat ID: `{chat.id}`", parse_mode="Markdown")

# إلغاء المحادثة
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    context.user_data.clear()
    return ConversationHandler.END

# التعامل مع "سؤال" أو "رؤيا"
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    print(f"تم اختيار: {text}")  # تسجيل الخيار
    if text == "إلغاء":
        return await cancel(update, context)

    if text == "سؤال عن علم التعبير أو عن رمز":
        await update.message.reply_text("✍️ فضلًا، اكتب سؤالك وسنقوم بإرساله للمختصين.")
        return ASKING_QUESTION

    elif text == "رؤيا":
        context.user_data.clear()
        keyboard = [["الليلة أو اليوم", "قبل أيام", "قبل أشهر"], ["قبل سنوات", "قبل ظروف معينة"], ["إلغاء"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("🕓 متى رأيت الرؤيا؟", reply_markup=reply_markup)
        context.user_data["flow"] = "ruyaa"
        context.user_data["answers"] = {}
        return ConversationHandler.END

# استقبال السؤال
async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_text = update.message.text.strip()
    print(f"تم استلام سؤال: {question_text}")  # تسجيل السؤال

    if question_text == "إلغاء":
        return await cancel(update, context)

    message = f"❓ سؤال جديد:\n{question_text}"
    print(f"محاولة إرسال الرسالة إلى {CHANNEL_USERNAME}: {message}")  # تسجيل محاولة الإرسال

    try:
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=message)
        await update.message.reply_text("✅ تم إرسال سؤالك، سنرد عليك قريبًا بإذن الله.")
        print("تم الإرسال بنجاح!")  # تأكيد الإرسال
    except telegram.error.TelegramError as e:
        await update.message.reply_text(f"حدث خطأ أثناء إرسال السؤال: {str(e)}. حاول لاحقًا.")
        print(f"Error sending question: {e}")
    return ConversationHandler.END

# جمع بيانات الرؤيا
async def handle_ruyaa_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("flow") != "ruyaa":
        return ConversationHandler.END

    answers = context.user_data.get("answers", {})
    text = update.message.text.strip()
    print(f"رؤيا - إجابة: {text}")  # تسجيل كل إجابة

    if text == "إلغاء":
        return await cancel(update, context)

    if "وقت_الرؤيا" not in answers:
        answers["وقت_الرؤيا"] = text
        context.user_data["answers"] = answers
        keyboard = [["نعم", "لا"], ["إلغاء"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل سبق أن عبّرت الرؤيا عند أحد؟", reply_markup=reply_markup)
        return ConversationHandler.END

    if "سبق_تعبير" not in answers:
        if text == "نعم":
            await update.message.reply_text("شكرًا لك، نعتذر عن تعبير الرؤى التي تم تعبيرها من قبل.")
            context.user_data.clear()
            return ConversationHandler.END
        elif text == "لا":
            answers["سبق_تعبير"] = "لا"
            context.user_data["answers"] = answers
            keyboard = [["ذكر", "أنثى"], ["إلغاء"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("ما جنسك؟", reply_markup=reply_markup)
            return ConversationHandler.END

    if "الجنس" not in answers:
        if text in ["ذكر", "أنثى"]:
            answers["الجنس"] = text
            context.user_data["answers"] = answers
            keyboard = [
                ["أعزب", "عزباء"],
                ["تقدم لي شخص", "خاطب", "مخطوبة"],
                ["متزوج", "متزوجة"],
                ["مطلق", "مطلقة"],
                ["أرمل", "أرملة"],
                ["إلغاء"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("ما حالتك الاجتماعية؟", reply_markup=reply_markup)
            return ConversationHandler.END

    if "الحالة_الاجتماعية" not in answers:
        answers["الحالة_الاجتماعية"] = text
        context.user_data["answers"] = answers
        if text in ["تقدم لي شخص", "خاطب", "مخطوبة", "متزوج", "متزوجة", "مطلق", "مطلقة"]:
            await update.message.reply_text("منذ متى ؟ (اكتب المدة التقريبية للحالة الاجتماعية)")
            return ConversationHandler.END
        else:
            keyboard = [["نعم", "لا"], ["إلغاء"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("هل عندك أولاد؟", reply_markup=reply_markup)
            return ConversationHandler.END

    if "مدة_الحالة" not in answers and answers["الحالة_الاجتماعية"] in ["تقدم لي شخص", "خاطب", "مخطوبة", "متزوج", "متزوجة", "مطلق", "مطلقة"]:
        answers["مدة_الحالة"] = text
        context.user_data["answers"] = answers
        keyboard = [["نعم", "لا"], ["إلغاء"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل عندك أولاد؟", reply_markup=reply_markup)
        return ConversationHandler.END

    if "عندك_أولاد" not in answers:
        if text in ["نعم", "لا"]:
            answers["عندك_أولاد"] = text
            context.user_data["answers"] = answers
            if text == "نعم":
                await update.message.reply_text("كم عدد الأولاد الذكور؟")
            else:
                answers["عدد_الذكور"] = "0"
                answers["عدد_البنات"] = "0"
                keyboard = [["نعم", "قدمت على وظيفة"], ["لا أعمل", "طالب", "طالبة"], ["إلغاء"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                await update.message.reply_text("هل تعمل؟", reply_markup=reply_markup)
            return ConversationHandler.END

    if "عدد_الذكور" not in answers and answers["عندك_أولاد"] == "نعم":
        try:
            if not text.isdigit():
                await update.message.reply_text("يرجى إدخال رقم صحيح لعدد الأولاد الذكور.")
                return ConversationHandler.END
            answers["عدد_الذكور"] = text
            context.user_data["answers"] = answers
            await update.message.reply_text("كم عدد البنات؟")
        except ValueError:
            await update.message.reply_text("يرجى إدخال رقم صحيح لعدد الأولاد الذكور.")
        return ConversationHandler.END

    if "عدد_البنات" not in answers and answers["عندك_أولاد"] == "نعم":
        try:
            if not text.isdigit():
                await update.message.reply_text("يرجى إدخال رقم صحيح لعدد البنات.")
                return ConversationHandler.END
            answers["عدد_البنات"] = text
            context.user_data["answers"] = answers
            keyboard = [["نعم", "قدمت على وظيفة"], ["لا أعمل", "طالب", "طالبة"], ["إلغاء"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("هل تعمل؟", reply_markup=reply_markup)
        except ValueError:
            await update.message.reply_text("يرجى إدخال رقم صحيح لعدد البنات.")
        return ConversationHandler.END

    if "العمل" not in answers:
        answers["العمل"] = text
        context.user_data["answers"] = answers
        keyboard = [["نعم", "لا"], ["إلغاء"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل تنتظر شيئًا له علاقة بالرؤيا؟", reply_markup=reply_markup)
        return ConversationHandler.END

    if "ينتظر_شيء" not in answers:
        if text in ["نعم", "لا"]:
            answers["ينتظر_شيء"] = text
            context.user_data["answers"] = answers
            keyboard = [["نعم", "لا"], ["إلغاء"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("هل أنت على رقية أو مصاب بمرض روحي؟", reply_markup=reply_markup)
            return ConversationHandler.END

    if "رقية" not in answers:
        if text in ["نعم", "لا"]:
            answers["رقية"] = text
            context.user_data["answers"] = answers
            await update.message.reply_text("اكتب الرؤيا بالتفصيل ولمعرفة التعبير تابع مجموعة الشات هذا تأويل رؤياي:")
            return ConversationHandler.END

    if "نص_الرؤيا" not in answers:
        answers["نص_الرؤيا"] = text
        context.user_data["answers"] = answers
        await update.message.reply_text("هل توجد معلومات إضافية لها علاقة بالرؤيا؟ (يمكنك كتابة أي شيء):")
        return ConversationHandler.END

    if "إضافات" not in answers:
        answers["إضافات"] = text
        message = f"""🌙 رؤيا جديدة:

🕓 وقت الرؤيا: {answers['وقت_الرؤيا']}
🙋 الجنس: {answers['الجنس']}
📌 الحالة الاجتماعية: {answers['الحالة_الاجتماعية']}
⏳ مدة الحالة: {answers.get('مدة_الحالة', '—')}

👶 عدد الأولاد: {answers.get('عدد_الذكور', '0')} ذكور / {answers.get('عدد_البنات', '0')} بنات
💼 العمل: {answers['العمل']}
⏱️ ينتظر شيئًا له علاقة؟ {answers['ينتظر_شيء']}
🔮 على رقية أو مصاب؟ {answers['رقية']}

📝 نص الرؤيا:
{answers['نص_الرؤيا']}

🔍 إضافات:
{answers['إضافات']}
"""
        print(f"محاولة إرسال الرؤيا إلى {CHANNEL_USERNAME}: {message}")  # تسجيل محاولة الإرسال

        try:
            await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=message)
            await update.message.reply_text("✅ تم استلام الرؤيا وإرسالها للمراجعة، وسيتم الرد قريبًا بإذن الله.")
            print("تم إرسال الرؤيا بنجاح!")  # تأكيد الإرسال
        except telegram.error.TelegramError as e:
            await update.message.reply_text(f"حدث خطأ أثناء إرسال الرؤيا: {str(e)}. حاول لاحقًا.")
            print(f"Error sending dream: {e}")
        context.user_data.clear()
        return ConversationHandler.END

# إعداد التطبيق
app_bot = ApplicationBuilder().token(TOKEN).build()

# إضافة المعالجات
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("myid", show_chat_id))
app_bot.add_handler(ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^(سؤال عن علم التعبير أو عن رمز|رؤيا)$"), handle_choice),
    ],
    states={
        ASKING_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^إلغاء$"), cancel)
    ],
))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(سؤال عن علم التعبير أو عن رمز|رؤيا)$"), handle_ruyaa_flow))

# تشغيل البوت في خيط منفصل
def run_bot():
    print("🤖 البوت يعمل الآن... افتحه في تيليجرام وجرب /start أو /myid داخل الجروب")
    app_bot.run_polling(drop_pending_updates=True)

# بدء الخدمة
if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    # لا نشغل Flask يدويًا، Render سيتولى ذلك باستخدام gunicorn
    print("Flask application ready for Render to serve via WSGI.")