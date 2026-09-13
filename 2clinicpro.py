import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

# =========================================================
# 1. BOT TOKEN
# =========================================================

BOT_TOKEN = "8990025362:AAGPgrk12jYV112TdaMKp04niyS_XQUS1p8"

bot = telebot.TeleBot(BOT_TOKEN)

# =========================================================
# 2. DATABASE
# =========================================================

db = sqlite3.connect("clinic.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    doctor_key TEXT,
    phone TEXT,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_telegram_id INTEGER,
    patient_name TEXT,
    patient_phone TEXT,
    doctor_key TEXT,
    doctor_name TEXT,
    doctor_phone TEXT,
    date TEXT,
    time TEXT,
    language TEXT,
    created_at TEXT
)
""")

db.commit()

# =========================================================
# 3. DOKTORLAR
# =========================================================

DOCTORS = {
    "terapevt": {
        "uz": "Terapevt",
        "tj": "Терапевт",
        "ru": "Терапевт"
    },

    "stomatolog": {
        "uz": "Stomatolog",
        "tj": "Стоматолог",
        "ru": "Стоматолог"
    },

    "kardiolog": {
        "uz": "Kardiolog",
        "tj": "Кардиолог",
        "ru": "Кардиолог"
    },

    "nevrolog": {
        "uz": "Nevrolog",
        "tj": "Невролог",
        "ru": "Невролог"
    }
}

# =========================================================
# 4. DOKTOR TELEFONLARI
# =========================================================

DOCTOR_PHONES = {
    "terapevt": "",
    "stomatolog": "03 105 5252",
    "kardiolog": "",
    "nevrolog": ""
}

# =========================================================
# 5. TARJIMALAR
# =========================================================

T = {

"uz": {

    "language":
        "🌐 Tilni tanlang:",

    "doctor":
        "👨‍⚕️ Shifokorni tanlang:",

    "date":
        "📅 Qabul kunini tanlang:",

    "time":
        "🕐 Qabul vaqtini tanlang:",

    "name":
        "👤 Ism va familiyangizni kiriting:",

    "phone":
        "📱 Telefon raqamingizni yuboring yoki yozing:",

    "send_phone":
        "📱 Telefon raqamimni yuborish",

    "busy":
        "❌ Kechirasiz, bu vaqt allaqachon band.\n"
        "Iltimos, boshqa vaqtni tanlang.",

    "success":
        "✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!\n\n"
        "👤 Foydalanuvchi: {name}\n"
        "👨‍⚕️ Shifokor: {doctor}\n"
        "📅 Sana: {date}\n"
        "🕐 Vaqt: {time}\n"
        "📱 Telefon: {phone}\n\n"
        "❤️ Sizning sog‘ligingiz biz uchun muhim!",

    "doctor_registered":
        "✅ Siz {doctor} sifatida ro‘yxatdan o‘tdingiz.\n\n"
        "📱 Telefon: {phone}\n\n"
        "Endi bemor sizga yozilsa, ma’lumotlar Telegramingizga keladi."
},

"tj": {

    "language":
        "🌐 Забонро интихоб кунед:",

    "doctor":
        "👨‍⚕️ Духтурро интихоб кунед:",

    "date":
        "📅 Рӯзи қабулро интихоб кунед:",

    "time":
        "🕐 Вақти қабулро интихоб кунед:",

    "name":
        "👤 Ном ва насабатонро нависед:",

    "phone":
        "📱 Рақами телефони худро фиристед ё нависед:",

    "send_phone":
        "📱 Рақами телефони ман",

    "busy":
        "❌ Мутаассифона, ин вақт аллакай банд аст.\n"
        "Лутфан вақти дигарро интихоб кунед.",

    "success":
        "✅ Шумо бомуваффақият ба қайд гирифта шудед!\n\n"
        "👤 Ном: {name}\n"
        "👨‍⚕️ Духтур: {doctor}\n"
        "📅 Сана: {date}\n"
        "🕐 Вақт: {time}\n"
        "📱 Телефон: {phone}\n\n"
        "❤️ Саломатии шумо барои мо муҳим аст!",

    "doctor_registered":
        "✅ Шумо ҳамчун {doctor} ба қайд гирифта шудед.\n\n"
        "📱 Телефон: {phone}\n\n"
        "Акнун маълумоти беморон ба Telegram-и шумо меояд."
},

"ru": {

    "language":
        "🌐 Выберите язык:",

    "doctor":
        "👨‍⚕️ Выберите врача:",

    "date":
        "📅 Выберите дату приёма:",

    "time":
        "🕐 Выберите время приёма:",

    "name":
        "👤 Введите имя и фамилию:",

    "phone":
        "📱 Отправьте или введите номер телефона:",

    "send_phone":
        "📱 Отправить мой номер",

    "busy":
        "❌ К сожалению, это время уже занято.\n"
        "Пожалуйста, выберите другое время.",

    "success":
        "✅ Вы успешно записались!\n\n"
        "👤 Пациент: {name}\n"
        "👨‍⚕️ Врач: {doctor}\n"
        "📅 Дата: {date}\n"
        "🕐 Время: {time}\n"
        "📱 Телефон: {phone}\n\n"
        "❤️ Ваше здоровье важно для нас!",

    "doctor_registered":
        "✅ Вы зарегистрированы как {doctor}.\n\n"
        "📱 Телефон: {phone}\n\n"
        "Теперь информация о пациентах будет приходить вам в Telegram."
}

}

# =========================================================
# 6. USER SESSION
# =========================================================

users = {}

# =========================================================
# 7. START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    users[message.chat.id] = {
        "lang": None,
        "doctor": None,
        "date": None,
        "time": None,
        "name": None,
        "phone": None
    }

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🇺🇿 O‘zbekcha",
            callback_data="lang_uz"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🇹🇯 Тоҷикӣ",
            callback_data="lang_tj"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🇷🇺 Русский",
            callback_data="lang_ru"
        )
    )

    bot.send_message(
        message.chat.id,
        "🌐 Tilni tanlang / Забонро интихоб кунед / Выберите язык:",
        reply_markup=keyboard
    )

# =========================================================
# 8. DOKTOR UCHUN /doctor
# =========================================================

@bot.message_handler(commands=["doctor"])
def doctor_command(message):

    keyboard = types.InlineKeyboardMarkup()

    for key, doctor in DOCTORS.items():

        keyboard.add(
            types.InlineKeyboardButton(
                "👨‍⚕️ " + doctor["uz"],
                callback_data="register_" + key
            )
        )

    bot.send_message(
        message.chat.id,
        "👨‍⚕️ Doktor turini tanlang:",
        reply_markup=keyboard
    )

# =========================================================
# 9. DOKTORNI RO‘YXATDAN O‘TKAZISH
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("register_")
)
def register_doctor(call):

    doctor_key = call.data.replace(
        "register_",
        ""
    )

    telegram_id = call.from_user.id

    doctor_name = DOCTORS[doctor_key]["uz"]

    doctor_phone = DOCTOR_PHONES[doctor_key]

    cur.execute("""
        INSERT OR REPLACE INTO doctors
        (
            telegram_id,
            doctor_key,
            phone,
            name
        )
        VALUES (?, ?, ?, ?)
    """, (
        telegram_id,
        doctor_key,
        doctor_phone,
        doctor_name
    ))

    db.commit()

    bot.answer_callback_query(
        call.id,
        "✅ Saqlandi!"
    )

    bot.send_message(
        call.message.chat.id,
        T["uz"]["doctor_registered"].format(
            doctor=doctor_name,
            phone=doctor_phone
        )
    )

# =========================================================
# 10. TIL TANLASH
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lang_")
)
def language(call):

    lang = call.data.replace(
        "lang_",
        ""
    )

    users[call.message.chat.id]["lang"] = lang

    bot.answer_callback_query(call.id)

    show_doctors(call.message.chat.id)

# =========================================================
# 11. DOKTORLARNI KO‘RSATISH
# =========================================================

def show_doctors(chat_id):

    lang = users[chat_id]["lang"]

    keyboard = types.InlineKeyboardMarkup()

    for key, doctor in DOCTORS.items():

        keyboard.add(
            types.InlineKeyboardButton(
                "👨‍⚕️ " + doctor[lang],
                callback_data="doctor_" + key
            )
        )

    bot.send_message(
        chat_id,
        T[lang]["doctor"],
        reply_markup=keyboard
    )

# =========================================================
# 12. DOKTOR TANLASH
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("doctor_")
)
def choose_doctor(call):

    chat_id = call.message.chat.id

    doctor_key = call.data.replace(
        "doctor_",
        ""
    )

    users[chat_id]["doctor"] = doctor_key

    bot.answer_callback_query(call.id)

    show_dates(chat_id)

# =========================================================
# 13. SANA TANLASH
# =========================================================

def show_dates(chat_id):

    lang = users[chat_id]["lang"]

    keyboard = types.InlineKeyboardMarkup()

    today = datetime.now()

    for i in range(7):

        d = today + timedelta(days=i)

        display = d.strftime("%d.%m.%Y")

        database_date = d.strftime("%Y-%m-%d")

        keyboard.add(
            types.InlineKeyboardButton(
                "📅 " + display,
                callback_data="date_" + database_date
            )
        )

    bot.send_message(
        chat_id,
        T[lang]["date"],
        reply_markup=keyboard
    )

# =========================================================
# 14. SANA
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("date_")
)
def choose_date(call):

    chat_id = call.message.chat.id

    date = call.data.replace(
        "date_",
        ""
    )

    users[chat_id]["date"] = date

    bot.answer_callback_query(call.id)

    show_times(chat_id)

# =========================================================
# 15. VAQTLAR
# =========================================================

def show_times(chat_id):

    lang = users[chat_id]["lang"]

    doctor = users[chat_id]["doctor"]

    date = users[chat_id]["date"]

    keyboard = types.InlineKeyboardMarkup()

    times = [
        "09:00",
        "09:30",
        "10:00",
        "10:30",
        "11:00",
        "11:30",

        # TUSHLIK 12:00 - 13:00 YO‘Q

        "13:00",
        "13:30",
        "14:00",
        "14:30",
        "15:00",
        "15:30",
        "16:00",
        "16:30"
    ]

    for time in times:

        cur.execute("""
            SELECT id
            FROM bookings
            WHERE doctor_key=?
            AND date=?
            AND time=?
        """, (
            doctor,
            date,
            time
        ))

        busy = cur.fetchone()

        if busy:
            text = "🔴 " + time
        else:
            text = "🟢 " + time

        keyboard.add(
            types.InlineKeyboardButton(
                text,
                callback_data="time_" + time
            )
        )

    bot.send_message(
        chat_id,
        T[lang]["time"],
        reply_markup=keyboard
    )

# =========================================================
# 16. VAQT TANLASH
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("time_")
)
def choose_time(call):

    chat_id = call.message.chat.id

    time = call.data.replace(
        "time_",
        ""
    )

    doctor = users[chat_id]["doctor"]

    date = users[chat_id]["date"]

    cur.execute("""
        SELECT id
        FROM bookings
        WHERE doctor_key=?
        AND date=?
        AND time=?
    """, (
        doctor,
        date,
        time
    ))

    if cur.fetchone():

        lang = users[chat_id]["lang"]

        bot.answer_callback_query(
            call.id,
            T[lang]["busy"],
            show_alert=True
        )

        show_times(chat_id)

        return

    users[chat_id]["time"] = time

    bot.answer_callback_query(call.id)

    ask_name(chat_id)

# =========================================================
# 17. ISM
# =========================================================

def ask_name(chat_id):

    lang = users[chat_id]["lang"]

    bot.send_message(
        chat_id,
        T[lang]["name"]
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id,
        get_name
    )

def get_name(message):

    chat_id = message.chat.id

    users[chat_id]["name"] = message.text.strip()

    ask_phone(chat_id)

# =========================================================
# 18. TELEFON
# =========================================================

def ask_phone(chat_id):

    lang = users[chat_id]["lang"]

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    keyboard.add(
        types.KeyboardButton(
            T[lang]["send_phone"],
            request_contact=True
        )
    )

    bot.send_message(
        chat_id,
        T[lang]["phone"],
        reply_markup=keyboard
    )

    bot.register_next_step_handler_by_chat_id(
        chat_id,
        get_phone
    )

def get_phone(message):

    chat_id = message.chat.id

    if message.contact:

        phone = message.contact.phone_number

    else:

        phone = message.text.strip()

    users[chat_id]["phone"] = phone

    save_booking(chat_id)

# =========================================================
# 19. BOOKING SAQLASH
# =========================================================

def save_booking(chat_id):

    data = users[chat_id]

    lang = data["lang"]

    doctor_key = data["doctor"]

    doctor_name = DOCTORS[doctor_key][lang]

    doctor_phone = DOCTOR_PHONES[doctor_key]

    date = data["date"]

    time = data["time"]

    name = data["name"]

    phone = data["phone"]

    # YANA BIR MARTA TEKSHIRISH
    cur.execute("""
        SELECT id
        FROM bookings
        WHERE doctor_key=?
        AND date=?
        AND time=?
    """, (
        doctor_key,
        date,
        time
    ))

    if cur.fetchone():

        bot.send_message(
            chat_id,
            T[lang]["busy"],
            reply_markup=types.ReplyKeyboardRemove()
        )

        show_times(chat_id)

        return

    # BAZAGA SAQLASH
    cur.execute("""
        INSERT INTO bookings
        (
            patient_telegram_id,
            patient_name,
            patient_phone,
            doctor_key,
            doctor_name,
            doctor_phone,
            date,
            time,
            language,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        chat_id,
        name,
        phone,
        doctor_key,
        doctor_name,
        doctor_phone,
        date,
        time,
        lang,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    db.commit()

    nice_date = datetime.strptime(
        date,
        "%Y-%m-%d"
    ).strftime("%d.%m.%Y")

    # BEMORGA XABAR
    bot.send_message(
        chat_id,
        T[lang]["success"].format(
            name=name,
            doctor=doctor_name,
            date=nice_date,
            time=time,
            phone=phone
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )

    # DOKTORGA XABAR
    send_doctor_message(
        doctor_key,
        name,
        phone,
        doctor_name,
        doctor_phone,
        nice_date,
        time
    )

# =========================================================
# 20. DOKTOR TELEGRAMIGA XABAR
# =========================================================

def send_doctor_message(
    doctor_key,
    patient_name,
    patient_phone,
    doctor_name,
    doctor_phone,
    date,
    time
):

    cur.execute("""
        SELECT telegram_id
        FROM doctors
        WHERE doctor_key=?
    """, (
        doctor_key,
    ))

    result = cur.fetchone()

    if not result:

        print(
            "❌ Doktor hali /doctor orqali ro‘yxatdan o‘tmagan!"
        )

        return

    doctor_telegram_id = result[0]

    text = (
        "🏥 YANGI BEMOR!\n\n"

        "👤 Bemor: " +
        patient_name +
        "\n"

        "📱 Bemor telefoni: " +
        patient_phone +
        "\n\n"

        "👨‍⚕️ Shifokor: " +
        doctor_name +
        "\n"

        "📱 Shifokor telefoni: " +
        doctor_phone +
        "\n\n"

        "📅 Sana: " +
        date +
        "\n"

        "🕐 Vaqt: " +
        time +
        "\n\n"

        "✅ Bemor qabulga yozildi."
    )

    try:

        bot.send_message(
            doctor_telegram_id,
            text
        )

        print(
            "✅ Doktorga xabar yuborildi!"
        )

    except Exception as error:

        print(
            "❌ Doktorga xabar yuborishda xato:"
        )

        print(error)

# =========================================================
# 21. BOTNI ISHGA TUSHIRISH
# =========================================================

print("==========================================")
print("🏥 KLINIKA TELEGRAM BOT")
print("==========================================")
print("✅ Bot ishga tushdi")
print("🦷 Stomatolog: 03 105 5252")
print("==========================================")

bot.infinity_polling(
    skip_pending=True
)