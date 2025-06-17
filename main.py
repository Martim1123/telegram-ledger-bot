from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from datetime import datetime
import os

ledger = []

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user.first_name
    timestamp = datetime.now().strftime('%H:%M:%S')
    today = datetime.now().strftime('%Y-%m-%d')

    if text.startswith('+') or text.startswith('-'):
        try:
            sign = 1 if text.startswith('+') else -1
            parts = text[1:].strip().split(' ', 1)
            amount = sign * float(parts[0])
            note = parts[1] if len(parts) > 1 else ''
            tx_type = 'in' if sign > 0 else 'out'
            ledger.append((today, timestamp, tx_type, abs(amount), note, user))

            await update.message.reply_text(
                f"{'📥 入帳成功' if tx_type == 'in' else '📤 下發成功'}\n"
                f"金額：{abs(amount)}\n備註：{note}"
            )
        except Exception:
            await update.message.reply_text("❌ 格式錯誤，請使用：+金額 備註 或 -金額 備註")
    else:
        await update.message.reply_text("❌ 格式錯誤，請使用：+金額 備註 或 -金額 備註")

async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime('%Y-%m-%d')
    ins = [x for x in ledger if x[0] == today and x[2] == 'in']
    outs = [x for x in ledger if x[0] == today and x[2] == 'out']
    total_in = sum(x[3] for x in ins)
    total_out = sum(x[3] for x in outs)
    remaining = total_in - total_out

    msg = "📊 今日報表\n"
    msg += f"\n今日入帳（{len(ins)}筆）\n"
    for x in ins:
        msg += f"{x[1]}　{x[3]:.2f}　{x[4]}\n"
    msg += f"\n今日下發（{len(outs)}筆）\n"
    for x in outs:
        msg += f"{x[1]}　{x[3]:.2f}　{x[4]}\n"
    msg += f"\n總入帳：{total_in:.2f}\n已下發：{total_out:.2f}\n餘額：{remaining:.2f}"

    await update.message.reply_text(msg)

if __name__ == '__main__':
    import asyncio

    async def main():
        app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))
        app.add_handler(CommandHandler("report", report_handler))
        await app.run_polling()

    asyncio.run(main())
