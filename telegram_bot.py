"""Bot de Telegram que reenvía preguntas a sci-bot.ru y devuelve la respuesta."""

import logging
import os
import tempfile
import time

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

from pdf_export import build_pdf
from scibot_client import SciBotError, ask_question, login

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
SCIBOT_USERNAME = os.environ["SCIBOT_USERNAME"]
SCIBOT_PASSWORD = os.environ["SCIBOT_PASSWORD"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text(
        "Hola! Envíame una pregunta y la mandaré a sci-bot.ru."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    question = update.message.text.strip()
    if not question:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        auth_cookie = login(SCIBOT_USERNAME, SCIBOT_PASSWORD)
        answer = await ask_question(auth_cookie, question)
    except SciBotError as e:
        logger.error("Error de sci-bot: %s", e)
        await update.message.reply_text(f"Error de sci-bot: {e}")
        return
    except Exception:
        logger.exception("Error inesperado")
        await update.message.reply_text("Ocurrió un error inesperado. Intenta de nuevo.")
        return

    if not answer:
        await update.message.reply_text("El bot no devolvió ninguna respuesta.")
        return

    pdf_path = os.path.join(tempfile.gettempdir(), f"scibot_{int(time.time() * 1000)}.pdf")
    try:
        build_pdf(question, answer, pdf_path)
        with open(pdf_path, "rb") as f:
            await update.message.reply_document(document=f, filename="respuesta.pdf")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def main() -> None:
    request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=60.0,
        pool_timeout=60.0,
        proxy="socks5://127.0.0.1:40000",
    )
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).get_updates_request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot iniciado. Esperando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("El bot se detuvo por un error")
