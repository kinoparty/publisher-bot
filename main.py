from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Замени на реальные данные
CHANNEL_ID = "@твой_канал" 
ADMINS = [123456789, 987654321] # Твой ID и ID сотрудницы

def process_image(photo_bytes):
    # Открываем изображение из памяти
    img = Image.open(photo_bytes)
    draw = ImageDraw.Draw(img)
    
    # Настройка шрифта (убедись, что файл font.ttf лежит в репозитории)
    try:
        font = ImageFont.truetype("arial.ttf", 40) # 40 - размер шрифта
    except IOError:
        font = ImageFont.load_default()
    
    # Текст водяного знака / надписи
    watermark_text = "MOST AUTO" 
    
    # Наложение текста. Координаты x=20, y=20 (левый верхний угол)
    # fill = цвет RGBA (белый с прозрачностью)
    draw.text((20, 20), watermark_text, font=font, fill=(255, 255, 255, 200))
    
    # Сохраняем результат в виртуальный буфер
    output_bytes = BytesIO()
    img.save(output_bytes, format='JPEG')
    output_bytes.seek(0)
    
    return output_bytes

@bot.message_handler(content_types=['photo'])
def handle_photo_post(message):
    # Проверка прав доступа
    if message.from_user.id not in ADMINS:
        return

    caption = message.caption
    if not caption:
        bot.reply_to(message, "Ошибка: пустой контент. Отправь фото с описанием.")
        return

    try:
        bot.reply_to(message, "Принято в обработку...")
        
        # Скачиваем фото в максимальном разрешении
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Пропускаем через функцию обработки
        img_io = BytesIO(downloaded_file)
        processed_image = process_image(img_io)
        
        # Кнопка
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Узнать цену / Наличие", url="https://t.me/твой_контакт")
        markup.add(btn)
        
        # Отправка в канал
        bot.send_photo(chat_id=CHANNEL_ID, photo=processed_image, caption=caption, reply_markup=markup)
        bot.reply_to(message, "Опубликовано.")
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")
