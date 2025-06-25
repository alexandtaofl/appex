import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent, InlineQueryResultArticle
from aiogram.types import InputFile
from aiogram.utils import executor

# Bot token from environment variable with fallback to provided token
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8097311993:AAHczkBPuVwpyCLKZHpz9Asbs9h1yS5Sxds')

# ID сотрудников, которые могут пользоваться ботом
ALLOWED_USERS = [1261089607, 7927695798, 6978241760]

# Включаем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Рекламные объявления
ads = {
    'public': {
        'title': 'VoIP + АТС для бизнеса (общее объявление)',
        'text': """**🔥 Надежная VoIP-телефония и АТС для бизнеса!**

📞 Что вы получаете?
• Чистая связь и настраиваемая АТС
• Многоканальные номера, запись звонков
• Анонимность и защита данных
• Подключение за 1 день!

**🏢 Идеально для Киева:**
• Подходит для серых ниш и call-центров
• Техподдержка 24/7

💸 Лучшие цены на рынке! Напишите в бот для деталей.

**👉 Подключить сейчас!**

#VoIP #АТС #Киев""",
        'photo_path': 'photo.jpg',
        'url': 'https://appex-telecom.com/',
        'manager': 't.me/maysonco'
    },
    'private': {
        'title': 'VoIP для друзей (короткое)',
        'text': """**🔥 Качественная VoIP-связь!**

📞 Чистая связь + АТС
💸 Выгодные цены
🚀 Быстрое подключение

Пишите для деталей!""",
        'photo_path': 'photo.jpg',
        'url': 'https://appex-telecom.com/',
        'manager': 't.me/maysonco'
    }
}

# Проверка доступа пользователя
def is_user_allowed(user_id: int) -> bool:
    """Проверяет, имеет ли пользователь доступ к боту"""
    return user_id in ALLOWED_USERS

# Стартовый обработчик
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    if not is_user_allowed(user_id):
        await message.reply("❌ У вас нет доступа к использованию этого бота.")
        logger.warning(f"Unauthorized access attempt from user {user_id}")
        return
    
    welcome_text = """🤖 Добро пожаловать в бот для рекламы VoIP услуг!

📋 Как пользоваться:
1. Используйте инлайн режим: введите @bot_name в любом чате
2. Выберите нужное объявление
3. Отправьте его в чат

🔒 Доступ ограничен авторизованными сотрудниками.

Для получения помощи обратитесь к администратору."""
    
    await message.reply(welcome_text)
    logger.info(f"User {user_id} accessed the bot")

# Инлайн режим обработки с кнопками
@dp.inline_handler()
async def inline_query_handler(inline_query: types.InlineQuery):
    """Обработчик инлайн запросов"""
    user_id = inline_query.from_user.id
    query = inline_query.query.lower()
    
    # Проверяем доступ пользователя
    if not is_user_allowed(user_id):
        await bot.answer_inline_query(
            inline_query.id, 
            results=[], 
            switch_pm_text="❌ Доступ запрещен", 
            switch_pm_parameter="no_access"
        )
        logger.warning(f"Unauthorized inline query from user {user_id}")
        return

    results = []
    
    # Фильтруем объявления по запросу
    for key, ad in ads.items():
        if not query or query in ad['title'].lower() or query in ad['text'].lower():
            # Создаем кнопки для инлайн результата
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton("🌐 Сайт компании", url="https://appex-telecom.com/"),
                InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/maysonco")
            )
            
            input_content = InputTextMessageContent(
                message_text=ad['text'],
                parse_mode='Markdown'
            )
            
            results.append(
                InlineQueryResultArticle(
                    id=key,
                    title=ad['title'],
                    input_message_content=input_content,
                    description='Отправить объявление с кнопками',
                    thumb_url='https://appex-telecom.com/favicon.ico',
                    reply_markup=keyboard
                )
            )

    await bot.answer_inline_query(inline_query.id, results=results, cache_time=1)
    logger.info(f"Served {len(results)} ads to user {user_id} for query: '{query}'")

# Обработчик текстовых сообщений (убрали обработку фото)
@dp.message_handler(content_types=['text'])
async def handle_text_message(message: types.Message):
    """Обработчик текстовых сообщений"""
    user_id = message.from_user.id
    
    if not is_user_allowed(user_id):
        await message.reply("❌ У вас нет доступа к использованию этого бота.")
        logger.warning(f"Unauthorized message from user {user_id}")
        return

    # Обрабатываем рекламные сообщения с кнопками напрямую
    if "🔥" in message.text or "🏢" in message.text:
        # Проверяем, соответствует ли текст одному из наших объявлений
        matching_ad = None
        for key, ad in ads.items():
            if message.text.strip() == ad['text'].strip():
                matching_ad = key
                break
        
        if matching_ad:
            # Создаем кнопки
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton("🌐 Сайт компании", url="https://appex-telecom.com/"),
                InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/maysonco")
            )
            
            # Отправляем сообщение с кнопками и форматированием
            await message.reply(
                text=message.text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # Удаляем исходное сообщение
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"Could not delete original message: {e}")
                
            logger.info(f"Sent ad '{matching_ad}' with buttons to user {user_id}")
        return

# Обработчик помощи
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    """Обработчик команды /help"""
    user_id = message.from_user.id
    
    if not is_user_allowed(user_id):
        await message.reply("❌ У вас нет доступа к использованию этого бота.")
        return
    
    help_text = """📋 Справка по использованию бота:

🔸 /start - Запуск бота
🔸 /help - Показать эту справку
🔸 /ads - Показать доступные объявления

📱 Инлайн режим:
• Введите @bot_name в любом чате
• Выберите нужное объявление
• Отправьте его

🔒 Доступ ограничен авторизованными сотрудниками.

Для технической поддержки обратитесь к администратору."""
    
    await message.reply(help_text)

# Показать доступные объявления
@dp.message_handler(commands=['ads'])
async def ads_handler(message: types.Message):
    """Показать список доступных объявлений"""
    user_id = message.from_user.id
    
    if not is_user_allowed(user_id):
        await message.reply("❌ У вас нет доступа к использованию этого бота.")
        return
    
    ads_text = "📢 Доступные рекламные объявления:\n\n"
    for key, ad in ads.items():
        ads_text += f"🔹 {ad['title']}\n"
    
    ads_text += "\n💡 Используйте инлайн режим для отправки объявлений в чаты."
    
    await message.reply(ads_text)

# Обработчик ошибок
@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    """Глобальный обработчик ошибок"""
    logger.error(f"Update {update} caused error {exception}")
    return True

# Функция запуска бота
async def on_startup(dp):
    """Функция, выполняемая при запуске бота"""
    logger.info("Bot started successfully!")
    
    # Проверяем корректность токена
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot info: @{bot_info.username} ({bot_info.first_name})")
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")

async def on_shutdown(dp):
    """Функция, выполняемая при остановке бота"""
    logger.info("Bot shutting down...")
    await bot.close()

if __name__ == '__main__':
    # Запускаем бота
    try:
        executor.start_polling(
            dp, 
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
