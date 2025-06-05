from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# 🔐 توكن البوت
TOKEN = "7596059153:AAEeVzWhDKc-1xGm6iUE6q1g8P9aSCWSV6Q"

# 📣 معرف جروب النقاش المرتبط بالقناة
CHANNEL_USERNAME = -1002677388715

# بدء المحادثة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["سؤال", "رؤيا"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "مرحبًا بك في بوت (هذا تأويل رؤياي) 🌙\n\nاختر نوع الخدمة:",
        reply_markup=reply_markup
    )

# إظهار معرف الشات
async def show_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"Chat ID: `{chat.id}`", parse_mode="Markdown")

# التعامل مع "سؤال" أو "رؤيا"
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "سؤال":
        await update.message.reply_text("فضلًا اكتب سؤالك بالتفصيل، وسنرد عليك في أقرب وقت بإذن الله.")
        context.user_data.clear()
    elif text == "رؤيا":
        keyboard = [
            ["الليلة أو اليوم"], ["قبل أيام"], ["قبل أسابيع"],
            ["قبل شهور"], ["قبل سنوات"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("متى رأيت الرؤيا؟", reply_markup=reply_markup)
        context.user_data["flow"] = "ruyaa"
        context.user_data["answers"] = {}

# جمع بيانات الرؤيا
async def handle_ruyaa_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("flow") != "ruyaa":
        return

    answers = context.user_data.get("answers", {})
    text = update.message.text.strip()

    if "وقت_الرؤيا" not in answers:
        answers["وقت_الرؤيا"] = text
        context.user_data["answers"] = answers
        keyboard = [["نعم", "لا"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل سبق أن عبّرت الرؤيا عند أحد؟", reply_markup=reply_markup)
        return

    if "سبق_تعبير" not in answers:
        if text == "نعم":
            await update.message.reply_text("شكرًا لك، نعتذر عن تعبير الرؤى التي تم تعبيرها من قبل.")
            context.user_data.clear()
            return
        elif text == "لا":
            answers["سبق_تعبير"] = "لا"
            context.user_data["answers"] = answers
            keyboard = [["ذكر", "أنثى"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("ما جنسك؟", reply_markup=reply_markup)
            return

    if "الجنس" not in answers:
        if text in ["ذكر", "أنثى"]:
            answers["الجنس"] = text
            context.user_data["answers"] = answers
            keyboard = [
                ["أعزب", "عزباء"],
                ["تقدم لي شخص", "خاطب", "مخطوبة"],
                ["متزوج", "متزوجة"],
                ["مطلق", "مطلقة"],
                ["أرمل", "أرملة"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("ما حالتك الاجتماعية؟", reply_markup=reply_markup)
            return

    if "الحالة_الاجتماعية" not in answers:
        answers["الحالة_الاجتماعية"] = text
        context.user_data["answers"] = answers
        if text in ["تقدم لي شخص", "خاطب", "مخطوبة", "متزوج", "متزوجة", "مطلق", "مطلقة"]:
            await update.message.reply_text("منذ متى -الحالة الاجتماعية-؟ (اكتب المدة التقريبية)")
            return
        else:
            await update.message.reply_text("هل عندك أولاد؟", reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], one_time_keyboard=True, resize_keyboard=True))
            return

    if "مدة_الحالة" not in answers and answers["الحالة_الاجتماعية"] in ["تقدم لي شخص", "خاطب", "مخطوبة", "متزوج", "متزوجة", "مطلق", "مطلقة"]:
        answers["مدة_الحالة"] = text
        context.user_data["answers"] = answers
        await update.message.reply_text("هل عندك أولاد؟", reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], one_time_keyboard=True, resize_keyboard=True))
        return

    if "عندك_أولاد" not in answers:
        if text in ["نعم", "لا"]:
            answers["عندك_أولاد"] = text
            context.user_data["answers"] = answers
            if text == "نعم":
                await update.message.reply_text("كم عدد الأولاد الذكور؟")
            else:
                answers["عدد_الذكور"] = "0"
                answers["عدد_البنات"] = "0"
                keyboard = [["نعم", "قدمت على وظيفة"], ["لا أعمل", "طالب", "طالبة"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                await update.message.reply_text("هل تعمل؟", reply_markup=reply_markup)
            return

    if "عدد_الذكور" not in answers and answers["عندك_أولاد"] == "نعم":
        answers["عدد_الذكور"] = text
        context.user_data["answers"] = answers
        await update.message.reply_text("كم عدد البنات؟")
        return

    if "عدد_البنات" not in answers and answers["عندك_أولاد"] == "نعم":
        answers["عدد_البنات"] = text
        context.user_data["answers"] = answers
        keyboard = [["نعم", "قدمت على وظيفة"], ["لا أعمل", "طالب", "طالبة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل تعمل؟", reply_markup=reply_markup)
        return

    if "العمل" not in answers:
        answers["العمل"] = text
        context.user_data["answers"] = answers
        keyboard = [["نعم", "لا"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("هل تنتظر شيئًا له علاقة بالرؤيا؟", reply_markup=reply_markup)
        return

    if "ينتظر_شيء" not in answers:
        if text in ["نعم", "لا"]:
            answers["ينتظر_شيء"] = text
            context.user_data["answers"] = answers
            keyboard = [["نعم", "لا"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("هل أنت على رقية أو مصاب بمرض روحي؟", reply_markup=reply_markup)
            return

    if "رقية" not in answers:
        if text in ["نعم", "لا"]:
            answers["رقية"] = text
            context.user_data["answers"] = answers
            await update.message.reply_text("اكتب الرؤيا بالتفصيل ولمعرفة التعبير تابع مجموعة الشات هذا تأويل رؤياي:")
            return

    if "نص_الرؤيا" not in answers:
        answers["نص_الرؤيا"] = text
        context.user_data["answers"] = answers
        await update.message.reply_text("هل توجد معلومات إضافية لها علاقة بالرؤيا؟ (يمكنك كتابة أي شيء):")
        return

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

        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=message)
        await update.message.reply_text("✅ تم استلام الرؤيا وإرسالها للمراجعة، وسيتم الرد قريبًا بإذن الله.")
        context.user_data.clear()
        return

# إعداد التطبيق
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", show_chat_id))
app.add_handler(MessageHandler(filters.Regex("^(سؤال|رؤيا)$"), handle_choice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ruyaa_flow))

print("🤖 البوت يعمل الآن... افتحه في تيليجرام وجرب /start أو /myid داخل الجروب")
app.run_polling()