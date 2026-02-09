import os
from datetime import datetime, timedelta
from pytz import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from app.storage.db import add_event, list_events, add_tracked_client, remove_tracked_client, get_tracked_clients
from app.integrations.trello_api import create_task_card, move_to_changes, find_best_match_card, rename_week_lists
from app.utils.formatters import format_new_demand_message, format_status_message

TZ = timezone(os.getenv("TIMEZONE","America/Sao_Paulo"))

# -------- Helpers --------
def chat_id():
    v = os.getenv("TELEGRAM_CHAT_ID","").strip()
    return int(v) if v else None

def kb_main_actions(payload_id: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 Design", callback_data=f"TYPE|design|{payload_id}"),
            InlineKeyboardButton("🎥 Vídeo", callback_data=f"TYPE|video|{payload_id}"),
        ],
        [
            InlineKeyboardButton("✅ Fazer Eu", callback_data=f"TYPE|me|{payload_id}"),
            InlineKeyboardButton("❌ Ignorar", callback_data=f"IGNORE|{payload_id}"),
        ]
    ])

def kb_people(task_type: str, payload_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Designer Clarysse", callback_data=f"ASSIGN|clarysse|{task_type}|{payload_id}")],
        [InlineKeyboardButton("Designer Larissa", callback_data=f"ASSIGN|larissa|{task_type}|{payload_id}")],
        [InlineKeyboardButton("Editor Bruno", callback_data=f"ASSIGN|bruno|{task_type}|{payload_id}")]
    ])

def kb_due_date(who: str, task_type: str, payload_id: str):
    today = datetime.now(TZ).date()
    tomorrow = today + timedelta(days=1)
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📅 Hoje ({today.strftime('%d/%m')})", callback_data=f"DUE|{who}|{task_type}|today|{payload_id}"),
            InlineKeyboardButton(f"📅 Amanhã ({tomorrow.strftime('%d/%m')})", callback_data=f"DUE|{who}|{task_type}|tomorrow|{payload_id}"),
        ],
        [InlineKeyboardButton("📅 Escolher data", callback_data=f"DUE|{who}|{task_type}|pick|{payload_id}")]
    ])

def kb_calendar(who: str, task_type: str, payload_id: str, base_date=None):
    # Calendário simples (próximos 14 dias)
    base_date = base_date or datetime.now(TZ).date()
    rows = []
    row = []
    for i in range(14):
        d = base_date + timedelta(days=i)
        row.append(InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"DUESET|{who}|{task_type}|{d.isoformat()}|{payload_id}"))
        if len(row) == 7:
            rows.append(row); row=[]
    if row: rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ Voltar", callback_data=f"BACK|{task_type}|{payload_id}")])
    return InlineKeyboardMarkup(rows)

# -------- Commands --------
async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "🤖 *Comandos do bot*
"
        "/resumo - status geral
"
        "/hoje - demandas de hoje
"
        "/semana - visão da semana
"
        "/clarysse - status Designer Clarysse
"
        "/larissa - status Designer Larissa
"
        "/bruno - status Editor Bruno
"
        "/add_cliente NOME - começar a monitorar
"
        "/remove_cliente NOME - parar de monitorar
"
        "/virar_semana - renomear listas no Trello
"
    )
    await update.message.reply_text(txt, parse_mode="Markdown")

async def cmd_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = list_events(limit=30)
    await update.message.reply_text(format_status_message(events), disable_web_page_preview=True)

async def cmd_hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = [e for e in list_events(limit=100) if "today" in (e[5] or "").lower()]
    await update.message.reply_text(format_status_message(events[:30]), disable_web_page_preview=True)

async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = list_events(limit=80)
    await update.message.reply_text(format_status_message(events), disable_web_page_preview=True)

async def cmd_person(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    events = [e for e in list_events(limit=120) if (e[5] or "").lower().find(name) >= 0]
    await update.message.reply_text(format_status_message(events[:30]), disable_web_page_preview=True)

async def cmd_clarysse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_person(update, context, "clarysse")

async def cmd_larissa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_person(update, context, "larissa")

async def cmd_bruno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_person(update, context, "bruno")

async def cmd_add_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Me fala o nome: /add_cliente Nome do Cliente")
    name = " ".join(context.args).strip()
    add_tracked_client(name)
    await update.message.reply_text(f"✅ Ok. Vou monitorar: {name}")

async def cmd_remove_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Me fala o nome: /remove_cliente Nome do Cliente")
    name = " ".join(context.args).strip()
    remove_tracked_client(name)
    await update.message.reply_text(f"✅ Parei de monitorar: {name}")

async def cmd_virar_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = rename_week_lists()
    await update.message.reply_text(res)

# -------- Callback flow --------
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data.split("|")

    if data[0] == "IGNORE":
        payload_id = data[1]
        add_event("telegram","ignored",payload=payload_id)
        return await q.edit_message_reply_markup(reply_markup=None)

    if data[0] == "TYPE":
        task_type, payload_id = data[1], data[2]
        if task_type in ("design","video"):
            await q.edit_message_reply_markup(reply_markup=kb_people(task_type, payload_id))
        elif task_type == "me":
            # Pra você mesma: escolhe data direto
            await q.edit_message_reply_markup(reply_markup=kb_due_date("milla", task_type, payload_id))
        return

    if data[0] == "ASSIGN":
        who, task_type, payload_id = data[1], data[2], data[3]
        await q.edit_message_reply_markup(reply_markup=kb_due_date(who, task_type, payload_id))
        return

    if data[0] == "DUE":
        who, task_type, mode, payload_id = data[1], data[2], data[3], data[4]
        if mode == "pick":
            await q.edit_message_reply_markup(reply_markup=kb_calendar(who, task_type, payload_id))
            return
        # today/tomorrow
        d = datetime.now(TZ).date() if mode=="today" else (datetime.now(TZ).date() + timedelta(days=1))
        await finalize_create_card(q, who, task_type, d, payload_id)
        return

    if data[0] == "DUESET":
        who, task_type, iso, payload_id = data[1], data[2], data[3], data[4]
        d = datetime.fromisoformat(iso).date()
        await finalize_create_card(q, who, task_type, d, payload_id)
        return

    if data[0] == "BACK":
        task_type, payload_id = data[1], data[2]
        await q.edit_message_reply_markup(reply_markup=kb_due_date("milla", task_type, payload_id))


async def finalize_create_card(q, who: str, task_type: str, due_date, payload_id: str):
    payload = context_payload(q, payload_id)
    if not payload:
        return await q.edit_message_text("⚠️ Não achei os dados dessa demanda (reinicia o bot e tenta de novo).")

    # Regra: se você fizer, não cria card no seu quadro (ajuste do PDF)
    # Só cria alerta de alteração quando for alteração. Aqui é nova demanda, então não salva no Trello da Milla.
    created = None
    if who != "milla":
        created = create_task_card(who=who, task_type=task_type, due_date=due_date, demand=payload)
        add_event("trello","card_created",client=payload.get("client"), title=payload.get("title"), payload=f"who={who}; url={created.get('url')}")
        await q.edit_message_text(f"✅ Cartão criado no Trello ({who}).\n🔗 {created.get('url')}", disable_web_page_preview=True)
    else:
        add_event("telegram","me_task_logged",client=payload.get("client"), title=payload.get("title"), payload=f"me; due={due_date.isoformat()}")
        await q.edit_message_text(f"✅ Fechado. Você faz.\n📅 Prazo: {due_date.strftime('%d/%m')} (17:30)")

def context_payload(q, payload_id):
    # payload guardado em bot_data
    return q.message.chat_data.get(f"payload:{payload_id}") if q.message else None


# -------- Entry point --------
def build_application() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN","").strip()
    if not token:
        raise RuntimeError("Faltou TELEGRAM_BOT_TOKEN no .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("ajuda", cmd_ajuda))
    app.add_handler(CommandHandler("resumo", cmd_resumo))
    app.add_handler(CommandHandler("hoje", cmd_hoje))
    app.add_handler(CommandHandler("semana", cmd_semana))
    app.add_handler(CommandHandler("clarysse", cmd_clarysse))
    app.add_handler(CommandHandler("larissa", cmd_larissa))
    app.add_handler(CommandHandler("bruno", cmd_bruno))
    app.add_handler(CommandHandler("add_cliente", cmd_add_cliente))
    app.add_handler(CommandHandler("remove_cliente", cmd_remove_cliente))
    app.add_handler(CommandHandler("virar_semana", cmd_virar_semana))

    app.add_handler(CallbackQueryHandler(on_callback))
    return app


async def push_new_demand(app: Application, demand: dict):
    # Salva payload no chat_data e manda mensagem com botões
    from uuid import uuid4
    payload_id = uuid4().hex[:10]

    cid = chat_id()
    if not cid:
        return

    # Guardar no chat_data do bot
    app.chat_data.setdefault(cid, {})
    app.chat_data[cid][f"payload:{payload_id}"] = demand

    msg = format_new_demand_message(demand)
    await app.bot.send_message(
        chat_id=cid,
        text=msg,
        reply_markup=kb_main_actions(payload_id),
        disable_web_page_preview=True
    )
