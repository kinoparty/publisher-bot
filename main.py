import os
import telebot
from flask import Flask, request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8590903863:AAElvfoY4TyDoWoqXYNncLhIY2VLB0YGuvs")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

CHANNEL_ID = "@TIR_PegasAT"
ADMINS = [551563550]
WATERMARK_TEXT = "MOST AUTO"

FOOTER_TEXT = """<a href="https://pegasat.com.ua"><b>🔗 Більше оригінальних запчастин</b></a>

<b>📞 Потрібна допомога з підбором?</b>
Наші фахівці швидко підберуть необхідну деталь саме для вашого автомобіля.

🔴 0953450040   🔵 0973450040

<b>PEGAS АВТОТРЕЙД</b>
✅ Оригінальні запчастини IVECO
💳 Безготівковий розрахунок
📦 Самовивіз або доставка Новою Поштою"""

def process_image(photo_bytes):
    img = Image.open(photo_bytes)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    draw.text((20, 20), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 200))
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
        
        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton(text="Дізнатися ціну / Наявність", url="https://t.me/TIR_PegasAT")
        btn2 = telebot.types.InlineKeyboardButton(text="Відправити другу ↗️", url="https://t.me/share/url?url=https://t.me/TIR_PegasAT")
        markup.add(btn1)
        markup.add(btn2)
        
        full_post_text = f"{caption}\n\n{FOOTER_TEXT}"
        
        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=processed_image,
            caption=full_post_text,
            parse_mode='HTML',
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
