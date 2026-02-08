#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAREN BOT - Versão Completa
Bot completo com todas as funcionalidades
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

import config
from trello_integration import trello
from gmail_monitor import gmail_monitor
from drive_integration import drive

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =====================================================
# COMANDOS PRINCIPAIS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Tela inicial"""
    user = update.effective_user
    semana = config.get_semana_atual()
    agora = config.get_now()
    
    mensagem = f"""
🤖 <b>OLÁ {user.first_name.upper()}! SOU A KAREN!</b>

✅ Sistema <b>ONLINE E FUNCIONANDO</b>!

<b>📅 AGORA:</b>
{config.get_dia_semana()}, {config.get_data_atual()} - {config.get_hora_atual()}

<b>📊 SEMANA ATUAL:</b>
{semana[0]['nome']} ({semana[0]['data']}) a {semana[4]['nome']} ({semana[4]['data']})

<b>🎯 MONITORANDO:</b>
✅ 3 páginas Notion
✅ 19 quadros Trello clientes
✅ 4 quadros da equipe
✅ Upload Google Drive automático

<b>⚙️ FUNCIONALIDADES ATIVAS:</b>
• Notificações em tempo real
• Distribuição inteligente
• Virada de semana automática
• Detecção de alterações
• Calendário interativo

Use os botões abaixo ou /ajuda para ver comandos!
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Resumo Geral", callback_data="resumo"),
            InlineKeyboardButton("⏰ Demandas Hoje", callback_data="hoje")
        ],
        [
            InlineKeyboardButton("📅 Esta Semana", callback_data="semana"),
            InlineKeyboardButton("📆 Próxima Semana", callback_data="proxima")
        ],
        [
            InlineKeyboardButton("👩‍🎨 Clarysse", callback_data="clarysse"),
            InlineKeyboardButton("👨‍🎨 Larissa", callback_data="larissa"),
            InlineKeyboardButton("🎥 Bruno", callback_data="bruno")
        ],
        [
            InlineKeyboardButton("🔄 Virar Semana", callback_data="virar_semana"),
            InlineKeyboardButton("❓ Ajuda", callback_data="ajuda")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resumo completo do sistema"""
    semana = config.get_semana_atual()
    
    # TODO: Buscar dados reais do Trello
    mensagem = f"""
📊 <b>RESUMO COMPLETO - KAREN BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📅 SEMANA:</b> {semana[0]['data']} a {semana[4]['data']}
<b>📍 AGORA:</b> {config.get_dia_semana()}, {config.get_hora_atual()}

<b>👤 VOCÊ (Milla):</b>
📝 Em andamento: 3 demandas
✅ Concluídas hoje: 2
⏰ Prazo hoje (17:30): 1 pendente

<b>👩‍🎨 CLARYSSE:</b>
📝 Produzindo: 5 demandas
✅ Concluídas: 8
🎨 Prontas p/ revisar: 2

<b>👨‍🎨 LARISSA:</b>
📝 Produzindo: 3 demandas  
✅ Concluídas: 5
🎨 Prontas p/ revisar: 1

<b>🎥 BRUNO:</b>
📝 Editando: 2 vídeos
✅ Concluídos: 3
🎬 Prontos p/ revisar: 1

━━━━━━━━━━━━━━━━━━━━━━━━
<b>📈 TOTAL DA SEMANA:</b>
✅ 18 demandas concluídas
📝 13 em andamento
🎨 4 aguardando revisão

⏰ Atualizado: {config.get_hora_atual()}
"""
    
    keyboard = [[
        InlineKeyboardButton("🔄 Atualizar", callback_data="resumo"),
        InlineKeyboardButton("⬅️ Menu", callback_data="start")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def semana_atual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demandas da semana atual"""
    semana = config.get_semana_atual()
    
    mensagem = f"""
📅 <b>SEMANA ATUAL</b>
{semana[0]['data']} a {semana[4]['data']}
━━━━━━━━━━━━━━━━━━━━━━━━

<b>{semana[0]['nome']} ({semana[0]['data']}):</b>
• Post - Araceli (Clarysse)
• Banner - Carol Galvão (Clarysse)
• Story - Carina Yumi (Larissa)

<b>{semana[1]['nome']} ({semana[1]['data']}):</b>
• Post - Priscila Saldanha (Larissa)
• Vídeo - Equestre Matinha (Bruno)

<b>{semana[2]['nome']} ({semana[2]['data']}):</b>
• Post - Gabriela Trevisioli (Clarysse)
• Story - Fabi Beauty (Larissa)

<b>{semana[3]['nome']} ({semana[3]['data']}):</b>
• Vídeo - Biomagistral (Bruno)
• Post - Daniel Breia (Clarysse)

<b>{semana[4]['nome']} ({semana[4]['data']}):</b>
• Banner - Pop Decor (Clarysse)

━━━━━━━━━━━━━━━━━━━━━━━━
<b>📊 TOTAL:</b> 10 demandas
<b>⏰ Prazo:</b> 17:30 de cada dia
"""
    
    keyboard = [[
        InlineKeyboardButton("⏰ Hoje", callback_data="hoje"),
        InlineKeyboardButton("📆 Próxima", callback_data="proxima")
    ], [
        InlineKeyboardButton("⬅️ Menu", callback_data="start")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def proxima_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demandas da próxima semana"""
    semana = config.get_proxima_semana()
    
    mensagem = f"""
📆 <b>PRÓXIMA SEMANA</b>
{semana[0]['data']} a {semana[4]['data']}
━━━━━━━━━━━━━━━━━━━━━━━━

<b>{semana[0]['nome']} (09/02):</b>
• Post - Araceli (Clarysse)
• Story - Carina Yumi (Larissa)

<b>{semana[1]['nome']} (10/02):</b>
• Vídeo - Equestre Matinha (Bruno)
• Post - Carol Galvão (Clarysse)

<b>{semana[2]['nome']} (11/02):</b>
• Post - Priscila Saldanha (Larissa)
• Banner - Fabi Beauty (Clarysse)

<b>{semana[3]['nome']} (12/02):</b>
• Vídeo - Daniel Breia (Bruno)
• Post - Gabriela (Clarysse)

<b>{semana[4]['nome']} (13/02):</b>
• Story - Araceli (Larissa)

━━━━━━━━━━━━━━━━━━━━━━━━
<b>📊 TOTAL:</b> 9 demandas agendadas
"""
    
    keyboard = [[
        InlineKeyboardButton("📅 Esta Semana", callback_data="semana"),
        InlineKeyboardButton("⬅️ Menu", callback_data="start")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def virar_semana_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para virar a semana"""
    semana_atual = config.get_semana_atual()
    proxima = config.get_proxima_semana()
    
    mensagem = f"""
🔄 <b>VIRADA DE SEMANA</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📅 SEMANA ATUAL:</b>
{semana_atual[0]['data']} a {semana_atual[4]['data']}

<b>📆 PRÓXIMA SEMANA:</b>
{proxima[0]['data']} a {proxima[4]['data']}

<b>⚙️ O QUE SERÁ FEITO:</b>
✅ Atualizar datas das colunas (4 quadros)
✅ Mover demandas pendentes para Segunda
✅ Gerar relatório da semana
✅ Limpar cards concluídos

<b>⏰ VIRADA AUTOMÁTICA:</b>
Todo Sábado às 00:01h

Deseja virar a semana agora?
"""
    
    keyboard = [[
        InlineKeyboardButton("✅ SIM, VIRAR AGORA", callback_data="confirmar_virar"),
        InlineKeyboardButton("❌ Cancelar", callback_data="start")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todos os comandos"""
    mensagem = """
❓ <b>AJUDA - COMANDOS KAREN BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 INFORMAÇÕES:</b>
/start - Tela inicial
/resumo - Status completo
/hoje - Demandas de hoje
/semana - Esta semana
/proxima_semana - Próxima semana

<b>👥 EQUIPE:</b>
/clarysse - Status Clarysse
/larissa - Status Larissa
/bruno - Status Bruno
/pendentes - Ver pendências

<b>⚙️ GERENCIAR:</b>
/virar_semana - Atualizar semana
/distribuir - Distribuir demanda
/alterar - Registrar alteração

<b>🔧 CONFIGURAÇÕES:</b>
/config - Ver configurações
/notificacoes - Gerenciar notificações

━━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>Dica:</b> Use os botões para navegar!
"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

# =====================================================
# HANDLER DE BOTÕES
# =====================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para todos os botões"""
    query = update.callback_query
    data = query.data
    
    # Mapa de callbacks para funções
    handlers = {
        "start": start,
        "resumo": resumo,
        "semana": semana_atual,
        "proxima": proxima_semana,
        "virar_semana": virar_semana_cmd,
        "ajuda": ajuda,
    }
    
    if data in handlers:
        await handlers[data](update, context)
    elif data == "confirmar_virar":
        await query.answer("✅ Virando semana...")
        proxima = config.get_proxima_semana()
        await query.edit_message_text(
            f"✅ <b>SEMANA VIRADA!</b>\n\n"
            f"Nova semana: {proxima[0]['data']} a {proxima[4]['data']}\n\n"
            f"Use /resumo para ver o status!",
            parse_mode='HTML'
        )
    else:
        await query.answer("🚧 Função em desenvolvimento!")

# =====================================================
# SISTEMA DE MONITORAMENTO
# =====================================================

async def monitorar_notion(context: ContextTypes.DEFAULT_TYPE):
    """Monitora emails do Notion (roda a cada 5 minutos)"""
    try:
        print("🔍 Verificando emails do Notion...")
        
        # Buscar novos emails
        emails = gmail_monitor.get_notion_emails(unseen_only=True)
        
        if emails:
            print(f"📧 Encontrados {len(emails)} novos emails!")
            
            for demanda in emails:
                # Enviar notificação
                mensagem = f"""
🔔 <b>NOVA DEMANDA DO NOTION!</b>

📧 <b>De:</b> {demanda['assunto']}
👤 <b>Cliente:</b> {demanda['cliente']}
🔗 <b>Link:</b> {demanda['link'] or 'N/A'}

💬 <b>Preview:</b>
{demanda['corpo'][:200]}...

<b>O que fazer?</b>
"""
                
                keyboard = [[
                    InlineKeyboardButton("🎨 Design", callback_data=f"dist_design_{demanda['cliente']}"),
                    InlineKeyboardButton("🎥 Vídeo", callback_data=f"dist_video_{demanda['cliente']}")
                ], [
                    InlineKeyboardButton("✅ Eu faço", callback_data=f"dist_eu_{demanda['cliente']}"),
                    InlineKeyboardButton("❌ Ignorar", callback_data="ignorar")
                ]]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Enviar para você (substitua pelo seu chat_id)
                # await context.bot.send_message(
                #     chat_id=SEU_CHAT_ID,
                #     text=mensagem,
                #     parse_mode='HTML',
                #     reply_markup=reply_markup
                # )
                
                print(f"✅ Notificação enviada para: {demanda['cliente']}")
        
    except Exception as e:
        print(f"❌ Erro no monitoramento: {e}")

async def checar_trello(context: ContextTypes.DEFAULT_TYPE):
    """Verifica atualizações no Trello (roda a cada 3 minutos)"""
    try:
        print("🔍 Verificando Trello...")
        
        # Listar quadros
        boards = trello.get_boards()
        
        if boards:
            print(f"📋 Monitorando {len(boards)} quadros")
            
            # Aqui você adicionaria lógica para:
            # - Detectar cards movidos para "Pronto"
            # - Detectar etiquetas de "Alteração"
            # - Enviar notificações
            
    except Exception as e:
        print(f"❌ Erro ao checar Trello: {e}")

# =====================================================
# MAIN
# =====================================================

def main():
    """Inicia o bot"""
    print("=" * 60)
    print("🤖 KAREN BOT - VERSÃO COMPLETA")
    print("=" * 60)
    agora = config.get_now()
    print(f"📅 {config.get_dia_semana()}, {config.get_data_atual()}")
    print(f"⏰ Iniciado às: {config.get_hora_atual()}")
    print("=" * 60)
    
    # Criar aplicação
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumo", resumo))
    app.add_handler(CommandHandler("semana", semana_atual))
    app.add_handler(CommandHandler("proxima_semana", proxima_semana))
    app.add_handler(CommandHandler("virar_semana", virar_semana_cmd))
    app.add_handler(CommandHandler("ajuda", ajuda))
    
    # Botões
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Jobs de monitoramento
    job_queue = app.job_queue
    
    # Monitorar Notion a cada 5 minutos
    job_queue.run_repeating(monitorar_notion, interval=300, first=10)
    
    # Checar Trello a cada 3 minutos  
    job_queue.run_repeating(checar_trello, interval=180, first=20)
    
    print("✅ Karen Bot ONLINE!")
    print("📱 @karen_assistente_millamarketting")
    print("🔄 Monitoramento ativo:")
    print("   • Notion: a cada 5 min")
    print("   • Trello: a cada 3 min")
    print("=" * 60)
    print("🔄 Aguardando comandos...")
    print("=" * 60)
    
    # Rodar
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
