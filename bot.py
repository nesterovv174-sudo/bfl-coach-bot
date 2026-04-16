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

# ==================== МЕНЮ ====================
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

skripty_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Скрипт первого разговора")],
        [KeyboardButton(text="🔙 Назад в главное меню")],
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Добро пожаловать в AI-коуч по БФЛ!\n\nВыберите нужный раздел:", reply_markup=main_menu)

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()

    # Главное меню
    if text == "📋 Возражения":
        await message.answer("Выберите возражение клиента:", reply_markup=vozrazheniya_menu)

    elif text == "📞 Скрипты":
        await message.answer("Выберите скрипт:", reply_markup=skripty_menu)

    elif text == "🤖 Спросить у ИИ":
        await message.answer(
            "🤖 Режим умного ИИ (GigaChat) включён.\n\n"
            "Задавайте любой вопрос по банкротству физических лиц — я дам подробный разбор и варианты ответа.",
            reply_markup=main_menu
        )
        return   # ← Важно! Выходим, чтобы не уходило в GigaChat дальше

    elif text == "⚡ Быстрый ответ":
        await message.answer("⚡ Отправьте сообщение клиента — я предложу варианты ответа.", reply_markup=main_menu)
        return

    elif text == "👋 Приветствие":
        await message.answer("👋 Добро пожаловать! Используйте меню ниже.", reply_markup=main_menu)

    elif text == "🔙 Назад в главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu)

    # ==================== ШАБЛОННЫЕ ВОЗРАЖЕНИЯ ====================
    elif text in ["💰 Дорого / Цена", "🏠 Заберут квартиру", "🤔 Нужно подумать", "😟 Боюсь последствий",
                  "💸 Нет денег", "📞 Коллекторы звонят", "🆓 Сам через МФЦ", "🔄 Уже пробовал",
                  "🚫 Не доверяю", "🙈 Стыдно / что скажут", "⏰ Времени нет", "⚖️ Уже в суде"]:
        await handle_template_objection(message, text)

    # ==================== СКРИПТЫ ====================
    elif text == "📞 Скрипт первого разговора":
        reply = "📞 **Скрипт первого разговора**\n\n(вставьте сюда ваш полный текст скрипта)"
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)

    else:
        # Всё остальное (обычный текст) отправляем в GigaChat
        await handle_gigachat(message)

# ==================== ШАБЛОННЫЕ ОТВЕТЫ ====================
async def handle_template_objection(message: types.Message, objection: str):
    templates = {
        "💰 Дорого / Цена": (
            "💰 **Дорого / Цена**\n\n"
            "**Вариант 1:**\n«Понимаю вас очень хорошо. Сейчас действительно каждая копейка на счету. При этом каждый месяц долг продолжает расти из-за процентов. Давайте вместе посчитаем, как будет выглядеть рассрочка на нашу работу.»\n\n"
            "**Вариант 2:**\n«Согласен, сумма выглядит большой. Но если ничего не делать, через год вы переплатите ещё больше.»"
        ),
        "🏠 Заберут квартиру": (
            "🏠 **Заберут квартиру**\n\n"
            "**Вариант 1:**\n«Это один из самых частых страхов. Единственное жильё, в котором вы проживаете, по закону защищено и не может быть реализовано.»"
        ),
        # Добавь остальные по желанию
    }

    reply = templates.get(objection, "✅ Ответ на возражение загружен.")
    await message.answer(reply, parse_mode="Markdown", reply_markup=vozrazheniya_menu)

# ==================== GIGACHAT ====================
async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не настроен.")
        return

    user_text = message.text

    system_prompt = """
Ты — экспертный коуч только по банкротству физических лиц в России (ФЗ-127).
Отвечай исключительно по теме БФЛ.
Используй эмпатию, профессиональный и мягкий тон.
Формат ответа:
1. **Краткий разбор**
2. **2–3 готовых варианта ответа клиенту**
3. **Рекомендации менеджеру**
4. **Вероятность закрытия** (в %)

Отвечай только на русском.
"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={
                    "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": "b0b0b0b0-b0b0-b0b0-b0b0-b0b0b0b0b0b0"
                },
                data="scope=GIGACHAT_API_PERS",
                ssl=False
            ) as resp:
                token_data = await resp.json()
                access_token = token_data.get("access_token")

            if not access_token:
                await message.answer("❌ Не удалось получить токен.")
                return

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
                    "max_tokens": 1500
                },
                ssl=False
            ) as resp:
                data = await resp.json()
                ai_reply = data["choices"][0]["message"]["content"]
                await message.answer(ai_reply, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка GigaChat:\n{str(e)[:500]}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен: шаблонные возражения + GigaChat")
    asyncio.run(dp.start_polling(bot))
