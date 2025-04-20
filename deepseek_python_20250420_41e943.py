from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator
import subprocess
import os

# تنظیمات ربات
TOKEN = "توکن_ربات_خود_را_اینجا_قرار_دهید"
translator = Translator()

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("ترجمه متن", callback_data='translate')],
        [InlineKeyboardButton("ساخت آهنگ", callback_data='make_music')]
    ]
    update.message.reply_text('لطفا گزینه مورد نظر را انتخاب کنید:', 
                            reply_markup=InlineKeyboardMarkup(keyboard))

def handle_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    if query.data == 'translate':
        context.user_data['mode'] = 'translate'
        query.edit_message_text('حالت ترجمه فعال شد. متن انگلیسی خود را ارسال کنید.')
    else:
        context.user_data['mode'] = 'make_music'
        query.edit_message_text('حالت ساخت آهنگ فعال شد. متن خود را ارسال کنید.')

def process_message(update: Update, context: CallbackContext) -> None:
    user_mode = context.user_data.get('mode')
    text = update.message.text
    
    if user_mode == 'translate':
        try:
            translated = translator.translate(text, dest='fa').text
            update.message.reply_text(f"ترجمه:\n{translated}")
        except Exception as e:
            update.message.reply_text(f"خطا در ترجمه: {e}")
            
    elif user_mode == 'make_music':
        update.message.reply_text("در حال ساخت آهنگ... لطفاً صبر کنید")
        try:
            # ساخت آهنگ با Riffusion
            output_file = "output.mp3"
            cmd = [
                "riffusion-cli",
                "-p", f"happy {text[:100]}",  # محدودیت طول متن
                "-o", output_file
            ]
            subprocess.run(cmd, check=True, timeout=300)
            
            with open(output_file, "rb") as audio_file:
                update.message.reply_audio(audio=audio_file, 
                                         title="آهنگ ساخته شده")
            
            os.remove(output_file)
        except Exception as e:
            update.message.reply_text(f"خطا در ساخت آهنگ: {e}")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(handle_selection))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()