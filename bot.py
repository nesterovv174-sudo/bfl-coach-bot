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

    # ==================== МЕНЮ ====================
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
        return

    elif text == "⚡ Быстрый ответ":
        await message.answer("⚡ Отправьте сообщение клиента — я предложу 2–3 варианта ответа.", reply_markup=main_menu)
        return

    elif text == "👋 Приветствие":
        await message.answer("👋 Добро пожаловать! Используйте меню ниже.", reply_markup=main_menu)

    elif text == "🔙 Назад в главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu)

    # ==================== СКРИПТ ПЕРВОГО РАЗГОВОРА ====================
    elif text == "📞 Скрипт первого разговора":
        reply = (
            "📞 **Скрипт первого разговора**\n\n"
            "Добрый день / вечер, {ИМЯ КЛИЕНТА}?\n\n"
            "— Это [ваше имя], я помощник юриста компании «БанкротствоГрупп». Вы недавно общались с моей коллегой...\n\n"
            "(вставьте сюда полный текст вашего скрипта)"
        )
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)

    # ==================== ШАБЛОННЫЕ ВОЗРАЖЕНИЯ (готовые тексты) ====================
    elif text in ["💰 Дорого / Цена", "🏠 Заберут квартиру", "🤔 Нужно подумать", "😟 Боюсь последствий",
                  "💸 Нет денег", "📞 Коллекторы звонят", "🆓 Сам через МФЦ", "🔄 Уже пробовал",
                  "🚫 Не доверяю", "🙈 Стыдно / что скажут", "⏰ Времени нет", "⚖️ Уже в суде"]:
        await handle_template_objection(message, text)

    else:
        # Если ничего не подошло — считаем, что это вопрос к ИИ
        await handle_gigachat(message)

# ==================== ШАБЛОННЫЕ ОТВЕТЫ НА ВОЗРАЖЕНИЯ ====================
async def handle_template_objection(message: types.Message, objection: str):
    replies = {
        "💰 Дорого / Цена": (
            "💰 **Дорого / Цена**\n\n"
            "**Вариант 1:**\n«Понимаю вас очень хорошо. Сейчас действительно каждая копейка на счету. При этом каждый месяц долг продолжает расти из-за процентов и пеней. Давайте вместе посчитаем, как будет выглядеть рассрочка на нашу работу — часто это выходит выгоднее, чем продолжать платить банкам.»\n\n"
            "**Вариант 2:**\n«Согласен, сумма выглядит большой. Но если ничего не делать, через год вы переплатите ещё больше. Мы помогаем остановить рост долга уже в первые недели.»"
        ),
        "🏠 Заберут квартиру": (
            "🏠 **Заберут квартиру**\n\n"
            "**Вариант 1:**\n«Это один из самых частых страхов. Хочу вас сразу успокоить: единственное жильё, в котором вы проживаете и прописаны, по закону защищено и не может быть продано (кроме ипотеки).»\n\n"
            "**Вариант 2:**\n«Я вас прекрасно понимаю, эта мысль пугает. На практике в 95% случаев единственное жильё остаётся у клиента. Давайте разберём вашу ситуацию.»"
        ),
        # Добавь остальные возражения по аналогии (я могу добавить все сразу)
        "🤔 Нужно подумать": "🤔 **Нужно подумать**\n\n**Вариант 1:**\n«Конечно, это важное решение. Давайте я отвечу на все ваши вопросы, чтобы вам было проще принять решение.»",
        # ... (остальные можно добавить позже)
    }

    reply = replies.get(objection, "✅ Ответ на возражение загружен.")
    await message.answer(reply, parse_mode="Markdown", reply_markup=vozrazheniya_menu)

# ==================== GIGACHAT ====================
async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не настроен.")
        return

    # Здесь будет вызов GigaChat (тот же код, что работал раньше)

    # Пока оставим заглушку, чтобы проверить структуру
    await message.answer("🤖 GigaChat получил ваш вопрос и думает над ответом...\n\n(пока в разработке — скоро будет полный ответ)")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен: шаблонные возражения + GigaChat")
    asyncio.run(dp.start_polling(bot))
