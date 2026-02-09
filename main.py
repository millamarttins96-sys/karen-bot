#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAREN BOT - VERSÃO LIMPA SEM ERROS
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Importar Trello
try:
    from trello_api import trello
    TRELLO_DISPONIVEL = True
except:
    TRELLO_DISPONIVEL = False
    print("⚠️ Trello não disponível")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
BRASILIA_TZ = timezone(timedelta(hours=-3))
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8217382481:AAHe12yh-31BqjoEB9NwCy5ONuN6kN7QDzs')

def get_now():
    return datetime.now(BRASILIA_TZ)

def get_semana():
    hoje = get_now()
    dia_semana = hoje.weekday()
    segunda = hoje - timedelta(days=dia_semana)
    
    if dia_semana >= 5:
        segunda = segunda + timedelta(days=7)
    
    semana = []
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    for i in range(5):
        dia = segunda + timedelta(days=i)
        semana.append({
            "nome": dias[i],
            "data": dia.strftime("%d/%m")
        })
    return semana

# Estado
fila_demandas = []
distribuindo = {}

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    semana = get_semana()
    
    msg = f"""
🤖 <b>KAREN BOT ONLINE!</b>

📅 Semana: {semana[0]['data']} a {semana[4]['data']}
📋 Pendentes: {len(fila_demandas)}

/test - Testar demanda
/demandas - Ver lista
"""
    
    await update.message.reply_text(msg, parse_mode='HTML')

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    demanda = {
        'cliente': 'Araceli',
        'titulo': '3 posts Instagram',
        'copy': 'Post 1: Promoção\nPost 2: Coleção',
        'link': 'https://notion.so/teste'
    }
    
    demanda_id = f"dem_{len(distribuindo)}"
    distribuindo[demanda_id] = demanda
    
    msg = f"""
🔔 <b>NOVA DEMANDA!</b>

👤 <b>Cliente:</b> {demanda['cliente']}
📝 <b>Demanda:</b> {demanda['titulo']}

💬 <b>Copy:</b>
{demanda['copy']}
"""
    
    keyboard = [[
        InlineKeyboardButton("🎨 Design", callback_data=f"tipo_design_{demanda_id}"),
        InlineKeyboardButton("🎥 Vídeo", callback_data=f"tipo_video_{demanda_id}")
    ], [
        InlineKeyboardButton("✅ Eu faço", callback_data=f"tipo_eu_{demanda_id}")
    ]]
    
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=markup)

async def ver_demandas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista demandas pendentes"""
    if not fila_demandas:
        msg = "✅ Nenhuma demanda pendente!"
        await update.message.reply_text(msg)
        return
    
    msg = f"📋 <b>DEMANDAS PENDENTES ({len(fila_demandas)})</b>\n\n"
    
    for i, dem in enumerate(fila_demandas[:10], 1):
        msg += f"{i}. {dem['cliente']} - {dem.get('titulo', 'Ver')[:30]}\n"
    
    msg += "\n<i>Use /test para simular distribuição</i>"
    
    await update.message.reply_text(msg, parse_mode='HTML')

async def listar_quadros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista TODOS os quadros do Trello"""
    if not TRELLO_DISPONIVEL:
        await update.message.reply_text("❌ Trello não disponível")
        return
    
    await update.message.reply_text("🔍 Buscando quadros no Trello...")
    
    boards = trello.get_boards()
    
    if not boards:
        await update.message.reply_text("❌ Nenhum quadro encontrado!")
        return
    
    msg = f"📋 <b>SEUS QUADROS NO TRELLO ({len(boards)})</b>\n\n"
    
    for i, board in enumerate(boards[:20], 1):
        msg += f"{i}. {board['name']}\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("tipo_"):
        parts = data.split("_")
        tipo = parts[1]
        demanda_id = "_".join(parts[2:])
        
        if demanda_id not in distribuindo:
            await query.edit_message_text("❌ Erro!")
            return
        
        demanda = distribuindo[demanda_id]
        demanda['tipo'] = tipo
        
        if tipo == "video":
            demanda['pessoa'] = 'bruno'
            await mostrar_dias(query, demanda_id)
        elif tipo == "eu":
            demanda['pessoa'] = 'milla'
            await mostrar_dias(query, demanda_id)
        else:
            msg = "👩‍🎨 <b>Qual designer?</b>"
            keyboard = [[
                InlineKeyboardButton("Clarysse", callback_data=f"pessoa_clarysse_{demanda_id}"),
                InlineKeyboardButton("Larissa", callback_data=f"pessoa_larissa_{demanda_id}")
            ]]
            markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(msg, parse_mode='HTML', reply_markup=markup)
    
    elif data.startswith("pessoa_"):
        parts = data.split("_")
        pessoa = parts[1]
        demanda_id = "_".join(parts[2:])
        
        if demanda_id not in distribuindo:
            await query.edit_message_text("❌ Erro!")
            return
        
        demanda = distribuindo[demanda_id]
        demanda['pessoa'] = pessoa
        await mostrar_dias(query, demanda_id)
    
    elif data.startswith("dia_"):
        parts = data.split("_")
        dia_idx = int(parts[1])
        demanda_id = "_".join(parts[2:])
        
        if demanda_id not in distribuindo:
            await query.edit_message_text("❌ Erro!")
            return
        
        demanda = distribuindo[demanda_id]
        semana = get_semana()
        dia = semana[dia_idx]
        
        # CRIAR CARD NO TRELLO DE VERDADE!
        await query.edit_message_text("⏳ Criando card no Trello...")
        
        sucesso, resultado = await criar_card_trello_real(demanda, dia)
        
        if sucesso:
            msg = f"""
✅ <b>CARD CRIADO NO TRELLO!</b>

👤 <b>Pessoa:</b> {demanda['pessoa'].title()}
📅 <b>Dia:</b> {dia['nome']} ({dia['data']})
📋 <b>Cliente:</b> {demanda['cliente']}

🔗 <a href="{resultado}">Ver no Trello</a>
"""
        else:
            msg = f"""
❌ <b>ERRO AO CRIAR CARD!</b>

{resultado}

<i>Verifique se os quadros e colunas existem no Trello.</i>
"""
        
        del distribuindo[demanda_id]
        await query.edit_message_text(msg, parse_mode='HTML', disable_web_page_preview=True)

async def mostrar_dias(query, demanda_id):
    semana = get_semana()
    
    msg = "📅 <b>Qual dia?</b>"
    
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

async def criar_card_trello_real(demanda, dia):
    """Cria card NO TRELLO DE VERDADE"""
    if not TRELLO_DISPONIVEL:
        return False, "Trello não disponível"
    
    try:
        pessoa = demanda['pessoa']
        
        # Mapear pessoa para nome do quadro
        quadros = {
            'clarysse': 'Designer Clarysse',
            'larissa': 'Designer Larissa',
            'bruno': 'EDITOR Bruno',
            'milla': 'Minhas Demandas'
        }
        
        quadro_nome = quadros.get(pessoa, 'Designer Clarysse')
        
        # Buscar quadro
        print(f"🔍 Buscando quadro: {quadro_nome}")
        board = trello.find_board(quadro_nome)
        if not board:
            return False, f"Quadro '{quadro_nome}' não encontrado"
        
        print(f"✅ Quadro encontrado: {board['name']}")
        
        # Determinar coluna
        eh_alteracao = demanda.get('eh_alteracao', False)
        
        if pessoa == 'milla' and eh_alteracao:
            coluna_nome = "Alterações"
        else:
            coluna_nome = f"{dia['nome']}-Feira ({dia['data']})"
        
        # Buscar coluna
        print(f"🔍 Buscando coluna: {coluna_nome}")
        lista = trello.find_list(board['id'], coluna_nome)
        if not lista:
            return False, f"Coluna '{coluna_nome}' não encontrada"
        
        print(f"✅ Coluna encontrada: {lista['name']}")
        
        # Criar card
        if pessoa == 'milla' and eh_alteracao:
            titulo = f"Alteração - {demanda['cliente']}"
            descricao = f"""
⚠️ ALTERAÇÃO

{demanda.get('copy', 'Ver no link')}

🔗 Link: {demanda['link']}
"""
        else:
            titulo = demanda['cliente']
            descricao = f"""
📝 DEMANDA:
{demanda.get('titulo', 'Ver no link')}

💬 COPY:
{demanda.get('copy', 'Ver no link')}

🔗 ORIGEM:
{demanda['link']}

⏰ Prazo: 17:30
"""
        
        print(f"📝 Criando card: {titulo}")
        card = trello.create_card(lista['id'], titulo, descricao)
        
        if card:
            print(f"✅ Card criado com sucesso!")
            return True, card.get('shortUrl', 'https://trello.com')
        else:
            return False, "Erro ao criar card"
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False, str(e)

def main():
    print("=" * 60)
    print("🤖 KAREN BOT - VERSÃO LIMPA")
    print("=" * 60)
    print(f"⏰ {get_now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("demandas", ver_demandas))
    app.add_handler(CommandHandler("quadros", listar_quadros))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ BOT ONLINE!")
    print("=" * 60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
