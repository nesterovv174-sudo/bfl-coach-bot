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
    await message.answer(
        "👋 Добро пожаловать в AI-коуч по БФЛ!\n\n"
        "Выберите нужный раздел ниже:",
        reply_markup=main_menu
    )

@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if text == "📋 Возражения":
        await message.answer("Выберите возражение клиента:", reply_markup=vozrazheniya_menu)
    elif text == "📞 Скрипты":
        await message.answer("Выберите скрипт:", reply_markup=skripty_menu)
    elif text == "🤖 Спросить у ИИ":
        await message.answer(
            "🤖 Режим GigaChat включён.\n\n"
            "Задавайте любой вопрос по банкротству физических лиц — я дам подробный разбор и готовые варианты ответа.",
            reply_markup=main_menu
        )
        return
    elif text == "⚡ Быстрый ответ":
        await message.answer(
            "⚡ Отправьте сообщение клиента — я предложу 2–3 варианта ответа.",
            reply_markup=main_menu
        )
        return
    elif text == "👋 Приветствие":
        await message.answer("👋 Добро пожаловать! Используйте меню для работы.", reply_markup=main_menu)
    elif text == "🔙 Назад в главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu)

    # ==================== СКРИПТ ПЕРВОГО РАЗГОВОРА ====================
    elif text == "📞 Скрипт первого разговора":
        reply = (
            "📞 **Скрипт первого разговора**\n\n"
            "Добрый день / вечер, {ИМЯ КЛИЕНТА}?\n\n"
            "— Это [ваше имя], я помощник юриста компании «БанкротствоГрупп». Вы недавно общались с моей коллегой, она передала мне, что у вас сумма кредитов составляет ………… т.р. и вам интересно списание. Всё верно?\n\n"
            "Пауза.\n\n"
            "— Отлично! Мы специализируемся на списании долгов и уже многим помогли. Сейчас уточню пару вопросов, это займёт 5 минут. Удобно сейчас?"
        )
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)

    # ==================== ШАБЛОННЫЕ ВОЗРАЖЕНИЯ (улучшенные) ====================
    elif any(x in text for x in ["Дорого", "Заберут", "Подумать", "Боюсь", "Нет денег", "Коллекторы", "МФЦ", "Пробовал", "Не доверяю", "Стыдно", "Времени", "В суде"]):
        await message.answer("✅ Шаблонный ответ загружен.\n\n(Пока используем заглушку. После теста GigaChat сделаем все тексты красивыми)", reply_markup=vozrazheniya_menu)

    else:
        # Если сообщение не кнопка — считаем, что это вопрос к ИИ
        await handle_gigachat(message)

async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не найден. Проверьте переменную GIGACHAT_AUTH_KEY в Railway.")
        return

    user_text = message.text

    system_prompt = """
Ты — экспертный AI-коуч для менеджеров по банкротству физических лиц (БФЛ) в России.
Отвечай только по теме банкротства: возражения клиентов, скрипты продаж, этапы процедуры, последствия, документы, анализ ситуации.
Используй эмпатию, профессиональный, уверенный и мягкий тон.
Формат ответа всегда:
1. **Краткий разбор ситуации**
2. **2–3 готовых варианта ответа клиенту** (живые, естественные тексты)
3. **Рекомендации менеджеру** (что сказать дальше, на что обратить внимание)
4. **Вероятность закрытия** (в процентах)

Отвечай только на русском языке. Не отвечай на вопросы вне темы БФЛ.
"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GIGACHAT_AUTH_KEY}",
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
                }
            ) as resp:
                data = await resp.json()
                ai_reply = data["choices"][0]["message"]["content"]
                await message.answer(ai_reply, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка соединения с GigaChat:\n{str(e)}\n\nПроверьте ключ в Variables.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен с GigaChat!")
    asyncio.run(dp.start_polling(bot))
