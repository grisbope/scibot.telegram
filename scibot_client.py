"""Cliente para sci-bot.ru: login por API REST y preguntas vía WebSocket."""

import asyncio
import json

import requests
import websockets

BASE_URL = "https://sci-bot.ru"
LOGIN_URL = f"{BASE_URL}/api/login"
WS_URL = "wss://sci-bot.ru/"

ANSWER_TIMEOUT = 180  # segundos máximos esperando una respuesta completa


class SciBotError(Exception):
    pass


def login(username: str, password: str) -> str:
    """Inicia sesión y devuelve la cookie de autenticación (scibot_auth)."""
    resp = requests.post(LOGIN_URL, json={"username": username, "password": password}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise SciBotError(data.get("error", "Login fallido"))

    cookie = resp.cookies.get("scibot_auth")
    if not cookie:
        raise SciBotError("No se recibió cookie de sesión (scibot_auth)")
    return cookie


async def ask_question(auth_cookie: str, question: str, lang: str = "es") -> str:
    """Envía una pregunta vía WebSocket y devuelve la respuesta completa concatenada."""
    headers = {"Cookie": f"scibot_auth={auth_cookie}"}

    async with websockets.connect(WS_URL, extra_headers=headers) as ws:
        await ws.send(json.dumps({
            "type": "chat",
            "message": question,
            "lang": lang,
            "popularScience": False,
        }))

        chunks = []
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=ANSWER_TIMEOUT)
            except asyncio.TimeoutError:
                raise SciBotError("Tiempo de espera agotado esperando respuesta del bot")

            try:
                evt = json.loads(raw)
            except json.JSONDecodeError:
                continue

            etype = evt.get("type")
            if etype == "content":
                chunks.append(evt.get("text", ""))
            elif etype == "error":
                raise SciBotError(evt.get("message") or evt.get("error") or "Error desconocido del bot")
            elif etype == "done":
                break

        return "".join(chunks).strip()
