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
            "🤖 Режим анализа ситуации включён.\n\n"
            "Опишите ситуацию клиента (доход, долги, имущество и т.д.) — я рассчитаю конкурсную массу, скажу можно ли списать долги и подробно разберу варианты защиты имущества.",
            reply_markup=main_menu
        )
        return

    elif text == "👋 Приветствие":
        await message.answer("👋 Добро пожаловать! Используйте меню ниже.", reply_markup=main_menu)

    elif text == "🔙 Назад в главное меню":
        await message.answer("Главное меню:", reply_markup=main_menu)

    elif text in ["💰 Дорого / Цена", "🏠 Заберут квартиру", "🤔 Нужно подумать", "😟 Боюсь последствий",
                  "💸 Нет денег", "📞 Коллекторы звонят", "🆓 Сам через МФЦ", "🔄 Уже пробовал",
                  "🚫 Не доверяю", "🙈 Стыдно / что скажут", "⏰ Времени нет", "⚖️ Уже в суде"]:
        await handle_template_objection(message, text)

    elif text == "📞 Скрипт первого разговора":
        reply = (
            "📞 **Скрипт первого разговора**\n\n"
            "Добрый день / вечер, {ИМЯ КЛИЕНТА}?\n\n"
            "— Это [ваше имя], я помощник юриста компании «БанкротствоГрупп». Вы недавно общались с моей коллегой (Имя сотрудника кол-центра), она передала мне что у вас сумма кредитов составляет ………… т.р и вам интересно списания данной суммы. Все верно ?\n\n"
            "Пауза для ответа.\n\n"
            "— Отлично! Мы как раз специализируемся на списании всех кредитов и долгов и уже многим нашим гражданам помогли. Сейчас я уточню у вас пару вопросов, Это займет 5 минут. Удобно сейчас?\n\n"
            "Но перед этим расскажите из чего эта сумма состоит ( Банки, мфо, долги по жкх).\n\n"
            "Шаг 2: Классификация\n"
            "Подскажите, проживаете в г. Воронеже или области?\n"
            "1. Подскажите, есть ли по данным кредитам или по части из них просрочки?\n"
            "2. Иван Иванович, подскажите, как давно уже не платите по кредитам? Сколько дней / месяцев у Вас просрочки?\n"
            "3. Подскажите что привело к возникновению просрочек по платежам? Что стало причиной трудностей с погашением задолженности?\n"
            "4. Подскажите, какой у Вас должен быть / есть ежемесячный платёж по всем кредитам, МФО, налогам (если есть)?\n"
            "5. ИМЯ КЛИЕНТА… Могу я узнать, а какая у Вас в данный момент именно официальная заработная плата?\n"
            "6. Так же на мало-важный вопрос, на Вас оформленное имущество какое-то есть? Что-то числится? Квартиры, дома, машины.\n"
            "Иван Иванович, а какой вариант Вы рассматриваете, снижение платежей по кредитам или возможность полного списания всех ваших долгов?\n\n"
            "Шаг 3: Закрепление\n"
            "{ИМЯ КЛИЕНТА}, если мы подберём вариант как {списать или уменьшить Вам платёж / полностью списать долг / иное решение}, это полностью решит Вашу проблему, я верно Вас понял(а)?\n\n"
            "Шаг 4: Предложение (назначение встречи)\n"
            "{ИМЯ КЛИЕНТА}, хочу отметить, что Ваша проблема для нас абсолютно типичная, и мы постоянно помогаем людям в аналогичных ситуациях.\n"
            "Давайте с Вами договоримся о встрече. Это бесплатно. Мы проанализируем вашу ситуацию, ответим на все ваши вопросы, проведем финансово-правовой анализ.\n\n"
            "Шаг 5: Закрытие\n"
            "{ИМЯ КЛИЕНТА}, в таком случае давайте назначим время Встречи. Завтра удобно будет подъехать?\n"
            "Возьмите, пожалуйста, на встречу документы по кредитам, если они есть.\n"
            "Дату, время и наш адрес я вам отправлю на мессенджер. Подскажите на данном номере у вас есть WhatsApp / Telegram?"
        )
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)

    else:
        await handle_gigachat(message)

# ==================== ФИКСИРОВАННЫЕ ОТВЕТЫ НА ВОЗРАЖЕНИЯ ====================
async def handle_template_objection(message: types.Message, objection: str):
    templates = {
        "💰 Дорого / Цена": (
            "💰 **Дорого / Цена**\n\n"
            "**Вариант 1:**\n«Понимаю вас очень хорошо. Сейчас действительно каждая копейка на счету, и любая дополнительная трата вызывает вопросы. При этом каждый месяц на вас продолжают начисляться проценты и пени. Давайте вместе посчитаем, как будет выглядеть рассрочка на нашу работу.»\n\n"
            "**Вариант 2:**\n«Согласен, сумма выглядит большой. Но если ничего не делать, через год вы переплатите ещё больше. Мы помогаем остановить рост долга уже в первые недели.»"
        ),
        "🏠 Заберут квартиру": (
            "🏠 **Заберут квартиру**\n\n"
            "**Вариант 1:**\n«Это один из самых частых страхов. Единственное жильё, в котором вы проживаете, по закону полностью защищено.»\n\n"
            "**Вариант 2:**\n«Я вас понимаю, эта мысль пугает. На практике в большинстве случаев жильё остаётся у клиента.»"
        ),
        # Добавь остальные по необходимости
    }

    reply = templates.get(objection, "✅ Ответ на возражение загружен.")
    await message.answer(reply, parse_mode="Markdown", reply_markup=vozrazheniya_menu)

# ==================== GIGACHAT С УЛУЧШЕННЫМ ПРОМПТОМ ====================
async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не настроен.")
        return

    # Читаем rules.txt
    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            rules_content = f.read().strip()
    except FileNotFoundError:
        rules_content = "Правила и актуальные данные не найдены."

    user_text = message.text

    system_prompt = f"""
Ты — узкоспециализированный эксперт по банкротству физических лиц в России (актуально на 2026 год).

Вот актуальные правила и цифры от владельца компании, на которые ты **обязательно** должен ориентироваться при каждом расчёте:

{rules_content}

Ты отвечаешь ИСКЛЮЧИТЕЛЬНО на вопросы по банкротству физических лиц.

Правила ответа:
1. Всегда начинай с **Прямого ответа**: можно ли в данной ситуации списать долги или нельзя.
2. Обязательно рассчитывай конкурсную массу на основе дохода и прожиточного минимума из rules.txt. Показывай расчёт в рублях с примером.
3. Подробно разбирай возможность списания долгов при данном доходе.
4. Очень подробно говори про имущество и варианты его спасения (единственное жильё, автомобиль, зарплатная карта, техника и т.д.).
5. Давай развёрнутый ответ с пошаговыми рекомендациями.
6. Если информации недостаточно — в конце задавай конкретные уточняющие вопросы нумерованным списком.

Отвечай профессионально, чётко и очень подробно. Используй нумерацию и списки. Все суммы указывай только в рублях.
"""

    try:
        async with aiohttp.ClientSession() as session:
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
                    "temperature": 0.5,
                    "max_tokens": 2000
                },
                ssl=False
            ) as resp:
                data = await resp.json()
                ai_reply = data["choices"][0]["message"]["content"]
                await message.answer(ai_reply, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка GigaChat:\n{str(e)[:600]}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен: rules.txt + расчёт конкурсной массы + акцент на имущество")
    asyncio.run(dp.start_polling(bot))
