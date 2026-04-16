import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = os.getenv("API_TOKEN")
GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Возражения"), KeyboardButton(text="📞 Скрипты")],
        [KeyboardButton(text="🤖 Спросить у ИИ"), KeyboardButton(text="⚡ Быстрый ответ")],
        [KeyboardButton(text="👋 Приветствие")],
    ],
    resize_keyboard=True
)

vozrazheniya_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Дорого / Цена"), KeyboardButton(text="🏠 Заберут квартиру")],
        [KeyboardButton(text="🤔 Нужно подумать"), KeyboardButton(text="😟 Боюсь последствий")],
        [KeyboardButton(text="💸 Нет денег"), KeyboardButton(text="📞 Коллекторы звонят")],
        [KeyboardButton(text="🆓 Сам через МФЦ"), KeyboardButton(text="🔄 Уже пробовал")],
        [KeyboardButton(text="🚫 Не доверяю"), KeyboardButton(text="🙈 Стыдно / что скажут")],
        [KeyboardButton(text="⏰ Времени нет"), KeyboardButton(text="⚖️ Уже в суде")],
        [KeyboardButton(text="🔙 Назад в главное меню")],
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Добро пожаловать в AI-коуч по БФЛ!\n\nВыберите раздел:", reply_markup=main_menu)

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()

    if text == "📋 Возражения":
        await message.answer("Выберите возражение клиента:", reply_markup=vozrazheniya_menu)
    elif text == "🤖 Спросить у ИИ":
        await message.answer("🤖 Режим GigaChat включён.\n\nЗадавайте любой вопрос по банкротству.", reply_markup=main_menu)
        return
    elif text == "⚡ Быстрый ответ":
        await message.answer("⚡ Отправьте сообщение клиента.", reply_markup=main_menu)
        return
    else:
        await handle_gigachat(message)

async def get_access_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": "b0b0b0b0-b0b0-b0b0-b0b0-b0b0b0b0b0b0"  # можно любой UUID
            },
            data="scope=GIGACHAT_API_PERS",
            ssl=False
        ) as resp:
            data = await resp.json()
            return data.get("access_token")

async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ не настроен.")
        return

    try:
        access_token = await get_access_token()
        if not access_token:
            await message.answer("❌ Не удалось получить access token.")
            return

        user_text = message.text

        system_prompt = """
Ты — экспертный коуч только по банкротству физических лиц в России.
Отвечай по теме БФЛ: возражения, скрипты, этапы, последствия.
Формат:
1. Краткий разбор
2. 2–3 варианта ответа клиенту
3. Рекомендации менеджеру
Отвечай только на русском.
"""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "GigaChat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1200
                },
                ssl=False
            ) as resp:
                data = await resp.json()
                ai_reply = data["choices"][0]["message"]["content"]
                await message.answer(ai_reply, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка:\n{str(e)[:400]}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен с GigaChat (через Access Token)")
    asyncio.run(dp.start_polling(bot))
