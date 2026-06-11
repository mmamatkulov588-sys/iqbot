import random
import sqlite3
import json
import os
import time
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ═══════════════════════════════════════════
# TOKEN VA ADMIN
# ═══════════════════════════════════════════
TOKEN        = "8950030772:AAGNsNjiqWEih2EI9NzfqsoYTfQ4xstkyY4"
ADMIN_IDS    = [8631917509]
BOT_USERNAME = "IQ_SAVOL_LAR_BOT"

# ═══════════════════════════════════════════
# DARAJALAR
# ═══════════════════════════════════════════
DARAJALAR = [
    {"nom": "🥚 Tuxum",     "min": 0,    "max": 49},
    {"nom": "🐣 Jo'ja",     "min": 50,   "max": 149},
    {"nom": "🦅 Lochin",    "min": 150,  "max": 299},
    {"nom": "🔥 Olimcha",   "min": 300,  "max": 499},
    {"nom": "🧠 Daho",      "min": 500,  "max": 799},
    {"nom": "👑 Ustoz",     "min": 800,  "max": 1199},
    {"nom": "🚀 Yulduz",    "min": 1200, "max": 1799},
    {"nom": "⚡ Legenda",   "min": 1800, "max": 2499},
    {"nom": "💎 Almos",     "min": 2500, "max": 3999},
    {"nom": "🌌 Galaktika", "min": 4000, "max": 999999},
]

BALL_JADVAL = {
    "juda_oson":   1,
    "oson":        1,
    "orta":        2,
    "qiyin":       3,
    "juda_qiyin":  4,
    "topishmoq":   3,
}

DARAJA_EMOJI = {
    "juda_oson":  "⚪",
    "oson":       "🟢",
    "orta":       "🟡",
    "qiyin":      "🔴",
    "juda_qiyin": "🔥",
    "topishmoq":  "🎭",
}

def daraja_aniqlash(ball):
    for d in DARAJALAR:
        if d["min"] <= ball <= d["max"]:
            return d
    return DARAJALAR[-1]

def keyingi_daraja(ball):
    for i, d in enumerate(DARAJALAR):
        if d["min"] <= ball <= d["max"]:
            return DARAJALAR[i+1] if i+1 < len(DARAJALAR) else None
    return None

# ═══════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════
db = sqlite3.connect("iqbot.db", check_same_thread=False)
cur = db.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY,
    name          TEXT,
    username      TEXT DEFAULT '',
    score         INTEGER DEFAULT 0,
    correct       INTEGER DEFAULT 0,
    wrong         INTEGER DEFAULT 0,
    premium       INTEGER DEFAULT 0,
    vip           INTEGER DEFAULT 0,
    daily_answers INTEGER DEFAULT 0,
    daraja        TEXT DEFAULT '🥚 Tuxum',
    referals      INTEGER DEFAULT 0,
    ref_by        INTEGER DEFAULT 0,
    joined_at     TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS musobaqa (
    user_id  INTEGER PRIMARY KEY,
    name     TEXT,
    correct  INTEGER DEFAULT 0,
    wrong    INTEGER DEFAULT 0,
    vaqt     REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS musobaqa_holati (
    id      INTEGER PRIMARY KEY CHECK (id=1),
    faol    INTEGER DEFAULT 0,
    tugash  REAL DEFAULT 0
);
INSERT OR IGNORE INTO musobaqa_holati (id, faol, tugash) VALUES (1, 0, 0);
""")
db.commit()

# ═══════════════════════════════════════════
# SAVOLLAR
# ═══════════════════════════════════════════
def load_q(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

iq_all       = load_q("questions/iq.json")
logic_all    = load_q("questions/logic.json")
topishmoq_all = load_q("questions/topishmoq.json")

def filter_level(qs, level):
    f = [q for q in qs if q.get("daraja") == level]
    return f if f else qs

# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════
def get_user(uid):
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    return cur.fetchone()

def ensure_user(uid, name, username=""):
    existing = get_user(uid)
    if not existing:
        cur.execute(
            "INSERT INTO users (user_id, name, username, joined_at) VALUES (?, ?, ?, ?)",
            (uid, name, username or "", datetime.now().strftime("%Y-%m-%d"))
        )
        db.commit()
        return True  # yangi foydalanuvchi
    return False  # eski foydalanuvchi

def upd_daraja(uid, ball):
    d = daraja_aniqlash(ball)
    cur.execute("UPDATE users SET daraja=? WHERE user_id=?", (d["nom"], uid))
    db.commit()

def is_admin(uid):
    return uid in ADMIN_IDS

def musobaqa_faol():
    cur.execute("SELECT faol, tugash FROM musobaqa_holati WHERE id=1")
    row = cur.fetchone()
    if not row or not row[0]:
        return False
    if row[1] > 0 and time.time() > row[1]:
        cur.execute("UPDATE musobaqa_holati SET faol=0 WHERE id=1")
        db.commit()
        return False
    return True

# ═══════════════════════════════════════════
# MENYULAR
# ═══════════════════════════════════════════
main_menu = ReplyKeyboardMarkup([
    ["🧠 IQ TEST",      "🧩 MANTIQ"],
    ["🎲 ARALASH",      "🎭 TOPISHMOQ"],
    ["📊 STATISTIKA",   "👤 PROFIL"],
    ["🏆 TOP-10",       "🎖 DARAJALAR"],
    ["💎 PREMIUM",      "👥 REFERAL"],
    ["⚔️ MUSOBAQA"],
], resize_keyboard=True)

daraja_menu = ReplyKeyboardMarkup([
    ["⚪ Juda oson"],
    ["🟢 Oson"],
    ["🟡 O'rta"],
    ["🔴 Qiyin"],
    ["🔥 Juda qiyin"],
    ["🔙 Orqaga"],
], resize_keyboard=True)

mus_menu = ReplyKeyboardMarkup([
    ["🧠 IQ TEST", "🧩 MANTIQ"],
    ["🎲 ARALASH TEST"],
    ["🔙 Orqaga"],
], resize_keyboard=True)

admin_menu = ReplyKeyboardMarkup([
    ["👥 Foydalanuvchilar", "📊 Statistika"],
    ["📢 Reklama",          "👑 Premium ber"],
    ["💎 VIP ber",          "🔄 Limit tiklash"],
    ["⚔️ Musobaqa boshqar", "📈 Analytics"],
    ["🔙 Asosiy menyu"],
], resize_keyboard=True)

# ═══════════════════════════════════════════
# /start — REFERAL TO'G'RI ISHLAYDI
# ═══════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user  = update.effective_user
    uid   = user.id
    uname = user.username or ""

    # ensure_user True qaytarsa — yangi foydalanuvchi
    is_new = ensure_user(uid, user.first_name, uname)
    context.user_data["holat"] = None

    # Referal — faqat yangi foydalanuvchi uchun
    if is_new and context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id != uid:
                # Referal egasi mavjudmi?
                ref_user = get_user(ref_id)
                if ref_user:
                    # Yangi foydalanuvchiga ref_by yozish
                    cur.execute(
                        "UPDATE users SET ref_by=? WHERE user_id=?",
                        (ref_id, uid)
                    )
                    # Referal egasiga ball berish
                    cur.execute(
                        "UPDATE users SET referals=referals+1, score=score+10 WHERE user_id=?",
                        (ref_id,)
                    )
                    db.commit()
                    # Referal egasining darajasini yangilash
                    cur.execute("SELECT score FROM users WHERE user_id=?", (ref_id,))
                    ref_score = cur.fetchone()[0]
                    upd_daraja(ref_id, ref_score)
                    # Referal egasiga xabar
                    try:
                        await context.bot.send_message(
                            chat_id=ref_id,
                            text=(
                                f"🎉 Referal bonus!\n\n"
                                f"👤 {user.first_name} sizning havolangiz orqali qo'shildi!\n"
                                f"🏆 +10 ball sizga berildi!"
                            )
                        )
                    except Exception:
                        pass
        except (ValueError, TypeError):
            pass

    # Foydalanuvchi ma'lumotlari
    cur.execute("SELECT COUNT(*) FROM users")
    jami = cur.fetchone()[0]

    cur.execute("SELECT daraja, score, premium, vip FROM users WHERE user_id=?", (uid,))
    row    = cur.fetchone()
    daraja = row[0] if row else "🥚 Tuxum"
    score  = row[1] if row else 0
    badge  = "💎 VIP" if (row and row[3]) else ("⭐ Premium" if (row and row[2]) else "🆓 Erkin")

    await update.message.reply_text(
        f"╔══════════════════╗\n"
        f"║   🔥 IQ BOT PRO  ║\n"
        f"╚══════════════════╝\n\n"
        f"👥 O'yinchilar: {jami} ta\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Salom, {user.first_name}!\n"
        f"🎖 Daraja:  {daraja}\n"
        f"🏆 Ball:    {score}\n"
        f"💳 Tarif:   {badge}\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 Menyudan tanlang:",
        reply_markup=main_menu
    )

# ═══════════════════════════════════════════
# SAVOL YUBORISH
# ═══════════════════════════════════════════
async def send_question(message, context):
    qs  = context.user_data.get("questions", [])
    idx = context.user_data.get("q_idx", 0)

    if idx >= len(qs):
        correct = context.user_data.get("s_correct", 0)
        wrong   = context.user_data.get("s_wrong",   0)
        ball    = context.user_data.get("s_ball",    0)
        total   = correct + wrong
        rejim   = context.user_data.get("rejim", "oddiy")

        foiz = round(correct / total * 100) if total > 0 else 0
        if foiz == 100:   baho = "🏆 MUKAMMAL!"
        elif foiz >= 80:  baho = "🌟 Ajoyib!"
        elif foiz >= 60:  baho = "👍 Yaxshi!"
        elif foiz >= 40:  baho = "💪 Harakat qiling!"
        else:              baho = "📚 Ko'proq mashq qiling!"

        xulosa = (
            f"╔══════════════════╗\n"
            f"║   🏁 TEST TUGADI ║\n"
            f"╚══════════════════╝\n\n"
            f"✅ To'g'ri:  {correct} ta\n"
            f"❌ Xato:     {wrong} ta\n"
            f"📝 Jami:     {total} ta\n"
            f"🏆 Ball:     +{ball}\n"
            f"🎯 Natija:   {foiz}%\n\n"
            f"{baho}"
        )

        if rejim == "musobaqa":
            m_uid  = context.user_data.get("m_uid")
            m_name = context.user_data.get("m_name", "Nomsiz")
            vaqt   = time.time() - context.user_data.get("m_start", time.time())
            cur.execute("""
                INSERT INTO musobaqa (user_id, name, correct, wrong, vaqt)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    correct = correct + excluded.correct,
                    wrong   = wrong   + excluded.wrong,
                    vaqt    = vaqt    + excluded.vaqt
            """, (m_uid, m_name, correct, wrong, vaqt))
            db.commit()
            xulosa += "\n\n✅ Musobaqa natijangiz saqlandi!"

        context.user_data.update({
            "s_correct": 0, "s_wrong": 0,
            "s_ball": 0, "rejim": "oddiy"
        })
        await message.reply_text(xulosa, reply_markup=main_menu)
        return

    q     = qs[idx]
    lv    = q.get("daraja", "oson")
    emoji = DARAJA_EMOJI.get(lv, "")
    ball  = BALL_JADVAL.get(lv, 1)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"  {opt}  ", callback_data=f"ans|{opt}")]
        for opt in q["options"]
    ])

    await message.reply_text(
        f"📌 SAVOL {idx+1}/{len(qs)}  {emoji}  +{ball} ball\n"
        f"{'─' * 24}\n\n"
        f"{q['question']}\n\n"
        f"{'─' * 24}\n"
        f"👇 Javobni tanlang:",
        reply_markup=keyboard
    )

# ═══════════════════════════════════════════
# TEST BOSHLASH
# ═══════════════════════════════════════════
async def start_test(update, context, qs, title, rejim="oddiy"):
    if not qs:
        await update.message.reply_text(
            "⚠️ Savollar topilmadi!\n"
            "Avval: py generate_questions.py"
        )
        return
    n = min(20, len(qs))
    context.user_data.update({
        "questions": random.sample(qs, n),
        "q_idx": 0, "s_correct": 0,
        "s_wrong": 0, "s_ball": 0,
        "rejim": rejim, "holat": "test"
    })
    if rejim == "musobaqa":
        context.user_data.update({
            "m_start": time.time(),
            "m_uid":   update.effective_user.id,
            "m_name":  update.effective_user.first_name
        })
    await update.message.reply_text(
        f"🚀 {title} BOSHLANDI!\n\n"
        f"📝 Savollar soni: {n} ta\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚪ Juda oson:  +1 ball\n"
        f"🟢 Oson:       +1 ball\n"
        f"🟡 O'rta:      +2 ball\n"
        f"🔴 Qiyin:      +3 ball\n"
        f"🔥 Juda qiyin: +4 ball\n"
        f"🎭 Topishmoq:  +3 ball\n"
        f"❌ Xato:       -1 ball\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🍀 Omad!"
    )
    await send_question(update.message, context)

# ═══════════════════════════════════════════
# CALLBACK — JAVOB
# ═══════════════════════════════════════════
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("ans|"):
        return

    selected = query.data[4:]
    uid      = query.from_user.id

    cur.execute(
        "SELECT premium, vip, daily_answers FROM users WHERE user_id=?", (uid,)
    )
    row = cur.fetchone()
    if not row:
        await query.message.reply_text("⚠️ Avval /start bosing.")
        return

    premium, vip, daily = row
    limit = 9999 if vip else (200 if premium else 50)

    if daily >= limit:
        await query.message.reply_text(
            "🚫 Kunlik limit tugadi!\n\n"
            "🆓 Erkin:   50 ta/kun\n"
            "⭐ Premium: 200 ta/kun\n"
            "💎 VIP:     ♾️ Cheksiz\n\n"
            "Menyudan 💎 PREMIUM ni tanlang."
        )
        return

    qs  = context.user_data.get("questions", [])
    idx = context.user_data.get("q_idx", 0)
    if idx >= len(qs):
        return

    q       = qs[idx]
    correct = q["answer"]
    lv      = q.get("daraja", "oson")
    ball    = BALL_JADVAL.get(lv, 1)

    cur.execute(
        "UPDATE users SET daily_answers=daily_answers+1 WHERE user_id=?", (uid,)
    )
    db.commit()

    if selected == correct:
        cur.execute(
            "UPDATE users SET score=score+?, correct=correct+1 WHERE user_id=?",
            (ball, uid)
        )
        db.commit()
        context.user_data["s_correct"] = context.user_data.get("s_correct", 0) + 1
        context.user_data["s_ball"]    = context.user_data.get("s_ball", 0) + ball

        cur.execute("SELECT score FROM users WHERE user_id=?", (uid,))
        new_score = cur.fetchone()[0]
        upd_daraja(uid, new_score)

        cur.execute("SELECT COUNT(*) FROM users WHERE score > ?", (new_score,))
        rank = cur.fetchone()[0] + 1
        rank_t = f"\n🏅 Reytingda: #{rank}" if rank <= 10 else ""

        await query.message.reply_text(
            f"✅ TO'G'RI! +{ball} ball 🎉{rank_t}"
        )
    else:
        cur.execute("SELECT score FROM users WHERE user_id=?", (uid,))
        cur_score = cur.fetchone()[0]
        new_score = max(0, cur_score - 1)
        cur.execute(
            "UPDATE users SET score=?, wrong=wrong+1 WHERE user_id=?",
            (new_score, uid)
        )
        db.commit()
        context.user_data["s_wrong"] = context.user_data.get("s_wrong", 0) + 1
        context.user_data["s_ball"]  = max(0, context.user_data.get("s_ball", 0) - 1)
        upd_daraja(uid, new_score)

        await query.message.reply_text(
            f"❌ XATO! -1 ball\n"
            f"✔️ To'g'ri javob: {correct}"
        )

    context.user_data["q_idx"] = idx + 1
    await send_question(query.message, context)

# ═══════════════════════════════════════════
# COPY REF CALLBACK
# ═══════════════════════════════════════════
async def copy_ref_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("copy_ref|"):
        uid = query.data.split("|")[1]
        havola = f"https://t.me/{BOT_USERNAME}?start={uid}"
        await query.message.reply_text(
            f"🔗 Sizning referal havolangiz:\n\n"
            f"{havola}\n\n"
            f"📋 Yuqoridagi havolani nusxalab do'stlaringizga yuboring!\n"
            f"Har yangi a'zo uchun +10 ball olasiz! 🎁"
        )

# ═══════════════════════════════════════════
# FOYDALANUVCHI TEXT HANDLER
# ═══════════════════════════════════════════
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text  = update.message.text
    uid   = update.effective_user.id
    user  = update.effective_user
    holat = context.user_data.get("holat")

    ensure_user(uid, user.first_name, user.username or "")

    # ── DARAJA TANLASH ──
    if holat == "daraja_tanla":
        tur  = context.user_data.get("test_tur", "iq")
        dmap = {
            "⚪ Juda oson":  "juda_oson",
            "🟢 Oson":       "oson",
            "🟡 O'rta":      "orta",
            "🔴 Qiyin":      "qiyin",
            "🔥 Juda qiyin": "juda_qiyin",
        }
        if text in dmap:
            lv = dmap[text]
            if tur == "iq":
                ql, t = filter_level(iq_all, lv), f"IQ TEST | {text}"
            elif tur == "logic":
                ql, t = filter_level(logic_all, lv), f"MANTIQ | {text}"
            else:
                ql, t = filter_level(iq_all + logic_all, lv), f"ARALASH | {text}"
            context.user_data["holat"] = None
            await start_test(update, context, ql, t)
            return
        elif text == "🔙 Orqaga":
            context.user_data["holat"] = None
            await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_menu)
            return

    # ── MUSOBAQA TEST TANLASH ──
    if holat == "mus_test_tanla":
        if text == "🧠 IQ TEST":
            ql, t = iq_all, "⚔️ MUSOBAQA — IQ TEST"
        elif text == "🧩 MANTIQ":
            ql, t = logic_all, "⚔️ MUSOBAQA — MANTIQ"
        elif text == "🎲 ARALASH TEST":
            ql, t = iq_all + logic_all, "⚔️ MUSOBAQA — ARALASH"
        elif text == "🔙 Orqaga":
            context.user_data["holat"] = None
            await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_menu)
            return
        else:
            ql = None
        if ql is not None:
            context.user_data["holat"] = None
            await start_test(update, context, ql, t, rejim="musobaqa")
            return

    # ── ASOSIY MENYU ──

    if text == "🧠 IQ TEST":
        context.user_data.update({"holat": "daraja_tanla", "test_tur": "iq"})
        await update.message.reply_text(
            "🧠 IQ TEST\n\nSavol qiyinligini tanlang:",
            reply_markup=daraja_menu
        )

    elif text == "🧩 MANTIQ":
        context.user_data.update({"holat": "daraja_tanla", "test_tur": "logic"})
        await update.message.reply_text(
            "🧩 MANTIQ TESTI\n\nSavol qiyinligini tanlang:",
            reply_markup=daraja_menu
        )

    elif text == "🎲 ARALASH":
        context.user_data.update({"holat": "daraja_tanla", "test_tur": "aralash"})
        await update.message.reply_text(
            "🎲 ARALASH TEST\n\nSavol qiyinligini tanlang:",
            reply_markup=daraja_menu
        )

    elif text == "🎭 TOPISHMOQ":
        if not topishmoq_all:
            await update.message.reply_text("⚠️ Topishmoqlar topilmadi!")
            return
        await start_test(update, context, topishmoq_all, "🎭 TOPISHMOQ")

    elif text == "📊 STATISTIKA":
        cur.execute(
            "SELECT score,correct,wrong,daily_answers,premium,vip,daraja,referals "
            "FROM users WHERE user_id=?", (uid,)
        )
        r = cur.fetchone()
        if not r:
            await update.message.reply_text("⚠️ /start bosing.")
            return
        score, correct, wrong, daily, premium, vip, daraja, refs = r
        total = correct + wrong
        foiz  = round(correct / total * 100) if total > 0 else 0
        badge = "💎 VIP" if vip else ("⭐ Premium" if premium else "🆓 Erkin")
        limit = "♾️" if vip else (f"{daily}/200" if premium else f"{daily}/50")

        await update.message.reply_text(
            f"╔══════════════════╗\n"
            f"║   📊 STATISTIKA  ║\n"
            f"╚══════════════════╝\n\n"
            f"👤 {user.first_name}\n"
            f"🎖 Daraja:    {daraja}\n"
            f"💳 Tarif:     {badge}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Ball:      {score}\n"
            f"✅ To'g'ri:   {correct}\n"
            f"❌ Xato:      {wrong}\n"
            f"📝 Jami:      {total}\n"
            f"🎯 Aniqlik:   {foiz}%\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 Bugun:     {limit}\n"
            f"👥 Referallar: {refs} ta"
        )

    elif text == "🏆 TOP-10":
        cur.execute(
            "SELECT name, score, daraja, vip, premium "
            "FROM users ORDER BY score DESC LIMIT 10"
        )
        rows = cur.fetchall()
        if not rows:
            await update.message.reply_text("📭 Hali hech kim yo'q.")
            return
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        out = "╔══════════════════╗\n║   🏆 TOP-10      ║\n╚══════════════════╝\n\n"
        for i, (name, score, daraja, v, p) in enumerate(rows):
            badge = " 💎" if v else (" ⭐" if p else "")
            out += f"{medals[i]} {name}{badge}\n   🏆 {score} ball  {daraja}\n\n"
        await update.message.reply_text(out)

    elif text == "👤 PROFIL":
        cur.execute(
            "SELECT name,score,correct,wrong,premium,vip,daraja,"
            "daily_answers,referals,joined_at FROM users WHERE user_id=?", (uid,)
        )
        r = cur.fetchone()
        if not r:
            await update.message.reply_text("⚠️ /start bosing.")
            return
        name, score, correct, wrong, prem, vip, daraja, daily, refs, joined = r
        total = correct + wrong
        foiz  = round(correct / total * 100) if total > 0 else 0
        badge = "💎 VIP" if vip else ("⭐ Premium" if prem else "🆓 Erkin")
        kd    = keyingi_daraja(score)
        kd_t  = f"📈 Keyingi: {kd['nom']} ({kd['min']} ball)" if kd else "🏆 MAX DARAJA!"

        cur.execute("SELECT COUNT(*) FROM users WHERE score > ?", (score,))
        rank = cur.fetchone()[0] + 1

        profil_xabar = f"🧠 IQ Test botiga qo'shiling!\nIQ test, mantiq va topishmoqlar bor 👇\nhttps://t.me/{BOT_USERNAME}?start={uid}"

        profil_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📤 Do'stlarga yuborish",
                switch_inline_query=profil_xabar
            )],
        ])

        await update.message.reply_text(
            f"╔══════════════════╗\n"
            f"║     👤 PROFIL    ║\n"
            f"╚══════════════════╝\n\n"
            f"👤 Ism:       {name}\n"
            f"🆔 ID:        {uid}\n"
            f"📅 Sana:      {joined}\n"
            f"💳 Tarif:     {badge}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎖 Daraja:    {daraja}\n"
            f"🏅 Reyting:   #{rank}\n"
            f"🏆 Ball:      {score}\n"
            f"✅ To'g'ri:   {correct}\n"
            f"❌ Xato:      {wrong}\n"
            f"🎯 Aniqlik:   {foiz}%\n"
            f"👥 Referallar: {refs} ta\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{kd_t}",
            reply_markup=profil_kb
        )

    elif text == "🎖 DARAJALAR":
        out = "╔══════════════════╗\n║   🎖 DARAJALAR   ║\n╚══════════════════╝\n\n"
        for d in DARAJALAR:
            out += f"{d['nom']}:  {d['min']} – {d['max']} ball\n"
        out += (
            "\n━━━━━━━━━━━━━━━━━━\n"
            "⚪ Juda oson:  +1 ball\n"
            "🟢 Oson:       +1 ball\n"
            "🟡 O'rta:      +2 ball\n"
            "🔴 Qiyin:      +3 ball\n"
            "🔥 Juda qiyin: +4 ball\n"
            "🎭 Topishmoq:  +3 ball\n"
            "❌ Xato:       -1 ball\n"
            "👥 Referal:    +10 ball"
        )
        await update.message.reply_text(out)

    elif text == "💎 PREMIUM":
        cur.execute("SELECT premium, vip FROM users WHERE user_id=?", (uid,))
        r = cur.fetchone()
        if r and r[1]:
            await update.message.reply_text(
                "╔══════════════════╗\n"
                "║    💎 VIP        ║\n"
                "╚══════════════════╝\n\n"
                "Siz VIP foydalanuvchisiz!\n\n"
                "✅ Cheksiz savollar\n"
                "✅ Barcha imkoniyatlar"
            )
        elif r and r[0]:
            await update.message.reply_text(
                "╔══════════════════╗\n"
                "║   ⭐ PREMIUM     ║\n"
                "╚══════════════════╝\n\n"
                "Siz PREMIUM foydalanuvchisiz!\n\n"
                "✅ 200 ta savol/kun\n"
                "✅ Maxsus belgi\n\n"
                "💎 VIP ga o'tish uchun admin bilan bog'laning."
            )
        else:
            await update.message.reply_text(
                "╔══════════════════╗\n"
                "║    💎 PREMIUM    ║\n"
                "╚══════════════════╝\n\n"
                "🆓 Erkin:   50 savol/kun\n"
                "⭐ Premium: 200 savol/kun\n"
                "💎 VIP:     ♾️ Cheksiz\n\n"
                "⭐ Premium imkoniyatlari:\n"
                "✅ Ko'proq savol\n"
                "✅ ⭐ Maxsus belgi\n\n"
                "💎 VIP imkoniyatlari:\n"
                "✅ Cheksiz savollar\n"
                "✅ 💎 VIP belgi\n"
                "✅ Musobaqa ustunligi\n\n"
                "📩 Admin bilan bog'laning!"
            )

    elif text == "👥 REFERAL":
        cur.execute("SELECT referals FROM users WHERE user_id=?", (uid,))
        r = cur.fetchone()
        refs = r[0] if r else 0

        qoldi_prem = max(0, 20 - refs)
        if refs >= 20:
            prem_text = "🎉 Siz 20 ta referal to'pladingiz!\n⭐ Premium sovg'a uchun adminga murojaat qiling!"
        else:
            prem_text = f"🎁 Premium olish uchun yana {qoldi_prem} ta odam taklif qiling!"

        filled = min(refs, 20)
        bar = "🟩" * filled + "⬜" * (20 - filled)
        havola = f"https://t.me/{BOT_USERNAME}?start={uid}"

        xabar = f"🧠 IQ Test botiga qo'shiling!\n\nIQ test, mantiq va topishmoqlar bor. Sinab ko'ring 👇\nhttps://t.me/{BOT_USERNAME}?start={uid}"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📤 Do'stlarga yuborish",
                switch_inline_query=xabar
            )],
            [InlineKeyboardButton(
                "🔗 Havolani nusxalash",
                callback_data=f"copy_ref|{uid}"
            )],
        ])

        await update.message.reply_text(
            f"╔══════════════════╗\n"
            f"║   👥 REFERAL     ║\n"
            f"╚══════════════════╝\n\n"
            f"🔗 Sizning havolangiz:\n"
            f"{havola}\n\n"
            f"👥 Taklif qilganlar: {refs} ta\n"
            f"🏆 Referal ball:     {refs * 10}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Premium yo'li: {refs}/20\n"
            f"{bar}\n"
            f"{prem_text}\n\n"
            f"📌 Har yangi a'zo uchun +10 ball!\n"
            f"👇 Quyidagi tugmani bosib havolangizni ulashing:",
            reply_markup=kb
        )

    elif text == "⚔️ MUSOBAQA":
        if not musobaqa_faol():
            await update.message.reply_text(
                "⚔️ MUSOBAQA\n\n"
                "⏳ Hozir faol musobaqa yo'q.\n\n"
                "Musobaqa har oyda bir marta o'tkaziladi.\n"
                "Yaqin musobaqa haqida xabar beramiz! 🔔"
            )
            return
        cur.execute("SELECT tugash FROM musobaqa_holati WHERE id=1")
        tugash = cur.fetchone()[0]
        qoldi  = max(0, int(tugash - time.time()))
        soat   = qoldi // 3600
        daqiqa = (qoldi % 3600) // 60

        context.user_data["holat"] = "mus_test_tanla"
        await update.message.reply_text(
            f"⚔️ MUSOBAQA DAVOM ETMOQDA!\n\n"
            f"⏱ Qolgan vaqt: {soat} soat {daqiqa} daqiqa\n\n"
            f"🥇 1-o'rin: 💎 PREMIUM\n"
            f"🥈 2-o'rin: ⭐ Maxsus belgi\n"
            f"🥉 3-o'rin: +50 ball\n"
            f"4️⃣-🔟 o'rin: 🎁 Maxsus sovga\n\n"
            f"Test turini tanlang:",
            reply_markup=mus_menu
        )

    elif text == "🔙 Orqaga":
        context.user_data["holat"] = None
        await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_menu)

    else:
        await update.message.reply_text("Menyudan tanlang 👇", reply_markup=main_menu)

# ═══════════════════════════════════════════
# ADMIN TEXT HANDLER
# ═══════════════════════════════════════════
async def admin_texts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    text  = update.message.text
    uid   = update.effective_user.id
    holat = context.user_data.get("holat")

    if not is_admin(uid):
        return False

    # Reklama matni kutilmoqda
    if holat == "reklama_yoz":
        if text == "🔙 Asosiy menyu":
            context.user_data["holat"] = None
            await update.message.reply_text("Bekor qilindi.", reply_markup=main_menu)
            return True
        cur.execute("SELECT user_id FROM users")
        all_uids = cur.fetchall()
        ok = 0
        for (u,) in all_uids:
            try:
                await context.bot.send_message(chat_id=u, text=f"📢 XABAR\n\n{text}")
                ok += 1
            except Exception:
                pass
        context.user_data["holat"] = None
        await update.message.reply_text(
            f"✅ {ok} ta foydalanuvchiga yuborildi!", reply_markup=admin_menu
        )
        return True

    # Premium berish
    if holat == "premium_ber":
        if text == "🔙 Asosiy menyu":
            context.user_data["holat"] = None
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_menu)
            return True
        try:
            tid = int(text.strip())
            cur.execute("UPDATE users SET premium=1 WHERE user_id=?", (tid,))
            db.commit()
            cur.execute("SELECT name FROM users WHERE user_id=?", (tid,))
            r = cur.fetchone()
            nm = r[0] if r else str(tid)
            await update.message.reply_text(
                f"✅ {nm} ga ⭐ Premium berildi!", reply_markup=admin_menu
            )
            try:
                await context.bot.send_message(
                    chat_id=tid,
                    text="🎉 Sizga ⭐ PREMIUM berildi!\n200 ta/kun savol ishlashingiz mumkin!"
                )
            except Exception:
                pass
        except (ValueError, TypeError):
            await update.message.reply_text("❗ Raqam (user_id) yozing.", reply_markup=admin_menu)
        context.user_data["holat"] = None
        return True

    # VIP berish
    if holat == "vip_ber":
        if text == "🔙 Asosiy menyu":
            context.user_data["holat"] = None
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_menu)
            return True
        try:
            tid = int(text.strip())
            cur.execute("UPDATE users SET vip=1, premium=1 WHERE user_id=?", (tid,))
            db.commit()
            cur.execute("SELECT name FROM users WHERE user_id=?", (tid,))
            r = cur.fetchone()
            nm = r[0] if r else str(tid)
            await update.message.reply_text(
                f"✅ {nm} ga 💎 VIP berildi!", reply_markup=admin_menu
            )
            try:
                await context.bot.send_message(
                    chat_id=tid,
                    text="🎉 Sizga 💎 VIP berildi!\n♾️ Cheksiz savollardan foydalaning!"
                )
            except Exception:
                pass
        except (ValueError, TypeError):
            await update.message.reply_text("❗ Raqam (user_id) yozing.", reply_markup=admin_menu)
        context.user_data["holat"] = None
        return True

    # Musobaqa muddati
    if holat == "mus_muddat":
        if text == "🔙 Asosiy menyu":
            context.user_data["holat"] = None
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_menu)
            return True
        try:
            soat   = int(text.strip())
            tugash = time.time() + soat * 3600
            cur.execute(
                "UPDATE musobaqa_holati SET faol=1, tugash=? WHERE id=1", (tugash,)
            )
            cur.execute("DELETE FROM musobaqa")
            db.commit()
            context.user_data["holat"] = None
            await update.message.reply_text(
                f"✅ Musobaqa {soat} soatga boshlandi!", reply_markup=admin_menu
            )
        except (ValueError, TypeError):
            await update.message.reply_text(
                "❗ Soat raqamini yozing (masalan: 24)", reply_markup=admin_menu
            )
        return True

    # Admin menyu tugmalari
    if text == "👥 Foydalanuvchilar":
        cur.execute("SELECT COUNT(*) FROM users")
        jami = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE vip=1")
        vip_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE premium=1 AND vip=0")
        prem_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE daily_answers > 0")
        faol = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM users WHERE joined_at=?",
            (datetime.now().strftime("%Y-%m-%d"),)
        )
        bugun = cur.fetchone()[0]
        await update.message.reply_text(
            f"╔══════════════════╗\n"
            f"║   👥 A'ZOLAR     ║\n"
            f"╚══════════════════╝\n\n"
            f"📊 Jami:            {jami} ta\n"
            f"💎 VIP:             {vip_cnt} ta\n"
            f"⭐ Premium:         {prem_cnt} ta\n"
            f"🆓 Erkin:           {jami - vip_cnt - prem_cnt} ta\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔥 Bugun faol:      {faol} ta\n"
            f"🆕 Bugun qo'shildi: {bugun} ta",
            reply_markup=admin_menu
        )
        return True

    elif text == "📊 Statistika":
        cur.execute("SELECT COUNT(*) FROM users")
        jami = cur.fetchone()[0]
        cur.execute("SELECT SUM(correct), SUM(wrong), SUM(score), SUM(referals) FROM users")
        r = cur.fetchone()
        c, w, s, refs = r[0] or 0, r[1] or 0, r[2] or 0, r[3] or 0
        cur.execute("SELECT name, score FROM users ORDER BY score DESC LIMIT 1")
        top = cur.fetchone()
        top_t = f"{top[0]} ({top[1]} ball)" if top else "Hali yo'q"
        await update.message.reply_text(
            f"╔══════════════════╗\n"
            f"║   📊 STATISTIKA  ║\n"
            f"╚══════════════════╝\n\n"
            f"👥 Foydalanuvchi:  {jami}\n"
            f"✅ Jami to'g'ri:   {c}\n"
            f"❌ Jami xato:      {w}\n"
            f"🏆 Jami ball:      {s}\n"
            f"👥 Jami referal:   {refs}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👑 Lider: {top_t}",
            reply_markup=admin_menu
        )
        return True

    elif text == "📈 Analytics":
        cur.execute(
            "SELECT daraja, COUNT(*) FROM users GROUP BY daraja ORDER BY COUNT(*) DESC"
        )
        rows = cur.fetchall()
        out = "📈 DARAJA BO'YICHA\n━━━━━━━━━━━━━━━━\n\n"
        for daraja, cnt in rows:
            out += f"{daraja}: {cnt} ta\n"
        await update.message.reply_text(out, reply_markup=admin_menu)
        return True

    elif text == "📢 Reklama":
        context.user_data["holat"] = "reklama_yoz"
        await update.message.reply_text(
            "📢 Reklama matnini yozing:\n\n"
            "Bekor qilish: 🔙 Asosiy menyu"
        )
        return True

    elif text == "👑 Premium ber":
        context.user_data["holat"] = "premium_ber"
        await update.message.reply_text(
            "👑 Premium bermoqchi bo'lgan foydalanuvchi ID sini yozing:\n\n"
            "Bekor qilish: 🔙 Asosiy menyu"
        )
        return True

    elif text == "💎 VIP ber":
        context.user_data["holat"] = "vip_ber"
        await update.message.reply_text(
            "💎 VIP bermoqchi bo'lgan foydalanuvchi ID sini yozing:\n\n"
            "Bekor qilish: 🔙 Asosiy menyu"
        )
        return True

    elif text == "🔄 Limit tiklash":
        cur.execute("UPDATE users SET daily_answers=0")
        db.commit()
        await update.message.reply_text("✅ Barcha limitlar tiklandi!", reply_markup=admin_menu)
        return True

    elif text == "⚔️ Musobaqa boshqar":
        cur.execute("SELECT faol, tugash FROM musobaqa_holati WHERE id=1")
        row    = cur.fetchone()
        faol_t = "🟢 FAOL" if (row and row[0]) else "🔴 FAOL EMAS"
        qoldi_t = ""
        if row and row[0] and row[1] > 0:
            q      = max(0, int(row[1] - time.time()))
            qoldi_t = f"\n⏱ Qolgan: {q//3600} soat {(q%3600)//60} daqiqa"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Boshlash", callback_data="adm|mus_start"),
             InlineKeyboardButton("⏹ Tugatish",  callback_data="adm|mus_stop")],
            [InlineKeyboardButton("📊 Natijalar", callback_data="adm|mus_natija")],
        ])
        await update.message.reply_text(
            f"⚔️ MUSOBAQA BOSHQARUVI\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Holat: {faol_t}{qoldi_t}",
            reply_markup=kb
        )
        return True

    elif text == "🔙 Asosiy menyu":
        context.user_data["holat"] = None
        await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_menu)
        return True

    return False

# ═══════════════════════════════════════════
# ADMIN CALLBACK
# ═══════════════════════════════════════════
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("adm|"):
        return False
    if not is_admin(query.from_user.id):
        return True
    action = query.data[4:]

    if action == "mus_start":
        context.user_data["holat"] = "mus_muddat"
        await query.message.reply_text(
            "⏱ Musobaqa necha soat davom etsin?\n"
            "Raqam yozing (masalan: 24 yoki 48):"
        )

    elif action == "mus_stop":
        cur.execute("UPDATE musobaqa_holati SET faol=0, tugash=0 WHERE id=1")
        db.commit()
        cur.execute(
            "SELECT user_id, name, correct, wrong, vaqt "
            "FROM musobaqa ORDER BY correct DESC, vaqt ASC LIMIT 10"
        )
        rows    = cur.fetchall()
        medals  = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        sovgalar = [
            "💎 PREMIUM", "⭐ Maxsus belgi", "+50 ball",
            "🎁 Sovga", "🎁 Sovga", "🎁 Sovga",
            "🎁 Sovga", "🎁 Sovga", "🎁 Sovga", "🎁 Sovga"
        ]
        natija = "⚔️ MUSOBAQA YAKUNLANDI!\n━━━━━━━━━━━━━━━━\n\n"
        for i, (uid, name, c, w, v) in enumerate(rows):
            d, s = int(v // 60), int(v % 60)
            natija += f"{medals[i]} {name}\n   ✅{c} to'g'ri | ⏱{d}:{s:02d} | {sovgalar[i]}\n\n"
        await query.message.reply_text(natija if rows else "Hech kim qatnashmadi.")
        for i, (uid, name, c, w, v) in enumerate(rows[:10]):
            try:
                if i == 0:
                    cur.execute("UPDATE users SET vip=1, premium=1 WHERE user_id=?", (uid,))
                    db.commit()
                    msg = f"🥇 1-o'rin! 💎 PREMIUM berildi! Tabriklaymiz {name}!"
                elif i == 1:
                    msg = f"🥈 2-o'rin! Tabriklaymiz {name}! ⭐ Maxsus belgi sizniki!"
                elif i == 2:
                    cur.execute("UPDATE users SET score=score+50 WHERE user_id=?", (uid,))
                    db.commit()
                    msg = f"🥉 3-o'rin! Tabriklaymiz {name}! +50 ball!"
                else:
                    msg = f"🏅 TOP-10 talikka kirdingiz! Tabriklaymiz {name}! 🎁"
                await context.bot.send_message(chat_id=uid, text=msg)
            except Exception:
                pass
        await query.message.reply_text("✅ G'oliblarga xabar yuborildi.")

    elif action == "mus_natija":
        cur.execute(
            "SELECT name, correct, wrong, vaqt "
            "FROM musobaqa ORDER BY correct DESC, vaqt ASC LIMIT 10"
        )
        rows = cur.fetchall()
        if not rows:
            await query.message.reply_text("Hali hech kim qatnashmagan.")
            return True
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        natija = "⚔️ JORIY NATIJALAR\n━━━━━━━━━━━━━━━━\n\n"
        for i, (name, c, w, v) in enumerate(rows):
            d, s = int(v // 60), int(v % 60)
            natija += f"{medals[i]} {name} — {c} to'g'ri | {d}:{s:02d}\n"
        await query.message.reply_text(natija)
    return True

# ═══════════════════════════════════════════
# ROUTERLAR
# ═══════════════════════════════════════════
async def texts_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        if await admin_texts(update, context):
            return
    await texts(update, context)

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data.startswith("adm|"):
        await admin_callback(update, context)
    elif data.startswith("copy_ref|"):
        await copy_ref_callback(update, context)
    else:
        await answer(update, context)

# ═══════════════════════════════════════════
# ADMIN COMMANDS
# ═══════════════════════════════════════════
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return
    ensure_user(update.effective_user.id, update.effective_user.first_name)
    cur.execute(
        "UPDATE users SET vip=1, premium=1 WHERE user_id=?",
        (update.effective_user.id,)
    )
    db.commit()
    await update.message.reply_text(
        "🔐 ADMIN PANEL\n━━━━━━━━━━━━━━━━\n\n"
        "Xush kelibsiz Admin!\n"
        "💎 Sizga VIP avtomatik berildi.",
        reply_markup=admin_menu
    )

# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("admin",      admin_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texts_router))
    app.add_handler(CallbackQueryHandler(callback_router))
    print("🔥 BOT ISHGA TUSHDI 🔥")
    app.run_polling()

if __name__ == "__main__":
    main()