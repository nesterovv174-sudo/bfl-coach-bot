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

# ==================== ГЛАВНОЕ МЕНЮ ====================
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Возражения"), KeyboardButton(text="📞 Скрипты")],
        [KeyboardButton(text="🤖 Спросить у ИИ")],
        [KeyboardButton(text="👋 Приветствие")],
    ],
    resize_keyboard=True
)

# ==================== МЕНЮ ВОЗРАЖЕНИЙ ====================
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

# ==================== МЕНЮ СКРИПТОВ ====================
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

    if text == "📋 Возражения":
        await message.answer("Выберите возражение клиента:", reply_markup=vozrazheniya_menu)

    elif text == "📞 Скрипты":
        await message.answer("Выберите скрипт:", reply_markup=skripty_menu)

    elif text == "🤖 Спросить у ИИ":
        await message.answer(
            "🤖 Режим умного ИИ включён.\n\n"
            "Задавайте любой вопрос по ситуации клиента — я дам максимально подробный разбор и рекомендации.",
            reply_markup=main_menu
        )
        return

    elif text == "👋 Приветствие":
        await message.answer("👋 Добро пожаловать! Используйте меню ниже.", reply_markup=main_menu)

    elif text == "🔙 Назад в главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu)

    # Шаблонные возражения
    elif text in ["💰 Дорого / Цена", "🏠 Заберут квартиру", "🤔 Нужно подумать", "😟 Боюсь последствий",
                  "💸 Нет денег", "📞 Коллекторы звонят", "🆓 Сам через МФЦ", "🔄 Уже пробовал",
                  "🚫 Не доверяю", "🙈 Стыдно / что скажут", "⏰ Времени нет", "⚖️ Уже в суде"]:
        await handle_template_objection(message, text)

    # Скрипт первого разговора
    elif text == "📞 Скрипт первого разговора":
        reply = (
            "📞 **Скрипт первого разговора**\n\n"
            "Добрый день / вечер, {ИМЯ КЛИЕНТА}?\n\n"
            "— Это [ваше имя], я помощник юриста компании «БанкротствоГрупп». Вы недавно общались с моей коллегой (Имя сотрудника кол-центра), она передала мне, что у вас сумма кредитов составляет ………… т.р. и вам интересно списание данной суммы. Всё верно?\n\n"
            "Пауза для ответа.\n\n"
            "— Отлично! Мы как раз специализируемся на списании всех кредитов и долгов и уже многим нашим гражданам помогли. Сейчас я уточню у вас пару вопросов, это займёт 5 минут. Удобно сейчас?\n\n"
            "Но перед этим расскажите, из чего эта сумма состоит (банки, МФО, долги по ЖКХ)?"
        )
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)

    else:
        # Всё остальное — вопрос к ИИ
        await handle_gigachat(message)

# ==================== ШАБЛОННЫЕ ВОЗРАЖЕНИЯ (по 2 варианта) ====================
async def handle_template_objection(message: types.Message, objection: str):
    templates = { ... }  # (тот же блок с 2 вариантами, что был раньше — не меняю, чтобы не удлинять сообщение)

    reply = templates.get(objection, "✅ Ответ на возражение загружен.")
    await message.answer(reply, parse_mode="Markdown", reply_markup=vozrazheniya_menu)

# ==================== GIGACHAT С ТВОИМ НОВЫМ ПРОМПТОМ ====================
async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не настроен.")
        return

    user_text = message.text

    # ← ТВОЙ НОВЫЙ ПРОМПТ ЗДЕСЬ
    system_prompt = """
Ты — профессиональный коуч и эксперт по банкротству физических лиц в России с более чем 10-летним опытом. Ты помог сотням людей успешно пройти процедуру банкротства через МФЦ и Арбитражный суд, списать долги от 300 тысяч до 50+ миллионов рублей.
Твоя главная задача — давать максимально подробные, развёрнутые, честные и поддерживающие ответы на любые вопросы о банкротстве физлиц.
Правила ответа:
- Всегда давай **развёрнутый ответ**.
- Никогда не отвечай коротко или односложно. Даже на простой вопрос раскрывай тему глубоко: объясняй причины, риски, нюансы, этапы, подводные камни, практические советы и реальные примеры из практики.
- Используй простой, живой, человеческий язык, без канцелярита. Объясняй как опытный наставник, который искренне хочет помочь человеку выйти из долговой ямы.
- Структура ответа (по возможности):
  1. Эмпатия и понимание ситуации человека
  2. Прямой и честный ответ на вопрос
  3. Подробное объяснение механизма (как это работает на практике)
  4. Важные нюансы и риски
  5. Пошаговые рекомендации, что делать дальше
Ты отлично знаешь:
- Все способы банкротства: через МФЦ (упрощённое) и через Арбитражный суд.
- Условия, требования, суммы долгов, последствия.
- Последние изменения в законодательстве (по состоянию на 2026 год).
- Как работает финансовый управляющий, сколько стоят его услуги.
- Что можно и нельзя делать до и во время процедуры.
- Как сохранить имущество (единственное жильё, автомобиль, зарплатную карту и т.д.).
- Последствия банкротства для кредитной истории, работы, выезда за границу, поручителей и родственников.
- Альтернативы банкротству (реструктуризация, рефинансирование, переговоры с банками).
Если вопрос касается конкретной ситуации человека — всегда проси дополнительные детали (сумма долгов, состав кредиторов, наличие имущества, доходы, регион и т.д.), чтобы дать максимально точный совет.
Ты категорически против «серых» и незаконных схем. Всегда говори только о легальных способах и честно предупреждаешь о всех рисках.
"""

    try:
        async with aiohttp.ClientSession() as session:
            # Получение Access Token
            async with session.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={
                    "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": "00000000-0000-0000-0000-000000000000"
                },
                data="scope=GIGACHAT_API_PERS",
                ssl=False
            ) as resp:
                token_data = await resp.json()
                access_token = token_data.get("access_token")

            if not access_token:
                await message.answer("❌ Не удалось получить токен.")
                return

            # Запрос к GigaChat
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
                    "temperature": 0.6,
                    "max_tokens": 1200
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
    print("✅ Бот запущен с твоим новым подробным промптом")
    asyncio.run(dp.start_polling(bot))
