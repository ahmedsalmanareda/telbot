from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import re

TOKEN = "8012418664:AAEIiFc5X6kv404m_8Ksn4n-pOogHYuO6to"
CHANNEL_USERNAME = "eltafauk"
YOUR_CHANNEL_LINK = "https://t.me/eltafauk"  # الرابط الكامل
YOUR_CHANNEL_SHORT_LINK = "t.me/eltafauk"    # الرابط المختصر
YOUR_CHANNEL_MENTION = "@eltafauk"           # المنشن
ADMIN_ID = 1638850584

bot = Bot(token=TOKEN)

def edit_content(text):
    if not text:
        return YOUR_CHANNEL_LINK
    
    # استبدال جميع أشكال الروابط والمنشنات
    replacements = [
        (r'(https?://(t\.me|telegram\.me)/)[\w-]+', fr'\1{CHANNEL_USERNAME}'),  # الروابط الكاملة
        (r'(t\.me/)[\w-]+', fr't.me/{CHANNEL_USERNAME}'),                       # الروابط المختصرة
        (r'@[\w-]+', YOUR_CHANNEL_MENTION)                                      # المنشنات
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    
    # إضافة الرابط إذا لم يوجد
    if not re.search(r'(t\.me|telegram\.me|@)', text):
        text += f"\n\n{YOUR_CHANNEL_LINK}"
    
    return text

def send_admin_notification(original_text, edited_text, message_id):
    try:
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📢 تم تعديل رسالة:\n\n"
                 f"⚪ الأصل: {original_text[:100]}{'...' if len(original_text) > 100 else ''}\n"
                 f"🟢 التعديل: {edited_text[:100]}{'...' if len(edited_text) > 100 else ''}\n"
                 f"🆔 ID الرسالة: {message_id}"
        )
    except Exception as e:
        print(f"فشل إرسال الإشعار: {e}")

def handle_message(update: Update, context: CallbackContext):
    message = update.channel_post or update.edited_channel_post
    if not message:
        return
    
    # معالجة مجموعات الوسائط
    if hasattr(message, 'media_group_id') and message.media_group_id:
        if f"mg_{message.media_group_id}" in context.chat_data:
            return
        context.chat_data[f"mg_{message.media_group_id}"] = True
        
        if message.caption:
            new_caption = edit_content(message.caption)
            try:
                bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=new_caption
                )
                send_admin_notification(message.caption, new_caption, message.message_id)
            except Exception as e:
                print(f"خطأ في تعديل مجموعة الوسائط: {e}")
        return
    
    # معالجة الرسائل النصية
    if message.text:
        new_text = edit_content(message.text)
        if new_text != message.text:
            try:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=new_text
                )
                send_admin_notification(message.text, new_text, message.message_id)
            except Exception as e:
                print(f"خطأ في تعديل النص: {e}")
    
    # معالجة الوسائط المفردة
    elif message.caption:
        new_caption = edit_content(message.caption)
        if new_caption != message.caption:
            try:
                bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=new_caption
                )
                send_admin_notification(message.caption, new_caption, message.message_id)
            except Exception as e:
                print(f"خطأ في تعديل الوصف: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(MessageHandler(
        Filters.chat_type.channel & (
            Filters.text | 
            Filters.photo | 
            Filters.video | 
            Filters.document
        ),
        handle_message
    ))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()