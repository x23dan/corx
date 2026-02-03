#!/usr/bin/env python3
import os, json, tempfile, traceback, subprocess
from multiprocessing import Process, Queue
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = "8019013565:AAGKHWKAC6gMBFPSUNSCNsFY5Lzgj4Se8SM"  # ضع توكن بوت تيليغرام هنا
TIMEOUT = 60
MAX_OUTPUT = 40000
MEMORY_FILE = "clawd_memory.json"

# ================= MEMORY =================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {}

def save_memory(m):
    json.dump(m, open(MEMORY_FILE, "w"), indent=2)

memory = load_memory()

# ================= AI UNDERSTANDING =================
def understand(text):
    t = text.lower()

    if "احفظ" in t or "تذكر" in t:
        parts = text.split()
        if len(parts) >= 3:
            return ("remember", parts[-2], parts[-1])
        return ("unknown", None)

    if "استرجع" in t or "اعرض" in t:
        parts = text.split()
        if len(parts) >= 2:
            return ("recall", parts[-1])
        return ("unknown", None)

    if t.startswith("نفذ") or t.startswith("شغل"):
        parts = text.split(" ",1)
        if len(parts) == 2:
            return ("exec", parts[1])
        return ("unknown", None)

    if t.startswith("!"):
        return ("system", t[1:])

    if "حالة" in t or "انت حي" in t:
        return ("auto", None)

    return ("python", text)

# ================= EXECUTOR =================
def worker(code, q):
    try:
        if code["type"] == "system":
            r = subprocess.run(code["cmd"], shell=True, capture_output=True, text=True, timeout=TIMEOUT)
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            return

        if code["type"] == "python":
            # استخدم mktemp بدلاً من NamedTemporaryFile
            path = tempfile.mktemp(suffix=".py")
            with open(path, "w") as f:
                f.write(code["cmd"])

            r = subprocess.run(["python3", path], capture_output=True, text=True, timeout=TIMEOUT)
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            os.remove(path)

    except subprocess.TimeoutExpired:
        q.put("⏱ Timeout")
    except Exception:
        q.put(traceback.format_exc())

def run_exec(obj):
    q = Queue()
    p = Process(target=worker, args=(obj,q))
    p.start()
    p.join(TIMEOUT+2)

    if p.is_alive():
        p.terminate()
        return "⏱ Timeout"

    return q.get() if not q.empty() else "❌ No output"

# ================= TELEGRAM HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Clawd AI Smart Agent\n\n"
        "تكلّم طبيعي:\n"
        "احفظ اسمي احمد\n"
        "استرجع اسمي\n"
        "نفذ ls\n"
        "print('hello')\n"
        "!whoami\n"
        "حالة"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    action = understand(msg)

    if action[0] == "remember" and action[1] and action[2]:
        memory[action[1]] = action[2]
        save_memory(memory)
        await update.message.reply_text("💾 تم الحفظ")
        return

    if action[0] == "recall" and action[1]:
        await update.message.reply_text(str(memory.get(action[1], "❌ غير موجود")))
        return

    if action[0] == "auto":
        await update.message.reply_text("🤖 Clawd يعمل بنجاح")
        return

    if action[0] == "exec":
        out = run_exec({"type":"system","cmd":action[1]})
    elif action[0] == "python":
        out = run_exec({"type":"python","cmd":action[1]})
    else:
        out = "❌ لم أفهم الأمر"

    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + "\n...(cut)"

    await update.message.reply_text(f"📤 {out}")

# ================= BOOT =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()    if t.startswith("!"):
        return ("system", t[1:])

    if "حالة" in t or "انت حي" in t:
        return ("auto", None)

    return ("python", text)

# ================= EXEC =================
def worker(code, q):
    try:
        if code["type"] == "system":
            r = subprocess.run(code["cmd"], shell=True, capture_output=True, text=True, timeout=TIMEOUT)
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            return

        if code["type"] == "python":
            # استخدام mktemp لتجنب مشاكل NamedTemporaryFile
            path = tempfile.mktemp(suffix=".py")
            with open(path, "w") as f:
                f.write(code["cmd"])

            r = subprocess.run(["python3", path], capture_output=True, text=True, timeout=TIMEOUT)
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            os.remove(path)

    except subprocess.TimeoutExpired:
        q.put("⏱ Timeout")
    except Exception:
        q.put(traceback.format_exc())

def run_exec(obj):
    q = Queue()
    p = Process(target=worker, args=(obj,q))
    p.start()
    p.join(TIMEOUT+2)

    if p.is_alive():
        p.terminate()
        return "⏱ Timeout"

    return q.get() if not q.empty() else "❌ No output"

# ================= TELEGRAM =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Clawd AI Smart Agent\n\n"
        "تكلّم طبيعي:\n"
        "احفظ اسمي احمد\n"
        "استرجع اسمي\n"
        "نفذ ls\n"
        "print('hello')\n"
        "!whoami\n"
        "حالة"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    action = understand(msg)

    if action[0] == "remember":
        memory[action[1]] = action[2]
        save_memory(memory)
        await update.message.reply_text("💾 تم الحفظ")
        return

    if action[0] == "recall":
        await update.message.reply_text(str(memory.get(action[1], "❌ غير موجود")))
        return

    if action[0] == "auto":
        await update.message.reply_text("🤖 Clawd يعمل بنجاح")
        return

    if action[0] == "exec":
        out = run_exec({"type":"system","cmd":action[1]})
    elif action[0] == "python":
        out = run_exec({"type":"python","cmd":action[1]})

    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + "\n...(cut)"

    await update.message.reply_text(f"📤 {out}")

# ================= BOOT =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
def run_exec(obj):
    q = Queue()
    p = Process(target=worker, args=(obj,q))
    p.start()
    p.join(TIMEOUT+2)

    if p.is_alive():
        p.terminate()
        return "Timeout"

    return q.get() if not q.empty() else "No output"

# ================= TELEGRAM =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Clawd AI Smart Agent\n\n"
        "تكلّم طبيعي:\n"
        "احفظ اسمي احمد\n"
        "استرجع اسمي\n"
        "نفذ ls\n"
        "print('hello')"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    action = understand(msg)

    if action[0] == "remember":
        memory[action[1]] = action[2]
        save_memory(memory)
        await update.message.reply_text("💾 تم الحفظ")
        return

    if action[0] == "recall":
        await update.message.reply_text(str(memory.get(action[1], "غير موجود")))
        return

    if action[0] == "auto":
        await update.message.reply_text("🤖 Clawd يعمل بنجاح")
        return

    if action[0] == "exec":
        out = run_exec({"type":"system","cmd":action[1]})
    elif action[0] == "python":
        out = run_exec({"type":"python","cmd":action[1]})

    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT]

    await update.message.reply_text(f"📤 {out}")

# ================= BOOT =================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()        # ---------- PYTHON MODE ----------
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            path = f.name

        result = subprocess.run(
            ["python3", path],
            capture_output=True, text=True, timeout=CODE_TIMEOUT
        )
        output = (result.stdout or "") + (result.stderr or "")
        q.put(output.strip() or "✅ تم التنفيذ بدون مخرجات")

    except subprocess.TimeoutExpired:
        q.put("⏱️ انتهى وقت التنفيذ")
    except Exception:
        q.put("❌ خطأ أثناء التنفيذ:\n" + traceback.format_exc())
    finally:
        try:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        except:
            pass


def run_code(code: str) -> str:
    q = Queue()
    p = Process(target=worker, args=(code, q))
    p.start()
    p.join(CODE_TIMEOUT + 5)

    if p.is_alive():
        p.terminate()
        return "⏱️ انتهى وقت التنفيذ"

    try:
        return q.get()
    except:
        return "❌ فشل استرجاع المخرجات"


# ======================== TELEGRAM HANDLERS ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Execution Bot\n\n"
        "• Python: أرسل الكود مباشرة\n"
        "• Linux: ابدأ بـ !\n\n"
        "أمثلة:\n"
        "!ls -la\n"
        "!whoami\n\n"
        "/run → إعادة التنفيذ\n"
        "/clear → مسح الذاكرة"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🧹 تم مسح الذاكرة")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    if not code.strip():
        await update.message.reply_text("❌ لا يمكن تنفيذ رسالة فارغة")
        return

    context.user_data["last_code"] = code
    output = run_code(code)
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + "\n... (تم القطع)"
    await update.message.reply_text(f"📤 النتيجة:\n{output}")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        doc: Document = update.message.document
        if not doc.file_name.endswith(".py"):
            await update.message.reply_text("❌ فقط ملفات .py مسموح بها")
            return
        if doc.file_size > MAX_FILE_SIZE:
            await update.message.reply_text("❌ الملف كبير جدًا")
            return

        file = await doc.get_file()
        code_bytes = await file.download_as_bytearray()
        code = code_bytes.decode(errors="ignore")
        if not code.strip():
            await update.message.reply_text("❌ الملف فارغ")
            return

        context.user_data["last_code"] = code
        output = run_code(code)
        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + "\n... (تم القطع)"
        await update.message.reply_text(f"📤 النتيجة:\n{output}")

    except Exception:
        await update.message.reply_text("❌ فشل تحميل الملف أو تنفيذه:\n" + traceback.format_exc())


async def run_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = context.user_data.get("last_code")
    if not code:
        await update.message.reply_text("❌ لا يوجد كود محفوظ")
        return

    output = run_code(code)
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + "\n... (تم القطع)"
    await update.message.reply_text(f"🔁 إعادة التنفيذ:\n{output}")


# ======================== BOOT ========================

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN غير موجود")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("run", run_last))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.run_polling()


if __name__ == "__main__":
    main()
