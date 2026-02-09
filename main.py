#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAREN BOT - SISTEMA COMPLETO
Monitora Notion + Trello e distribui demandas REAIS
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters
)

import config
from trello_api import trello
from gmail_monitor import gmail

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estado temporário (será melhorado depois)
distribuindo = {}
fila_demandas = []  # Lista de demandas não distribuídas

# =====================================================
# COMANDOS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    semana = config.get_semana_atual()
    
    msg = f"""
🤖 <b>KAREN BOT - SISTEMA ATIVO!</b>

✅ Monitorando:
• 3 páginas Notion
• 19 quadros Trello clientes  
• 4 quadros da equipe

📅 <b>Semana:</b> {semana[0]['data']} a {semana[4]['data']}

📋 <b>Demandas pendentes:</b> {len(fila_demandas)}

<b>Comandos:</b>
/demandas - Ver todas pendentes
/resumo - Status geral
/hoje - Demandas de hoje
/test - Testar notificação
"""
    
    keyboard = [[
        InlineKeyboardButton("📋 Ver Demandas", callback_data="ver_demandas"),
        InlineKeyboardButton("⏰ Hoje", callback_data="hoje")
    ]]
    
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=markup)

async def ver_demandas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todas as demandas não distribuídas"""
    if not fila_demandas:
        msg = "✅ Nenhuma demanda pendente!\n\nTodas foram distribuídas."
        
        if update.callback_query:
            await update.callback_query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return
    
    msg = f"""
📋 <b>DEMANDAS PENDENTES ({len(fila_demandas)})</b>

Clique em uma para distribuir:
"""
    
    keyboard = []
    for i, dem in enumerate(fila_demandas[:10]):  # Mostrar até 10
        texto = f"{dem['cliente']} - {dem.get('titulo', 'Ver')[:20]}"
        keyboard.append([InlineKeyboardButton(
            f"{i+1}. {texto}",
            callback_data=f"dist_dem_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔄 Atualizar", callback_data="ver_demandas")])
    markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=markup)
    else:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=markup)

async def test_notificacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Testa uma notificação de demanda"""
    demanda_exemplo = {
        'cliente': 'Araceli',
        'titulo': '3 posts Instagram',
        'copy': 'Post 1: Promoção verão\nPost 2: Nova coleção\nPost 3: Depoimento',
        'data': '12/02/2026',
        'link': 'https://notion.so/exemplo',
        'origem': 'notion'
    }
    
    await enviar_notificacao_demanda(update, context, demanda_exemplo)

async def enviar_notificacao_demanda(update, context, demanda):
    """Envia notificação de nova demanda"""
    msg = f"""
🔔 <b>NOVA DEMANDA!</b>

👤 <b>Cliente:</b> {demanda['cliente']}
📝 <b>Demanda:</b> {demanda.get('titulo', 'Ver descrição')}
📅 <b>Entrega:</b> {demanda.get('data', 'A definir')}

💬 <b>Copy:</b>
{demanda.get('copy', 'Ver no link')[:200]}...

🔗 <a href="{demanda['link']}">Abrir tarefa</a>
"""
    
    # Salvar demanda temporariamente
    demanda_id = f"dem_{len(distribuindo)}"
    distribuindo[demanda_id] = demanda
    
    keyboard = [[
        InlineKeyboardButton("🎨 Design", callback_data=f"tipo_design_{demanda_id}"),
        InlineKeyboardButton("🎥 Vídeo", callback_data=f"tipo_video_{demanda_id}")
    ], [
        InlineKeyboardButton("✅ Eu faço", callback_data=f"tipo_eu_{demanda_id}"),
        InlineKeyboardButton("❌ Ignorar", callback_data=f"ignorar_{demanda_id}")
    ]]
    
    markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text(msg, parse_mode='HTML', reply_markup=markup)
    else:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=markup)

# =====================================================
# HANDLERS DE BOTÕES
# =====================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal de botões"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # VER LISTA DE DEMANDAS
    if data == "ver_demandas":
        await ver_demandas(update, context)
    
    # DISTRIBUIR DEMANDA DA LISTA
    elif data.startswith("dist_dem_"):
        index = int(data.split("_")[2])
        if index < len(fila_demandas):
            demanda = fila_demandas[index]
            await enviar_notificacao_demanda(update, context, demanda)
    
    # TIPO DE DEMANDA (Design/Vídeo/Eu)
    elif data.startswith("tipo_"):
        await handle_tipo_demanda(update, context, data)
    
    # ESCOLHER PESSOA
    elif data.startswith("pessoa_"):
        await handle_escolher_pessoa(update, context, data)
    
    # ESCOLHER DIA
    elif data.startswith("dia_"):
        await handle_escolher_dia(update, context, data)
    
    # OUTROS
    elif data == "resumo":
        await query.edit_message_text("📊 Função em desenvolvimento!")
    elif data == "hoje":
        await query.edit_message_text("⏰ Função em desenvolvimento!")

async def handle_tipo_demanda(update, context, data):
    """Handle quando escolhe tipo (design/video/eu)"""
    query = update.callback_query
    parts = data.split("_")
    tipo = parts[1]  # design, video, eu
    demanda_id = "_".join(parts[2:])
    
    if demanda_id not in distribuindo:
        await query.edit_message_text("❌ Demanda não encontrada!")
        return
    
    demanda = distribuindo[demanda_id]
    demanda['tipo_escolhido'] = tipo
    
    if tipo == "eu":
        # Se escolheu "Eu faço", pula escolher pessoa
        demanda['pessoa'] = 'milla'
        await mostrar_escolher_dia(query, demanda_id, demanda)
    elif tipo == "design":
        # Mostra designers
        msg = f"👩‍🎨 <b>Qual designer?</b>\n\nCliente: {demanda['cliente']}"
        keyboard = [[
            InlineKeyboardButton("👩‍🎨 Clarysse", callback_data=f"pessoa_clarysse_{demanda_id}"),
            InlineKeyboardButton("👨‍🎨 Larissa", callback_data=f"pessoa_larissa_{demanda_id}")
        ]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=markup)
    elif tipo == "video":
        # Vai direto para Bruno
        demanda['pessoa'] = 'bruno'
        await mostrar_escolher_dia(query, demanda_id, demanda)

async def handle_escolher_pessoa(update, context, data):
    """Handle quando escolhe pessoa"""
    query = update.callback_query
    parts = data.split("_")
    pessoa = parts[1]  # clarysse, larissa
    demanda_id = "_".join(parts[2:])
    
    if demanda_id not in distribuindo:
        await query.edit_message_text("❌ Demanda não encontrada!")
        return
    
    demanda = distribuindo[demanda_id]
    demanda['pessoa'] = pessoa
    
    await mostrar_escolher_dia(query, demanda_id, demanda)

async def mostrar_escolher_dia(query, demanda_id, demanda):
    """Mostra opções de dia da semana"""
    semana = config.get_semana_atual()
    
    pessoa_nome = config.EQUIPE[demanda['pessoa']]['nome']
    
    msg = f"""
📅 <b>Qual dia?</b>

{config.EQUIPE[demanda['pessoa']]['emoji']} <b>{pessoa_nome}</b>
👤 Cliente: {demanda['cliente']}
"""
    
    keyboard = []
    linha = []
    for i, dia in enumerate(semana):
        linha.append(InlineKeyboardButton(
            f"{dia['nome'][:3]} {dia['data']}", 
            callback_data=f"dia_{i}_{demanda_id}"
        ))
        if len(linha) == 2:
            keyboard.append(linha)
            linha = []
    if linha:
        keyboard.append(linha)
    
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=markup)

async def handle_escolher_dia(update, context, data):
    """Handle quando escolhe dia"""
    query = update.callback_query
    parts = data.split("_")
    dia_index = int(parts[1])
    demanda_id = "_".join(parts[2:])
    
    if demanda_id not in distribuindo:
        await query.edit_message_text("❌ Demanda não encontrada!")
        return
    
    demanda = distribuindo[demanda_id]
    semana = config.get_semana_atual()
    dia_escolhido = semana[dia_index]
    
    demanda['dia'] = dia_escolhido
    
    # CRIAR CARD NO TRELLO!
    sucesso = await criar_card_trello(demanda)
    
    if sucesso:
        pessoa_nome = config.EQUIPE[demanda['pessoa']]['nome']
        
        msg = f"""
✅ <b>CARD CRIADO!</b>

📌 <b>Quadro:</b> {pessoa_nome}
📅 <b>Dia:</b> {dia_escolhido['nome']}-Feira ({dia_escolhido['data']})
👤 <b>Cliente:</b> {demanda['cliente']}

🔗 <a href="https://trello.com">Ver no Trello</a>

📋 Pendentes: {len(fila_demandas)}
"""
        
        # Remover da fila se estava lá
        if demanda in fila_demandas:
            fila_demandas.remove(demanda)
        
        # Limpar da memória
        del distribuindo[demanda_id]
        
        # Botão para próxima
        keyboard = []
        if fila_demandas:
            keyboard.append([InlineKeyboardButton(
                f"➡️ Próxima ({len(fila_demandas)} pendentes)",
                callback_data="ver_demandas"
            )])
        markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=markup)
    else:
        await query.edit_message_text("❌ Erro ao criar card! Tente novamente.")

# =====================================================
# CRIAR CARD NO TRELLO
# =====================================================

async def criar_card_trello(demanda):
    """Cria card no Trello REAL"""
    try:
        pessoa = demanda['pessoa']
        quadro_nome = config.EQUIPE[pessoa]['quadro']
        dia = demanda['dia']
        
        # Buscar quadro
        board = trello.find_board(quadro_nome)
        if not board:
            print(f"Quadro não encontrado: {quadro_nome}")
            return False
        
        # Verificar se é ALTERAÇÃO ou NOVA DEMANDA
        eh_alteracao = demanda.get('eh_alteracao', False)
        
        # Se for ALTERAÇÃO + EU FAÇO → Coluna Alterações
        if pessoa == 'milla' and eh_alteracao:
            coluna_nome = "Alterações"
            titulo = f"Alteração - {demanda['cliente']}"
            descricao = f"""
⚠️ ALTERAÇÃO

{demanda.get('copy', 'Ver no link')}

🔗 Link: {demanda['link']}
"""
            prazo = None
        else:
            # Para TODOS (incluindo Milla em nova demanda): coluna do dia
            coluna_nome = f"{dia['nome']}-Feira ({dia['data']})"
            titulo = demanda['cliente']
            descricao = f"""
📝 DEMANDA:
{demanda.get('titulo', 'Ver no link')}

💬 COPY:
{demanda.get('copy', 'Ver no link')}

🔗 ORIGEM:
{demanda['link']}

⏰ Prazo: {dia['data_completa']} - 17:30
"""
            prazo = f"{dia['data_completa']}T17:30:00.000Z"
        
        # Buscar coluna
        lista = trello.find_list(board['id'], coluna_nome)
        if not lista:
            print(f"Coluna não encontrada: {coluna_nome}")
            return False
        
        # Criar card
        card = trello.create_card(
            lista['id'],
            titulo,
            descricao,
            due=prazo
        )
        
        if card:
            print(f"✅ Card criado: {titulo} em {quadro_nome}/{coluna_nome}")
            return True
        return False
        
    except Exception as e:
        print(f"Erro ao criar card: {e}")
        return False

# =====================================================
# MONITORAMENTO
# =====================================================

async def monitorar_gmail_job(context: ContextTypes.DEFAULT_TYPE):
    """Job que roda a cada 5 minutos"""
    print("🔍 Checando Gmail...")
    
    try:
        demandas = gmail.get_notion_emails()
        
        if demandas:
            print(f"📧 {len(demandas)} novos emails!")
            
            for demanda in demandas:
                # Adicionar à fila
                fila_demandas.append(demanda)
                print(f"  ✅ Adicionada: {demanda['cliente']}")
            
            print(f"📋 Total na fila: {len(fila_demandas)}")
    except Exception as e:
        print(f"Erro ao monitorar Gmail: {e}")

# =====================================================
# MAIN
# =====================================================

def main():
    print("=" * 60)
    print("🤖 KAREN BOT - SISTEMA COMPLETO")
    print("=" * 60)
    print(f"📅 {config.get_now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_notificacao))
    app.add_handler(CommandHandler("demandas", ver_demandas))
    
    # Botões
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Jobs de monitoramento
    job_queue = app.job_queue
    job_queue.run_repeating(monitorar_gmail_job, interval=300, first=10)
    
    print("✅ BOT ONLINE!")
    print("📱 @karen_assistente_millamarketting")
    print("🔄 Monitorando Gmail a cada 5 min")
    print("=" * 60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
