import os
import telebot
import urllib.parse
from flask import Flask, request
from io import BytesIO
from PIL import Image

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8590903863:AAElvfoY4TyDoWoqXYNncLhIY2VLB0YGuvs")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

CHANNEL_ID = "@TIR_PegasAT"
ADMINS = [551563550]

FOOTER_TEXT = """<a href="https://pegasat.com.ua"><b>🔗 Більше оригінальних запчастин</b></a>

<b>📞 Зателефонуйте нам!</b>
Наші фахівці швидко підберуть необхідну деталь саме для вашого автомобіля.

🔵 0973450040   🔴 0953450040

<b>PEGAS АВТОТРЕЙД</b>
✅ Оригінальні запчастини IVECO
💳 Безготівковий розрахунок
📦 Самовивіз або доставка Новою Поштою"""

def process_image(photo_bytes):
    img = Image.open(photo_bytes)
    output_bytes = BytesIO()
    img.save(output_bytes, format='JPEG')
    output_bytes.seek(0)
    return output_bytes

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_photo_post(message):
    if message.from_user.id not in ADMINS:
        return
        
    if message.content_type != 'photo':
        bot.reply_to(message, f"Ошибка: Ты прислал {message.content_type}, а нужно сжатое ФОТО.")
        return
        
    caption = message.html_caption
    if not caption:
        bot.reply_to(message, "Ошибка: пустой контент. Отправь фото с описанием.")
        return
        
    try:
        bot.reply_to(message, "Принято в обработку...")
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        img_io = BytesIO(downloaded_file)
        processed_image = process_image(img_io)
        
        full_post_text = f"{caption}\n\n{FOOTER_TEXT}"
        
        # 1. Отправляем пост без кнопок, чтобы получить его ID в канале
        sent_message = bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=processed_image,
            caption=full_post_text,
            parse_mode='HTML'
        )
        
        # 2. Формируем прямую ссылку на опубликованный пост
        channel_name = CHANNEL_ID.replace('@', '')
        post_url = f"https://t.me/{channel_name}/{sent_message.message_id}"
        
        # 3. Кодируем заготовку текста для менеджера с вшитой ссылкой
        prefilled_text = f"Доброго дня! Цікавить ціна та наявність запчастини з цього поста:\n{post_url}"
        encoded_text = urllib.parse.quote(prefilled_text)
        manager_link = f"https://t.me/+380973450040?text={encoded_text}"
        
        # 4. Создаем кнопку с умной ссылкой и прикручиваем к посту
        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton(text="Дізнатися ціну / Наявність", url=manager_link)
        markup.add(btn1)
        
        bot.edit_message_reply_markup(
            chat_id=CHANNEL_ID, 
            message_id=sent_message.message_id, 
            reply_markup=markup
        )
        
        bot.reply_to(message, "Опубликовано.")
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://publisher-bot-992802077002.europe-west1.run.app/' + TELEGRAM_TOKEN)
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
