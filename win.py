import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

TOKEN = "7605412218:AAGsKUzKzD6qxNTJ78550Aqy5_zyYWDudm4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

bot.remove_webhook()
time.sleep(1)

user_data = {}

# ────────── КНОПКИ ──────────
def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("➗ Разделить на 2", callback_data="div2"),
        InlineKeyboardButton("➗ Разделить на 3", callback_data="div3"),
    )
    kb.add(InlineKeyboardButton("🔄 Обновить", callback_data="refresh"))
    return kb

# ────────── START ──────────
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "💎 <b>PREMIUM HEDGE STRATEGY</b>\n\n"
        "Введите <b>банк</b> одной конторы\n\n"
        "Пример:\n<b>280</b>"
    )

@bot.callback_query_handler(func=lambda c: c.data == "refresh")
def refresh(call):
    bot.send_message(call.message.chat.id, "💰 Введите банк:")
    bot.answer_callback_query(call.id)

# ────────── РАСЧЁТ БАЗЫ ──────────
@bot.message_handler(func=lambda m: m.text.isdigit())
def calculate(message):
    bank = int(message.text)

    high = bank // 3 + 10
    mid = high
    low = bank - high - mid
    if low < 0:
        high = bank // 3
        mid = high
        low = bank - high - mid

    red = high
    black = mid
    blue = low

    white = max(red, black, blue) - min(red, black, blue)
    total = red + black + blue + white
    zero = round(total / 36, 2)

    user_data[message.chat.id] = {
        "red": red,
        "black": black,
        "blue": blue,
        "white": white,
        "zero": zero
    }

    send_strategy(message.chat.id, red, black, blue, white, zero, total)

# ────────── ДЕЛЕНИЕ ──────────
@bot.callback_query_handler(func=lambda c: c.data in ["div2", "div3"])
def divide(call):
    div = 2 if call.data == "div2" else 3
    data = user_data.get(call.message.chat.id)
    if not data:
        return

    red = round(data["red"] / div, 2)
    black = round(data["black"] / div, 2)
    blue = round(data["blue"] / div, 2)
    white = round(data["white"] / div, 2)
    zero = round(data["zero"] / div, 2)

    total = red + black + blue + white
    send_strategy(call.message.chat.id, red, black, blue, white, zero, total, div)
    bot.answer_callback_query(call.id)

# ────────── ВЫВОД ──────────
def send_strategy(chat_id, red, black, blue, white, zero, total, div=None):
    title = "💎 <b>PREMIUM STRATEGY</b>"
    if div:
        title += f"\n➗ Деление на {div}"

    text = (
        "━━━━━━━━━━━━━━━━━━\n"
        f"{title}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "🏦 <b>Основная контора</b>\n\n"
        f"🔴 Красный:\n<b>{red} $</b>\n\n"
        f"⚫ Чёрный:\n<b>{black} $</b>\n\n"
        f"🔵 Синий:\n<b>{blue} $</b>\n\n"

        "➕ <b>Другая контора</b>\n\n"
        f"⚪ Белый (остаток):\n<b>{white} $</b>\n\n"

        "🛡 <b>Страховка</b>\n\n"
        f"🟢 0:\n<b>{zero} $</b>\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Общая сумма:</b>\n<b>{round(total,2)} $</b>\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    bot.send_message(chat_id, text, reply_markup=main_kb())

bot.infinity_polling(skip_pending=True)
