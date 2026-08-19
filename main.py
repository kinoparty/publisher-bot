import os
import telebot
from flask import Flask, request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# 1. Инициализация переменных окружения и бота (ДО обработчиков)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "твой_токен_если_нет_в_переменных")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# 2. Настройки
CHANNEL_ID = "@твой_канал" 
ADMINS = [123456789, 987654321] # Замени на свои ID
WATERMARK_TEXT = "MOST AUTO"

# 3. Функция обработки фото
def process_image(photo_bytes):
    img = Image.open(photo_bytes)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    
    # Наложение водяного знака
    draw.text((20, 20), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 200))
    
    output_bytes = BytesIO()
    img.save(output_bytes, format='JPEG')
    output_bytes.seek(0)
    return output_bytes

# 4. Обработчик сообщений с фото
@bot.message_handler(content_types=['photo'])
def handle_photo_post(message):
    if message.from_user.id not in ADMINS:
        return

    caption = message.caption
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
        
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Узнать цену / Наличие", url="https://t.me/твой_контакт")
        markup.add(btn)
        
        bot.send_photo(chat_id=CHANNEL_ID, photo=processed_image, caption=caption, reply_markup=markup)
        bot.reply_to(message, "Опубликовано.")
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

# 5. Маршруты Flask для работы вебхука в Cloud Run
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # Этот эндпоинт можно дернуть в браузере для автоматической установки вебхука
    # подставив свой URL вместо "твой-url-из-cloud-run"
    bot.set_webhook(url='https://твой-url-из-cloud-run.a.run.app/' + TELEGRAM_TOKEN)
    return "Webhook set!", 200

# 6. Запуск сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
