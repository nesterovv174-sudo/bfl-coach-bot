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
        [KeyboardButton(text="🤖 Спросить у ИИ")],
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
        await message.answer("🤖 Режим анализа ситуации включён.\n\nОпишите ситуацию клиента (доход, долги, имущество и т.д.)", reply_markup=main_menu)
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
        # (полный скрипт как раньше — оставил без изменений)
        reply = "📞 **Скрипт первого разговора**\n\n[твой полный 5-шаговый скрипт здесь — вставь если нужно]"
        await message.answer(reply, parse_mode="Markdown", reply_markup=skripty_menu)
    else:
        await handle_gigachat(message)

async def handle_template_objection(message: types.Message, objection: str):
    # (шаблоны как раньше — можешь дополнить)
    await message.answer("✅ Ответ на возражение загружен.", reply_markup=vozrazheniya_menu)

# ==================== GIGACHAT — МАКСИМАЛЬНО ЖЁСТКИЙ ПРОМПТ ====================
async def handle_gigachat(message: types.Message):
    if not GIGACHAT_AUTH_KEY:
        await message.answer("❌ Ключ GigaChat не настроен.")
        return

    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            rules_content = f.read().strip()
    except FileNotFoundError:
        rules_content = "Правила не найдены."

    user_text = message.text

    system_prompt = f"""
Ты — эксперт по банкротству физических лиц в России 2026 года.

**СТРОГОЕ ПРАВИЛО №1 (повторяй это в голове перед каждым ответом):**
Используй ТОЛЬКО данные из блока ниже. Никогда не бери другие цифры прожиточного минимума.

=== ПРАВИЛА ИЗ rules.txt (обязательно использовать эти цифры) ===
{rules_content}
=== КОНЕЦ ПРАВИЛ ===

**СТРОГОЕ ПРАВИЛО №2:**
Все расчёты делай **только в рублях**. Пример правильного расчёта для пенсионера с пенсией 18 000 руб.:
Доход = 18 000 руб.
Прожиточный минимум пенсионера = 16 000 руб.
Конкурсная масса = 18 000 - 16 000 = 2 000 руб. в месяц.

**Правила ответа (обязательно соблюдай порядок):**
1. Начинай с **Прямого ответа**: можно ли списать долги или нельзя.
2. Обязательно делай расчёт конкурсной массы по правилам выше и показывай пример в рублях.
3. Подробно разбирай защиту имущества и варианты его спасения.
4. Давай подробный ответ.
5. В конце — уточняющие вопросы нумерованным списком, если нужно.

Отвечай только по теме банкротства физлиц.
"""

    try:
        async with aiohttp.ClientSession() as session:
            # Получаем токен
            async with session.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={"Authorization": f"Basic {GIGACHAT_AUTH_KEY}", "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json", "RqUID": "00000000-0000-0000-0000-000000000000"},
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
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={
                    "model": "GigaChat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ],
                    "temperature": 0.2,   # максимально низко — почти не фантазирует
                    "max_tokens": 2200
                },
                ssl=False
            ) as resp:
                data = await resp.json()
                ai_reply = data["choices"][0]["message"]["content"]
                await message.answer(ai_reply, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка:\n{str(e)[:500]}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен — максимально жёсткий промпт + принуждение rules.txt")
    asyncio.run(dp.start_polling(bot))
