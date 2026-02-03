#!/usr/bin/env python3
import os
import json
import tempfile
import traceback
import subprocess
from multiprocessing import Process, Queue
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================

BOT_TOKEN = "8019013565:AAGKHWKAC6gMBFPSUNSCNsFY5Lzgj4Se8SM"
TIMEOUT = 60
MAX_OUTPUT = 40000
MEMORY_FILE = "clawd_memory.json"

# ================= MEMORY =================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

memory = load_memory()

# ================= AI UNDERSTAND =================

def understand(text):
    t = text.lower()

    if "احفظ" in t or "تذكر" in t:
        parts = text.split()
        if len(parts) >= 3:
            return ("remember", parts[-2], parts[-1])
        return ("unknown",)

    if "استرجع" in t or "اعرض" in t:
        parts = text.split()
        if len(parts) >= 2:
            return ("recall", parts[-1])
        return ("unknown",)

    if t.startswith("نفذ"):
        return ("system", text[4:].strip())

    if t.startswith("!"):
        return ("system", text[1:].strip())

    if "حالة" in t:
        return ("status",)

    return ("chat", text)

# ================= EXECUTOR =================

def worker(task, q):
    try:
        if task["type"] == "system":
            r = subprocess.run(
                task["cmd"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

            output = (r.stdout + r.stderr).strip()
            q.put(output if output else "✅ تم التنفيذ")
            return

        if task["type"] == "python":
            path = tempfile.mktemp(suffix=".py")

            with open(path, "w", encoding="utf-8") as f:
                f.write(task["cmd"])

            r = subprocess.run(
                ["python3", path],
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

            output = (r.stdout + r.stderr).strip()
            q.put(output if output else "✅ تم التنفيذ")

            os.remove(path)

    except subprocess.TimeoutExpired:
        q.put("⏱ انتهى الوقت")
    except Exception:
        q.put(traceback.format_exc())

def run_exec(task):
    q = Queue()
    p = Process(target=worker, args=(task, q))
    p.start()
    p.join(TIMEOUT + 2)

    if p.is_alive():
        p.terminate()
        return "⏱ انتهى الوقت"

    return q.get() if not q.empty() else "❌ لا مخرجات"

# ================= TELEGRAM =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Clawd AI Agent\n\n"
        "تحدث طبيعي:\n"
        "مرحبًا كيف حالك؟\n\n"
        "أوامر:\n"
        "احفظ اسمي احمد\n"
        "استرجع اسمي\n"
        "نفذ ls\n"
        "!whoami\n"
        "print('hello')\n"
        "حالة"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    action = understand(msg)

    if action[0] == "chat":
        await update.message.reply_text("🤖 Clawd: " + msg)
        return

    if action[0] == "remember":
        memory[action[1]] = action[2]
        save_memory(memory)
        await update.message.reply_text("💾 تم الحفظ")
        return

    if action[0] == "recall":
        await update.message.reply_text(
            str(memory.get(action[1], "❌ غير موجود"))
        )
        return

    if action[0] == "status":
        await update.message.reply_text("✅ Clawd يعمل بنجاح")
        return

    if action[0] == "system":
        out = run_exec({"type": "system", "cmd": action[1]})
    else:
        out = run_exec({"type": "python", "cmd": msg})

    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + "\n...(تم القطع)"

    await update.message.reply_text("📤 " + out)

# ================= BOOT =================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
