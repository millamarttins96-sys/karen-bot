#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAREN BOT - Versão Funcional Simplificada
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fuso horário Brasil
BRASILIA_TZ = timezone(timedelta(hours=-3))
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8217382481:AAHe12yh-31BqjoEB9NwCy5ONuN6kN7QDzs')

def get_now():
    return datetime.now(BRASILIA_TZ)

def get_semana_atual():
    hoje = get_now()
    dia_semana = hoje.weekday()
    dias_ate_segunda = dia_semana
    segunda = hoje - timedelta(days=dias_ate_segunda)
    
    if dia_semana >= 5:
        segunda = segunda + timedelta(days=7)
    
    semana = []
    dias_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    for i in range(5):
        dia = segunda + timedelta(days=i)
        semana.append({
            "nome": dias_nome[i],
            "data": dia.strftime("%d/%m")
        })
    return semana

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    semana = get_semana_atual()
    agora = get_now()
    
    mensagem = f"""
🤖 <b>KAREN BOT ONLINE!</b>

✅ Sistema funcionando!

📅 <b>Agora:</b> {agora.strftime("%d/%m/%Y %H:%M")}

📊 <b>Semana:</b> {semana[0]['data']} a {semana[4]['data']}

Use os botões abaixo:
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data="status"),
            InlineKeyboardButton("📅 Semana", callback_data="semana")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start":
        await start(update, context)
    elif query.data == "status":
        await query.edit_message_text("✅ Bot funcionando normalmente!")
    elif query.data == "semana":
        semana = get_semana_atual()
        msg = f"📅 Semana: {semana[0]['data']} a {semana[4]['data']}"
        await query.edit_message_text(msg)

def main():
    """Inicia o bot"""
    print("=" * 60)
    print("🤖 KAREN BOT - INICIANDO")
    print("=" * 60)
    print(f"⏰ {get_now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ BOT ONLINE!")
    print("=" * 60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
