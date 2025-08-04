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

nest_asyncio.apply()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger(__name__).setLevel(logging.INFO)

API_TOKEN = "7624803486:AAEt991OGmkhI3Fdkm632ioACziCz7kMvmI"

words_to_learn = {
    'word': [
        'ability', 'abroad', 'accept', 'access', 'accompany', 'achieve', 'acquire', 'actually', 'adapt', 'addition',
        'address', 'admire', 'admit', 'adult', 'advantage', 'advice', 'affect', 'afford', 'agency', 'agree',
        'ahead', 'aid', 'aim', 'allow', 'alone', 'amaze', 'among', 'amount', 'ancient', 'annoy',
        'answer', 'anxious', 'apart', 'apologize', 'appeal', 'appear', 'apply', 'appreciate', 'approach', 'appropriate',
        'approve', 'argue', 'arise', 'arrange', 'arrival', 'artistic', 'associate', 'assume', 'atmosphere', 'attach',
        'attempt', 'attend', 'attitude', 'attractive', 'audience', 'available', 'avoid', 'award', 'aware', 'back',
        'balance', 'bargain', 'barrier', 'base', 'basically', 'basis', 'bear', 'beat', 'become', 'behavior',
        'believe', 'belong', 'benefit', 'besides', 'better', 'beyond', 'bid', 'bill', 'bitter', 'blame',
        'board', 'body', 'bother', 'branch', 'break', 'breathe', 'bright', 'bring', 'broad', 'budget',
        'burn', 'burst', 'bury', 'busy', 'calculate', 'call', 'campaign', 'can', 'cancer', 'capable'
    ],
    'translation': [
        'توانایی', 'خارج از کشور', 'پذیرفتن', 'دسترسی', 'همراهی کردن', 'دستیابی', 'کسب کردن', 'در واقع', 'تطبیق دادن', 'علاوه بر',
        'آدرس دادن', 'تحسین کردن', 'پذیرفتن', 'بزرگسال', 'مزیت', 'نصیحت', 'تأثیر گذاشتن', 'توانایی مالی', 'نمایندگی', 'موافق بودن',
        'جلوتر', 'کمک', 'هدف', 'اجازه دادن', 'تنها', 'شگفت‌زده کردن', 'در میان', 'مقدار', 'باستانی', 'اذیت کردن',
        'پاسخ', 'نگران', 'جدا', 'عذرخواهی کردن', 'درخواست', 'ظاهر شدن', 'درخواست کردن', 'قدردانی کردن', 'نزدیک شدن', 'مناسب',
        'تأیید کردن', 'بحث کردن', 'پیش آمدن', 'ترتیب دادن', 'ورود', 'هنری', 'همراه', 'فرض کردن', 'جو', 'چسباندن',
        'تلاش', 'حاضر شدن', 'نگرش', 'جذاب', 'مخاطب', 'در دسترس', 'اجتناب کردن', 'جایزه', 'آگاه', 'پشت',
        'تعادل', 'چانه زدن', 'مانع', 'پایه', 'اساساً', 'اساس', 'تحمل کردن', 'شکست دادن', 'شدن', 'رفتار',
        'باور کردن', 'متعلق بودن', 'مزیت', 'علاوه بر این', 'بهتر', 'فراتر', 'پیشنهاد', 'صورتحساب', 'تلخ', 'سرزنش کردن',
        'تخته', 'بدن', 'مزاحم شدن', 'شاخه', 'شکستن', 'نفس کشیدن', 'روشن', 'آوردن', 'گسترده', 'بودجه',
        'سوختن', 'ترکیدن', 'دفن کردن', 'مشغول', 'محاسبه کردن', 'صدا زدن', 'کمپین', 'توانستن', 'سرطان', 'توانا'
    ],
    'pronunciation': [
        'اَبیلیتی', 'اَبراد', 'اَکسِپت', 'اَکسِس', 'اَکومپِنی', 'اَچیو', 'اِکوایِر', 'اَکچوئِلی', 'اَدَپت', 'اَدیشن',
        'اَدرِس', 'اَدمایِر', 'اَدمیت', 'اَدالت', 'اَدوانتِج', 'اَدوایس', 'اِفِکت', 'اَفورد', 'اِیجِنسی', 'اَگری',
        'اَهِد', 'اِید', 'اِیم', 'اَلاو', 'اَلون', 'اِمیز', 'اَمونگ', 'اَمونت', 'اِینشِنت', 'اَنای',
        'اَنسِر', 'اَنکشِس', 'اَپارت', 'اَپالِجایز', 'اَپیل', 'اَپیر', 'اَپلای', 'اَپریشیِیت', 'اَپروچ', 'اَپروپریِیت',
        'اَپروو', 'آرگیو', 'اِرایز', 'اِرِینج', 'اِرایوَل', 'آرتیستیک', 'اَسوشیِیت', 'اَسیوم', 'اَتمِسفیر', 'اَتَچ',
        'اَتِمت', 'اَتِند', 'اَتیتود', 'اَترَکتیو', 'آدیِنس', 'اَوَیلَبِل', 'اَوُید', 'اَوُرد', 'اَوِر', 'بَک',
        'بَلَنس', 'بارگِین', 'بَرِر', 'بِیس', 'بِیسیکَلی', 'بِیسیس', 'بِر', 'بیت', 'بیکام', 'بیهِیویِر',
        'بیلیو', 'بیلُنگ', 'بِنِفیت', 'بِسایدز', 'بِتِر', 'بیاند', 'بید', 'بیل', 'بیتِر', 'بِلِیم',
        'بورد', 'بادی', 'باتِر', 'برَنچ', 'برِیک', 'بریذ', 'برایت', 'برینگ', 'براد', 'بادجِت',
        'بِرن', 'بِرست', 'بِری', 'بیزی', 'کَلکیولِیت', 'کال', 'کَمپِین', 'کَن', 'کَنسِر', 'کِیپَبل'
    ],
    'example': [
        'She has the ability to learn new things quickly.', 'He works abroad for an international company.', 'I accept your apology.', 'Do you have access to the internet?', 'He will accompany her to the party.', 'I want to achieve my goals.', 'You can acquire knowledge through reading.', 'I\'m actually very tired.', 'Birds adapt to their environment.', 'In addition to her salary, she gets a bonus.',
        'He addressed the crowd for an hour.', 'I admire your courage.', 'I admit that I was wrong.', 'Children should be supervised by an adult.', 'It is an advantage to speak a second language.', 'I need your advice.', 'Smoking can affect your health.', 'I can\'t afford a new car.', 'He works for a government agency.', 'I agree with your opinion.',
        'He is ahead of the other students.', 'The first aid kit is in the car.', 'Our aim is to win the game.', 'Please allow me to help you.', 'She lives alone in a big house.', 'The magic show amazed the children.', 'He is among the best students.', 'A large amount of money was spent.', 'The ancient city was discovered by archaeologists.', 'My little brother annoys me.',
        'He gave me the correct answer.', 'She is anxious about her exam.', 'The two houses are far apart.', 'I apologize for being late.', 'He made an appeal for help.', 'She appears to be happy.', 'You can apply for the job online.', 'I appreciate your help.', 'The train is approaching the station.', 'Wear appropriate clothes for the party.',
        'I hope you approve of my decision.', 'My sister and I often argue.', 'A new problem has arisen.', 'I will arrange a meeting for tomorrow.', 'We waited for his arrival.', 'He is very artistic and loves to paint.', 'He is an associate of mine.', 'I assume you are correct.', 'The atmosphere in the room was tense.', 'Please attach your photo to the form.',
        'He made an attempt to solve the problem.', 'I attend school every day.', 'She has a positive attitude towards life.', 'The new building is very attractive.', 'The audience clapped loudly.', 'This book is available in all libraries.', 'I try to avoid fast food.', 'He won an award for his performance.', 'I am aware of the risks.', 'Turn your back to me.',
        'You need to find a balance between work and life.', 'She got a good bargain on the new car.', 'The language barrier makes it difficult to communicate.', 'The statue stands on a stone base.', 'The computer is basically a very fast calculator.', 'The decision was made on the basis of a report.', 'I can\'t bear to see you sad.', 'He can beat anyone at chess.', 'She wants to become a doctor.', 'His behavior was unacceptable.',
        'I believe in your innocence.', 'This book belongs on the top shelf.', 'The new policy will benefit everyone.', 'Besides being a good cook, she is also a talented singer.', 'The weather is better today.', 'The mountain is beautiful beyond words.', 'They will bid on the new contract.', 'Can you pay the bill please?', 'He was bitter about his defeat.', 'He blames me for everything.',
        'Write the answer on the board.', 'He has a strong body.', 'Don\'t bother me now.', 'The tree has many branches.', 'I will break the bad news to her.', 'I need to breathe some fresh air.', 'He has a bright idea.', 'Can you bring me a glass of water?', 'The river is very broad.', 'We need to create a budget for the project.',
        'He burned the old letters.', 'The balloon burst with a loud bang.', 'They will bury the time capsule.', 'I am busy with my homework.', 'Can you calculate the total cost for me?', 'Can you call your mother please?', 'He started a campaign to raise money for charity.', 'I can speak three languages.', 'The doctor diagnosed him with cancer.', 'She is capable of doing the job.'
    ],
    'example_translation': [
        'او توانایی یادگیری سریع چیزهای جدید را دارد.', 'او برای یک شرکت بین‌المللی در خارج از کشور کار می‌کند.', 'عذرخواهی شما را می‌پذیرم.', 'آیا به اینترنت دسترسی دارید؟', 'او او را در مهمانی همراهی خواهد کرد.', 'می‌خواهم به اهدافم دست یابم.', 'شما می‌توانید از طریق مطالعه دانش کسب کنید.', 'در واقع من خیلی خسته‌ام.', 'پرندگان با محیط خود تطبیق پیدا می‌کنند.', 'علاوه بر حقوقش، پاداش هم می‌گیرد.',
        'او یک ساعت برای جمعیت سخنرانی کرد.', 'من شجاعت شما را تحسین می‌کنم.', 'قبول می‌کنم که اشتباه کردم.', 'کودکان باید تحت نظارت بزرگسالان باشند.', 'صحبت کردن به زبان دوم یک مزیت است.', 'من به نصیحت شما نیاز دارم.', 'سیگار کشیدن می‌تواند بر سلامت شما تأثیر بگذارد.', 'من توانایی مالی برای خرید یک ماشین جدید را ندارم.', 'او برای یک نمایندگی دولتی کار می‌کند.', 'من با نظر شما موافق هستم.',
        'او جلوتر از بقیه دانش‌آموزان است.', 'جعبه کمک‌های اولیه در ماشین است.', 'هدف ما پیروزی در بازی است.', 'لطفاً به من اجازه دهید کمکتان کنم.', 'او تنها در یک خانه بزرگ زندگی می‌کند.', 'نمایش جادویی بچه‌ها را شگفت‌زده کرد.', 'او در میان بهترین دانش‌آموزان است.', 'مقدار زیادی پول خرج شد.', 'شهر باستانی توسط باستان‌شناسان کشف شد.', 'برادر کوچکم مرا اذیت می‌کند.',
        'او به من پاسخ صحیح را داد.', 'او نگران امتحانش است.', 'این دو خانه از هم دور هستند.', 'بابت تأخیرم عذرخواهی می‌کنم.', 'او درخواست کمک کرد.', 'به نظر می‌رسد او خوشحال است.', 'شما می‌توانید برای این شغل آنلاین درخواست دهید.', 'از کمک شما قدردانی می‌کنم.', 'قطار به ایستگاه نزدیک می‌شود.', 'لباس مناسب برای مهمانی بپوشید.',
        'امیدوارم تصمیم من را تأیید کنید.', 'من و خواهرم اغلب بحث می‌کنیم.', 'یک مشکل جدید پیش آمده است.', 'من یک جلسه برای فردا ترتیب خواهم داد.', 'ما منتظر ورود او بودیم.', 'او بسیار هنری است و عاشق نقاشی است.', 'او همکار من است.', 'من فرض می‌کنم که شما درست می‌گویید.', 'جو در اتاق پرتنش بود.', 'لطفاً عکس خود را به فرم بچسبانید.',
        'او برای حل مشکل تلاش کرد.', 'من هر روز به مدرسه می‌روم.', 'او نگرش مثبتی نسبت به زندگی دارد.', 'ساختمان جدید بسیار جذاب است.', 'مخاطبان با صدای بلند دست زدند.', 'این کتاب در تمام کتابخانه‌ها موجود است.', 'سعی می‌کنم از فست فود دوری کنم.', 'او برای عملکردش جایزه گرفت.', 'من از خطرات آگاه هستم.', 'پشت به من کن.',
        'باید بین کار و زندگی تعادل پیدا کنید.', 'او برای ماشین جدید تخفیف خوبی گرفت.', 'مانع زبانی برقراری ارتباط را دشوار می‌کند.', 'مجسمه روی یک پایه سنگی ایستاده است.', 'کامپیوتر اساساً یک ماشین حساب بسیار سریع است.', 'تصمیم بر اساس یک گزارش گرفته شد.', 'نمی‌توانم ناراحتی شما را تحمل کنم.', 'او می‌تواند هر کسی را در شطرنج شکست دهد.', 'او می‌خواهد دکتر شود.', 'رفتار او غیرقابل قبول بود.',
        'من به بی‌گناهی شما باور دارم.', 'این کتاب متعلق به قفسه بالا است.', 'سیاست جدید به نفع همه خواهد بود.', 'علاوه بر آشپز خوب بودن، او خواننده با استعدادی نیز هست.', 'آب و هوا امروز بهتر است.', 'کوه فراتر از کلمات زیبا است.', 'آنها برای قرارداد جدید پیشنهاد خواهند داد.', 'لطفاً می‌توانید صورتحساب را پرداخت کنید؟', 'او از شکست خود تلخ بود.', 'او مرا برای همه چیز سرزنش می‌کند.',
        'پاسخ را روی تخته بنویسید.', 'او بدن قوی دارد.', 'حالا مزاحم من نشوید.', 'درخت شاخه‌های زیادی دارد.', 'من خبر بد را به او خواهم داد.', 'من نیاز به تنفس هوای تازه دارم.', 'او یک ایده روشن دارد.', 'می‌توانید یک لیوان آب برای من بیاورید؟', 'رودخانه بسیار گسترده است.', 'ما باید یک بودجه برای پروژه ایجاد کنیم.',
        'او نامه‌های قدیمی را سوزاند.', 'بالن با صدای بلندی ترکید.', 'آنها کپسول زمان را دفن خواهند کرد.', 'من مشغول انجام تکالیفم هستم.', 'می‌توانید کل هزینه را برای من محاسبه کنید؟', 'لطفاً می‌توانید با مادرتان تماس بگیرید؟', 'او یک کمپین برای جمع‌آوری پول برای خیریه راه‌اندازی کرد.', 'من می‌توانم به سه زبان صحبت کنم.', 'دکتر او را به سرطان تشخیص داد.', 'او توانایی انجام این کار را دارد.'
    ],
    'review_interval': [1] * 100,
    'last_reviewed_timestamp': [0.0] * 100
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

def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_*[]()~`>#+=-|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def send_audio_from_text(context: ContextTypes.DEFAULT_TYPE, chat_id, text: str, lang: str):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    await context.bot.send_audio(chat_id=chat_id, audio=audio_bytes)

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

    await send_audio_from_text(context, update.effective_chat.id, word, 'en')
    time.sleep(1)
    await send_audio_from_text(context, update.effective_chat.id, word_to_quiz_data['example'], 'en')
    
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
