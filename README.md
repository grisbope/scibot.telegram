# scibot.telegram

Bot de Telegram personal que reenvía preguntas a [sci-bot.ru](https://sci-bot.ru) y devuelve la respuesta como documento PDF.

## Qué hace

1. Recibes un mensaje de texto en Telegram.
2. El bot inicia sesión en sci-bot.ru con tus credenciales.
3. Envía la pregunta por WebSocket y espera la respuesta completa.
4. Genera un PDF con la pregunta y la respuesta, y te lo envía como archivo adjunto.

## Requisitos

- **Python 3.10+**
- Cuenta activa en [sci-bot.ru](https://sci-bot.ru)
- Token de bot de Telegram ([@BotFather](https://t.me/BotFather))
- **Windows** (la exportación PDF usa fuentes del sistema: `arial.ttf` / `arialbd.ttf`)
- Proxy SOCKS5 local en `127.0.0.1:40000` (configurado en el bot para la conexión con Telegram)

## Instalación

```bash
git clone https://github.com/grisbope/scibot.telegram.git
cd scibot.telegram

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate  # Linux / macOS

pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo y completa tus credenciales:

```bash
copy .env.example .env
```

| Variable | Descripción |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token del bot, obtenido desde BotFather |
| `SCIBOT_USERNAME` | Usuario de sci-bot.ru |
| `SCIBOT_PASSWORD` | Contraseña de sci-bot.ru |
| `ALLOWED_USER_ID` | ID numérico de Telegram del único usuario autorizado |

El archivo `.env` no se sube al repositorio. Nunca compartas tokens ni contraseñas.

### Acceso restringido

Solo responde al usuario cuyo ID coincide con `ALLOWED_USER_ID` en `.env`. Cualquier otro usuario es ignorado silenciosamente.

Puedes obtener tu ID con bots como [@userinfobot](https://t.me/userinfobot).

### Proxy de Telegram

El bot usa un proxy SOCKS5 en `127.0.0.1:40000` para conectarse a la API de Telegram. Si no lo necesitas, edita o elimina el parámetro `proxy` en `telegram_bot.py`:

```python
request = HTTPXRequest(
    connect_timeout=60.0,
    read_timeout=60.0,
    pool_timeout=60.0,
    proxy="socks5://127.0.0.1:40000",  # quitar o cambiar según tu entorno
)
```

## Uso

```bash
python telegram_bot.py
```

En Telegram:

- `/start` — mensaje de bienvenida
- Cualquier texto — se envía a sci-bot.ru y recibes `respuesta.pdf`

Los eventos se registran en `bot.log` (también excluido del repositorio).

### Ejecución en segundo plano (Windows)

`run_hidden.vbs` lanza el bot sin ventana de consola. Antes de usarlo, ajusta las rutas de Python y del proyecto dentro del archivo:

```vbs
ws.CurrentDirectory = "C:\ruta\a\scibot.telegram"
ws.Run """C:\ruta\a\pythonw.exe"" telegram_bot.py", 0, False
```

Doble clic en el `.vbs` o colócalo en el inicio de Windows si quieres que arranque automáticamente.

## Estructura del proyecto

```
scibot.telegram/
├── telegram_bot.py    # Bot de Telegram: handlers, polling, envío del PDF
├── scibot_client.py   # Login REST + chat WebSocket con sci-bot.ru
├── pdf_export.py      # Generación del PDF con fpdf2
├── requirements.txt   # Dependencias Python
├── run_hidden.vbs     # Arranque oculto en Windows
├── .env.example       # Plantilla de variables de entorno
└── .gitignore
```

## Cómo funciona por dentro

```
Telegram (mensaje)
       │
       ▼
telegram_bot.py
       │
       ├── scibot_client.login()     → POST /api/login  → cookie scibot_auth
       │
       └── scibot_client.ask_question()  → WebSocket wss://sci-bot.ru/
                │                              (eventos: content, done, error)
                ▼
           pdf_export.build_pdf()
                │
                ▼
       Telegram (documento respuesta.pdf)
```

- **Timeout de respuesta:** 180 segundos (`ANSWER_TIMEOUT` en `scibot_client.py`)
- **Idioma por defecto:** español (`lang="es"`)
- **Formato de salida:** PDF, no mensaje de texto

## Dependencias principales

| Paquete | Uso |
|---|---|
| `python-telegram-bot` | Bot de Telegram y polling |
| `websockets` | Chat en tiempo real con sci-bot.ru |
| `requests` | Login HTTP |
| `fpdf2` | Generación de PDF |
| `python-dotenv` | Variables de entorno desde `.env` |
| `httpx[socks]` | Cliente HTTP con soporte SOCKS5 |

## Solución de problemas

| Síntoma | Posible causa |
|---|---|
| El bot no responde | Tu ID de Telegram no coincide con `ALLOWED_USER_ID` en `.env` |
| `Error de sci-bot: Login fallido` | Usuario o contraseña incorrectos en `.env` |
| `Tiempo de espera agotado` | sci-bot.ru tardó más de 180 s; reintenta |
| Error al conectar con Telegram | Proxy SOCKS5 no activo o token inválido |
| PDF con caracteres rotos | Fuente Arial no encontrada (solo probado en Windows) |

Revisa `bot.log` para el detalle de errores en ejecución.

## Licencia

Uso personal. sci-bot.ru es un servicio de terceros; respeta sus términos de uso.
