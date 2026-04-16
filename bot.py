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

    if text == "📋 Возражения":
        await message.answer("Выберите возражение клиента:", reply_markup=vozrazheniya_menu)

    elif text == "📞 Скрипты":
        await message.answer("Выберите скрипт:", reply_markup=skripty_menu)

    elif text == "🤖 Спросить у ИИ":
        await message.answer(
            "🤖 Режим умного ИИ включён.\n\n"
            "Задавайте любой вопрос по ситуации клиента — я дам **разбор** и рекомендации для тебя как менеджера.",
            reply_markup=main_menu
        )
        return

    elif text == "⚡ Быстрый ответ":
        await message.answer("⚡ Отправьте сообщение клиента — я предложу варианты ответа.", reply_markup=main_menu)
        return

    elif text == "👋 Приветствие":
        await message.answer("👋 Добро пожаловать! Используйте меню.", reply_markup=main_menu)

    elif text == "🔙 Назад в главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu)

    # ==================== ШАБЛОННЫЕ ВОЗРАЖЕНИЯ ====================
    elif text in ["💰 Дорого / Цена", "🏠 Заберут квартиру", "🤔 Нужно подумать", "😟 Боюсь последствий",
                  "💸 Нет денег", "📞 Коллекторы звонят", "🆓 Сам через МФЦ", "🔄 Уже пробовал",
                  "🚫 Не доверяю", "🙈 Стыдно / что скажут", "⏰ Времени нет", "⚖️ Уже в суде"]:
        await handle_template_objection(message, text)

    # ==================== СКРИПТ ====================
    elif text == "📞 Скрипт первого разговора":
        reply = "📞 **Скрипт первого разговора**\n\n(вставь сюда полный текст скрипта)"
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)

    else:
        # Всё остальное — вопрос сотрудника к ИИ
        await handle_gigachat(message)

# ==================== ШАБЛОННЫЕ ОТВЕТЫ ====================
async def handle_template_objection(message: types.Message, objection: str):
    templates = {
        "💰 Дорого / Цена": (
            "💰 **Дорого / Цена**\n\n"
            "**Вариант 1:**\n«Понимаю вас очень хорошо. Сейчас каждая копейка на счету. При этом долг каждый месяц растёт из-за процентов и пеней. Давайте посчитаем вместе, как будет выглядеть рассрочка на нашу работу — часто это выходит выгоднее.»\n\n"
            "**Вариант 2:**\n«Согласен, сумма выглядит большой. Но если ничего не делать, через год вы переплатите ещё больше. Мы помогаем остановить рост долга уже в первые недели.»"
        ),
        "🏠 Заберут квартиру": (
            "🏠 **Заберут квартиру**\n\n"
            "**Вариант 1:**\n«Это один из самых частых страхов. Единственное жильё, в котором вы проживаете и прописаны, по закону полностью защищено и не может быть продано.»\n\n"
            "**Вариант 2:**\n«Я вас понимаю, эта мысль пугает. На практике в большинстве случаев жильё остаётся у клиента. Давайте разберём вашу ситуацию.»"
        ),
        "🤔 Нужно подумать": (
            "🤔 **Нужно подумать**\n\n"
            "**Вариант 1:**\n«Конечно, это важное решение. Давайте я подробно отвечу на все ваши вопросы, чтобы вам было проще принять решение.»"
        ),
        "😟 Боюсь последствий": (
            "😟 **Боюсь последствий**\n\n"
            "**Вариант 1:**\n«Я вас очень хорошо понимаю. Давайте я честно расскажу, какие последствия реально есть по закону, а какие — просто мифы.»"
        ),
        "💸 Нет денег": (
            "💸 **Нет денег**\n\n"
            "**Вариант 1:**\n«Понимаю вас. У нас есть гибкая система оплаты и рассрочка. Главное — остановить давление коллекторов уже на старте.»"
        ),
        "📞 Коллекторы звонят": (
            "📞 **Коллекторы звонят**\n\n"
            "**Вариант 1:**\n«Понимаю, как это неприятно. После начала процедуры коллекторы обязаны прекратить общение с вами. Мы берём общение на себя.»"
        ),
        "🆓 Сам через МФЦ": (
            "🆓 **Сам через МФЦ**\n\n"
            "**Вариант 1:**\n«МФЦ подходит только для самых простых случаев. При больших суммах часто бывают отказы. Мы берём всю работу на себя и доводим до результата.»"
        ),
        "🔄 Уже пробовал": (
            "🔄 **Уже пробовал**\n\n"
            "**Вариант 1:**\n«Сочувствую, что предыдущий опыт был неудачным. Расскажите, пожалуйста, с чем именно вы столкнулись? Мы работаем по-другому.»"
        ),
        "🚫 Не доверяю": (
            "🚫 **Не доверяю**\n\n"
            "**Вариант 1:**\n«Понимаю ваше недоверие. Мы работаем официально, по договору. Могу показать примеры документов и отзывы реальных клиентов.»"
        ),
        "🙈 Стыдно / что скажут": (
            "🙈 **Стыдно / что скажут**\n\n"
            "**Вариант 1:**\n«Это очень деликатная тема. Многие клиенты вначале чувствуют то же самое. На практике это почти не влияет на повседневную жизнь.»"
        ),
        "⏰ Времени нет": (
            "⏰ **Времени нет**\n\n"
            "**Вариант 1:**\n«Понимаю, график плотный. Мы можем провести короткую консультацию по телефону или в мессенджере.»"
        ),
        "⚖️ Уже в суде": (
            "⚖️ **Уже в суде**\n\n"
            "**Вариант 1:**\n«Это не критично. Банкротство можно запустить даже при наличии судебных решений. Мы часто работаем с такими случаями.»"
        ),
    }

    reply = templates.get(objection, "✅ Ответ на возражение загружен.")
    await message.answer(reply, parse_mode="Markdown", reply_markup=vozrazheniya_menu)

# ==================== GIGACHAT (только разбор, без лишних вариантов) ====================
async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не настроен.")
        return

    user_text = message.text

    system_prompt = """
Ты — экспертный AI-коуч для менеджеров по банкротству физических лиц.
Сотрудник задаёт тебе вопрос по ситуации клиента.
Отвечай **только разбор ситуации** + рекомендации менеджеру.
Не предлагай варианты ответа клиенту, если тебя об этом не просят.
Используй эмпатию и профессиональный тон.
Отвечай только на русском.
"""

    try:
        async with aiohttp.ClientSession() as session:
            # Получаем Access Token
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
    print("✅ Бот запущен: шаблонные возражения + чистый GigaChat")
    asyncio.run(dp.start_polling(bot))
