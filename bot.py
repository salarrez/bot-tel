# وارد کردن کتابخانه‌های مورد نیاز
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import pandas as pd
import numpy as np
import random
import nest_asyncio
import time
import re
from gtts import gTTS
import io

# اعمال nest_asyncio برای اجرای صحیح در Colab
nest_asyncio.apply()

# تنظیمات لاگ‌گیری
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger(__name__).setLevel(logging.INFO)

API_TOKEN = "7624803486:AAEt991OGmkhI3Fdkm632ioACziCz7kMvmI"

# لیست کلمات
words_to_learn = {
    'word': ['prevalent', 'profound', 'ubiquitous', 'resilient', 'ephemeral', 'mitigate'],
    'translation': ['رایج', 'عمیق', 'فراگیر', 'انعطاف‌پذیر', 'زودگذر', 'کاهش دادن'],
    'pronunciation': ['پِرِوِلِنت', 'پروفاوُند', 'یوبیکویتوس', 'ریزیلیِنت', 'اِفِمِرال', 'میتِگِیت'],
    'example': [
        'His ideas are prevalent among young people.',
        'The crisis had a profound effect on the economy.',
        'Smartphones are ubiquitous today.',
        'He is a resilient person who can bounce back from setbacks.',
        'Fashions are often ephemeral.',
        'We need to mitigate the risks.'
    ],
    'example_translation': [
        'ایده‌های او در بین جوانان رایج است.',
        'بحران تأثیر عمیقی بر اقتصاد داشت.',
        'امروزه تلفن‌های هوشمند فراگیر هستند.',
        'او فردی انعطاف‌پذیر است که می‌تواند از شکست‌ها برگردد.',
        'مدها اغلب زودگذر هستند.',
        'ما باید ریسک‌ها را کاهش دهیم.'
    ],
    'review_interval': [1, 1, 1, 1, 1, 1],
    'last_reviewed_timestamp': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
}
words_df = pd.DataFrame(words_to_learn)

def generate_quiz_question(word_to_quiz):
    options_df = words_df[words_df['word'] == word_to_quiz]
    if options_df.empty:
        return None, None
    correct_translation = options_df['translation'].iloc[0]
    all_translations = words_df['translation'].tolist()
    all_translations.remove(correct_translation)
    random.shuffle(all_translations)
    options = [correct_translation] + all_translations[:3]
    random.shuffle(options)
    return options, correct_translation

# تابع کمکی برای فرار (escape) از کاراکترهای خاص MarkdownV2
def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_*[]()~`>#+=-|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# توابع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'words_data' not in context.user_data:
        context.user_data['words_data'] = words_df.copy()
    await update.message.reply_text('سلام! به ربات هوشمند یادگیری زبان خوش آمدید. با فرمان /quiz شروع کنید.')

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'words_data' not in context.user_data:
        await update.message.reply_text('لطفاً ابتدا با فرمان /start ربات را راه‌اندازی کنید.')
        return
    user_words_df = context.user_data['words_data']
    current_time = time.time()
    user_words_df['next_review_time'] = user_words_df['last_reviewed_timestamp'] + user_words_df['review_interval'] * 86400
    words_to_review = user_words_df[user_words_df['next_review_time'] <= current_time]
    
    if words_to_review.empty:
        await update.message.reply_text('کلمه جدیدی برای مرور وجود ندارد. لطفاً بعداً دوباره امتحان کنید.')
        return
        
    word_to_quiz_data = words_to_review.sample(1).iloc[0]
    word = word_to_quiz_data['word']
    
    options, correct_answer = generate_quiz_question(word)
    
    context.user_data['correct_answer'] = correct_answer
    context.user_data['word_to_quiz'] = word
    context.user_data['word_data'] = word_to_quiz_data.to_dict()
    
    question_text = (
        f"**کلمه:** {escape_markdown_v2(word)}\n"
        f"**تلفظ:** {escape_markdown_v2(word_to_quiz_data['pronunciation'])}\n"
        f"**معنی:** ||{escape_markdown_v2(word_to_quiz_data['translation'])}|| \n\n"
        f"**مثال:** {escape_markdown_v2(word_to_quiz_data['example'])}\n"
        f"**معنی مثال:** ||{escape_markdown_v2(word_to_quiz_data['example_translation'])}|| \n\n"
        f"**بلدی این کلمه رو؟**"
    )

    keyboard = [
        [InlineKeyboardButton("✅ بله، می‌دانم", callback_data=f"known_{word}")],
        [InlineKeyboardButton("❌ خیر، نمی‌دانم", callback_data=f"unknown_{word}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(question_text, reply_markup=reply_markup, parse_mode='MarkdownV2')

async def handle_knowledge_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'words_data' not in context.user_data:
        await update.callback_query.message.reply_text('لطفاً ابتدا با فرمان /start ربات را راه‌اندازی کنید.')
        return
    
    query = update.callback_query
    await query.answer()
    
    action, word = query.data.split('_', 1)

    if action == "known":
        await query.edit_message_text(text=f'✅ کلمه "{word}" به لیست دانسته‌های شما اضافه شد.')
        user_words_df = context.user_data['words_data']
        user_words_df.loc[user_words_df['word'] == word, 'review_interval'] *= 2
        user_words_df.loc[user_words_df['word'] == word, 'last_reviewed_timestamp'] = time.time()
        context.user_data['words_data'] = user_words_df
    elif action == "unknown":
        await query.edit_message_text(text=f'❌ کلمه "{word}" به لیست ندانسته‌های شما اضافه شد.')
        user_words_df = context.user_data['words_data']
        user_words_df.loc[user_words_df['word'] == word, 'review_interval'] = 1
        user_words_df.loc[user_words_df['word'] == word, 'last_reviewed_timestamp'] = time.time()
        context.user_data['words_data'] = user_words_df

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(handle_knowledge_check, pattern="^(known|unknown)_.*"))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
