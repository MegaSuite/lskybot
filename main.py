import os
import requests
import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from io import BytesIO
from PIL import Image

# 配置 logging 模块
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 图床 API 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN provided")
API_ENDPOINT = os.getenv('API_ENDPOINT')
if not API_ENDPOINT:
    raise ValueError("No API_ENDPOINT provided")
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
if not BEARER_TOKEN:
    raise ValueError("No BEARER_TOKEN")

HEADERS = {
    'Authorization': BEARER_TOKEN,
    'Accept': 'application/json'
}

# 定义上传到图床的函数
def upload_to_image_host(image_data, filename):
    # 检查文件类型
    try:
        image = Image.open(image_data)
        image_format = image.format
    except Exception as e:
        logging.error(f"Invalid image file: {e}")
        raise Exception("Invalid image file")

    # 确定文件的 MIME 类型
    if image_format == 'JPEG':
        mime_type = 'image/jpeg'
    elif image_format == 'PNG':
        mime_type = 'image/png'
    else:
        raise Exception(f"Unsupported file type: {image_format}")

    # 重置文件指针
    image_data.seek(0)
    logging.info(f"MIME Type: {mime_type}")
    
    # 加边界头信息
    files = {
        'file': (filename, image_data, mime_type)
    }
    
    try:
        response = requests.post(API_ENDPOINT, headers=HEADERS, files=files)
        response_data = response.json()
        if response.status_code == 200 and response_data.get("status"):
            return response_data["data"]["links"]["url"]
        else:
            logging.error(f"Failed to upload image, Status Code: {response.status_code}, Response: {response.text}")
            raise Exception(f"Failed to upload image: {response_data.get('message')}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

# 异步开始命令的处理函数
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('请发送一张图片，我会将其上传到图床并返回链接。')

# 处理收到的图片 (也需要声明为异步)
async def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = await update.message.photo[-1].get_file()

    photo_bytes = BytesIO(await photo_file.download_as_bytearray())
    
    # 使用文件名
    file_name = photo_file.file_path.split('/')[-1]

    try:
        image_link = upload_to_image_host(photo_bytes, file_name)
        await update.message.reply_text(f"图片已成功上传，链接是：\n`{image_link}`", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"图片上传失败: {e}")
        await update.message.reply_text("图片上传失败，请稍后再试。")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == '__main__':
    main()
