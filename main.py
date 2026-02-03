#!/usr/bin/env python3
import os
import json
import tempfile
import traceback
import subprocess
from multiprocessing import Process, Queue
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = "8019013565:AAGKHWKAC6gMBFPSUNSCNsFY5Lzgj4Se8SM"
TIMEOUT = 60
MAX_OUTPUT = 40000
MEMORY_FILE = "clawd_memory.json"

# ================= MEMORY =================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(m):
    with open(MEMORY_FILE, "w") as f:
        json.dump(m, f, indent=2)

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
        parts = text.split(" ", 1)
        if len(parts) == 2:
            return ("exec", parts[1])
        return ("unknown", None)

    if t.startswith("!"):
        return ("system", t[1:])

    if "حالة" in t or "انت حي" in t:
        return ("auto", None)

    # كل شيء آخر يُعتبر محادثة طبيعية
    return ("chat", text)

# ================= EXECUTOR =================
def worker(code, q):
    try:
        if code["type"] == "system":
            r = subprocess.run(
                code["cmd"], shell=True, capture_output=True, text=True, timeout=TIMEOUT
            )
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            return

        if code["type"] == "python":
            path = tempfile.mktemp(suffix=".py")
            with open(path, "w") as f:
                f.write(code["cmd"])

            r = subprocess.run(
                ["python3", path], capture_output=True, text=True, timeout=TIMEOUT
            )
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            os.remove(path)

    except subprocess.TimeoutExpired:
        q.put("⏱ Timeout")
    except Exception:
        q.put(traceback.format_exc())

def run_exec(obj):
    q = Queue()
    p = Process(target=worker, args=(obj, q))
    p.start()
    p.join(TIMEOUT + 2)

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

    # --- محادثة طبيعية ---
    if action[0] == "chat":
        await update.message.reply_text("🤖 Clawd يقول: " + action[1])
        return

    # --- حفظ واسترجاع ---
    if action[0] == "remember" and action[1] and action[2]:
        memory[action[1]] = action[2]
        save_memory(memory)
        await update.message.reply_text("💾 تم الحفظ")
        return

    if action[0] == "recall" and action[1]:
        await update.message.reply_text(str(memory.get(action[1], "❌ غير موجود")))
        return

    # --- فحص الحالة ---
    if action[0] == "auto":
        await update.message.reply_text("🤖 Clawd يعمل بنجاح")
        return

    # --- تنفيذ الأوامر ---
    if action[0] == "exec":
        out = run_exec({"type": "system", "cmd": action[1]})
    elif action[0] == "python":
        out = run_exec({"type": "python", "cmd": action[1]})
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
    main()            return ("remember", parts[-2], parts[-1])
        return ("unknown", None)

    if "استرجع" in t or "اعرض" in t:
        parts = text.split()
        if len(parts) >= 2:
            return ("recall", parts[-1])
        return ("unknown", None)

    if t.startswith("نفذ") or t.startswith("شغل"):
        parts = text.split(" ", 1)
        if len(parts) == 2:
            return ("exec", parts[1])
        return ("unknown", None)

    if t.startswith("!"):
        return ("system", t[1:])

    if "حالة" in t or "انت حي" in t:
        return ("auto", None)

    # كل شيء آخر يُعتبر محادثة طبيعية
    return ("chat", text)

# ================= EXECUTOR =================
def worker(code, q):
    try:
        if code["type"] == "system":
            r = subprocess.run(
                code["cmd"], shell=True, capture_output=True, text=True, timeout=TIMEOUT
            )
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            return

        if code["type"] == "python":
            path = tempfile.mktemp(suffix=".py")
            with open(path, "w") as f:
                f.write(code["cmd"])

            r = subprocess.run(
                ["python3", path], capture_output=True, text=True, timeout=TIMEOUT
            )
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            os.remove(path)

    except subprocess.TimeoutExpired:
        q.put("⏱ Timeout")
    except Exception:
        q.put(traceback.format_exc())

def run_exec(obj):
    q = Queue()
    p = Process(target=worker, args=(obj, q))
    p.start()
    p.join(TIMEOUT + 2)

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

    # --- محادثة طبيعية ---
    if action[0] == "chat":
        await update.message.reply_text("🤖 Clawd يقول: " + action[1])
        return

    # --- حفظ واسترجاع ---
    if action[0] == "remember" and action[1] and action[2]:
        memory[action[1]] = action[2]
        save_memory(memory)
        await update.message.reply_text("💾 تم الحفظ")
        return

    if action[0] == "recall" and action[1]:
        await update.message.reply_text(str(memory.get(action[1], "❌ غير موجود")))
        return

    # --- فحص الحالة ---
    if action[0] == "auto":
        await update.message.reply_text("🤖 Clawd يعمل بنجاح")
        return

    # --- تنفيذ الأوامر ---
    if action[0] == "exec":
        out = run_exec({"type": "system", "cmd": action[1]})
    elif action[0] == "python":
        out = run_exec({"type": "python", "cmd": action[1]})
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
    main()            return

        if code["type"] == "python":
            path = tempfile.mktemp(suffix=".py")
            with open(path, "w") as f:
                f.write(code["cmd"])

            r = subprocess.run(
                ["python3", path], capture_output=True, text=True, timeout=TIMEOUT
            )
            q.put((r.stdout + r.stderr).strip() or "✅ Done")
            os.remove(path)

    except subprocess.TimeoutExpired:
        q.put("⏱ Timeout")
    except Exception:
        q.put(traceback.format_exc())

def run_exec(obj):
    q = Queue()
    p = Process(target=worker, args=(obj, q))
    p.start()
    p.join(TIMEOUT + 2)

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
        out = run_exec({"type": "system", "cmd": action[1]})
    elif action[0] == "python":
        out = run_exec({"type": "python", "cmd": action[1]})
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
    main()
