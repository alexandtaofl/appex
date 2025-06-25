import logging as _l
import os as _o
import base64 as _b
from aiogram import Bot as _B, Dispatcher as _D, types as _t
from aiogram.types import InlineKeyboardMarkup as _IKM, InlineKeyboardButton as _IKB, InlineQueryResultArticle as _IQRA, InputTextMessageContent as _ITMC
from aiogram.utils import executor as _e

# Обфусцированные данные
_x1 = _b.b64decode(b'ODA5NzMxMTk5MzpBQUhjemtCUHVWd3B5Q0xLWkhwejlBc2JzOWgxeVM1U3hkcw==').decode()
_x2 = [int('0x4b2e5437', 16), int('0x1dbb7e36', 16), int('0x1a0f9e08', 16)]

_l.basicConfig(level=_l.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_lg = _l.getLogger(__name__)

_bot = _B(token=_o.getenv('TELEGRAM_BOT_TOKEN', _x1))
_dp = _D(_bot)

def _check(uid: int) -> bool:
    return uid in _x2

_ads = {
    'pub': {
        't': '🔥 **VoIP-телефония для бизнеса**',
        'c': '🏢 **Корпоративная IP-АТС** — экономия до 70% на связи!\n\n📞 Виртуальные номера, многоканальность, CRM-интеграция\n💸 Лучшие цены на рынке! Напишите в бот для деталей.\n\n👉 **Получить консультацию менеджера**'
    },
    'prv': {
        't': '📞 VoIP-телефония',
        'c': '🔥 **Дешевая связь для бизнеса**\n\n📱 IP-телефония, виртуальные номера\n💰 Лучшие цены на рынке\n\n👉 **Связаться с менеджером**'
    }
}

@_dp.message_handler(commands=['start'])
async def _h1(msg: _t.Message):
    if not _check(msg.from_user.id):
        await msg.reply("❌ У вас нет доступа к этому боту.")
        _lg.warning(f"Unauthorized access attempt from user {msg.from_user.id}")
        return
    
    _lg.info(f"User {msg.from_user.id} accessed the bot")
    await msg.reply(
        "👋 Добро пожаловать в бот для рекламы VoIP услуг!\n\n"
        "🔸 Используйте инлайн режим: напишите @appexadsbot в любом чате\n"
        "🔸 Выберите тип объявления\n"
        "🔸 Отправьте готовую рекламу с кнопками\n\n"
        "/help - справка\n"
        "/ads - посмотреть объявления"
    )

@_dp.inline_handler()
async def _h2(iq: _t.InlineQuery):
    if not _check(iq.from_user.id):
        _lg.warning(f"Unauthorized inline query from user {iq.from_user.id}")
        return
    
    _res = []
    
    for k, v in _ads.items():
        _kb = _IKM(row_width=1)
        _kb.add(
            _IKB("🌐 Наш сайт", url="https://appex-telecom.com/"),
            _IKB("💬 Менеджер", url="https://t.me/maysonco")
        )
        
        _res.append(
            _IQRA(
                id=k,
                title=v['t'],
                input_message_content=_ITMC(
                    message_text=v['c'],
                    parse_mode='Markdown'
                ),
                reply_markup=_kb,
                description=f"Отправить {k} объявление"
            )
        )
    
    await _bot.answer_inline_query(iq.id, _res, cache_time=1)
    _lg.info(f"Served {len(_res)} ads to user {iq.from_user.id} for query: '{iq.query}'")

@_dp.message_handler(content_types=['text'])
async def _h3(msg: _t.Message):
    if not _check(msg.from_user.id):
        await msg.reply("❌ У вас нет доступа к этому боту.")
        _lg.warning(f"Unauthorized access attempt from user {msg.from_user.id}")
        return
    
    await msg.reply("Используйте инлайн режим: напишите @appexadsbot в любом чате для отправки рекламы!")

@_dp.message_handler(commands=['help'])
async def _h4(msg: _t.Message):
    if not _check(msg.from_user.id):
        await msg.reply("❌ У вас нет доступа к этому боту.")
        return
    
    await msg.reply(
        "📖 **Справка по использованию бота:**\n\n"
        "1️⃣ Откройте любой чат в Telegram\n"
        "2️⃣ Напишите @appexadsbot и пробел\n"
        "3️⃣ Выберите тип объявления из списка\n"
        "4️⃣ Нажмите на нужное объявление\n"
        "5️⃣ Отправьте готовую рекламу с кнопками!\n\n"
        "✅ Объявления содержат кнопки для перехода на сайт и к менеджеру"
    )

@_dp.message_handler(commands=['ads'])
async def _h5(msg: _t.Message):
    if not _check(msg.from_user.id):
        await msg.reply("❌ У вас нет доступа к этому боту.")
        return
    
    _txt = "📋 **Доступные объявления:**\n\n"
    for k, v in _ads.items():
        _txt += f"**{k.upper()}:**\n{v['c']}\n\n"
    
    await msg.reply(_txt, parse_mode='Markdown')

@_dp.errors_handler()
async def _h6(upd: _t.Update, exc: Exception):
    _lg.error(f"Error occurred: {exc}")
    return True

async def _start(dp):
    _bi = await _bot.get_me()
    _lg.info("Bot started successfully!")
    _lg.info(f"Bot info: @{_bi.username} ({_bi.first_name})")

async def _stop(dp):
    _lg.info("Bot stopped")

if __name__ == '__main__':
    _e.start_polling(_dp, skip_updates=True, on_startup=_start, on_shutdown=_stop)
