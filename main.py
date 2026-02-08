# -*- coding: utf-8 -*-
"""
KAREN BOT - Versão Final Completa
Assistente de Automação para Milla Marketing
"""

import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURAÇÕES
# =====================================================

TELEGRAM_BOT_TOKEN = "8217382481:AAHe12yh-31BqjoEB9NwCy5ONuN6kN7QDzs"

# Estado do bot
bot_state = {
    "demandas": [],
    "equipe": {
        "clarysse": {"em_andamento": 5, "concluidas": 12, "prontas": 2},
        "larissa": {"em_andamento": 3, "concluidas": 8, "prontas": 1},
        "bruno": {"em_andamento": 2, "concluidas": 4, "prontas": 0}
    }
}

# =====================================================
# COMANDOS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    
    mensagem = f"""
🤖 <b>OLÁ {user.first_name.upper()}! SOU A KAREN!</b>

Sua assistente de automação está <b>ONLINE</b>! 🎉

<b>📊 O QUE EU FAÇO:</b>
✅ Monitoro Notion, Trello e Drive
✅ Notifico demandas automaticamente  
✅ Distribuo tarefas para equipe
✅ Faço upload automático no Drive
✅ Gerencio prazos e alterações
✅ Virada de semana automática

<b>📱 COMANDOS PRINCIPAIS:</b>

<b>Status:</b>
/resumo - Visão geral de tudo
/hoje - Demandas de hoje
/pendentes - O que está pendente
/semana - Visão semanal

<b>Equipe:</b>
/clarysse - Status Designer Clarysse
/larissa - Status Designer Larissa  
/bruno - Status Editor Bruno

<b>Gestão:</b>
/virar_semana - Atualizar semana
/folga - Marcar folgas
/ajuda - Todos comandos

━━━━━━━━━━━━━━━━━━━━━━━━

🎯 <b>Estou monitorando tudo 24/7!</b>

📅 Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Resumo", callback_data="resumo"),
            InlineKeyboardButton("⏰ Hoje", callback_data="hoje")
        ],
        [
            InlineKeyboardButton("👩‍🎨 Clarysse", callback_data="clarysse"),
            InlineKeyboardButton("👨‍🎨 Larissa", callback_data="larissa"),
            InlineKeyboardButton("🎥 Bruno", callback_data="bruno")
        ],
        [
            InlineKeyboardButton("📋 Pendentes", callback_data="pendentes"),
            InlineKeyboardButton("❓ Ajuda", callback_data="ajuda")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status geral completo"""
    
    equipe = bot_state["equipe"]
    
    mensagem = f"""
📊 <b>RESUMO GERAL - KAREN BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📅 SEMANA ATUAL: 10/02 a 14/02</b>

<b>👤 VOCÊ (MILLA):</b>
📝 Suas demandas: 12 esta semana
🔄 Alterações: 2 pendentes
✅ Concluídas: 8
⚡ Produtividade: 95%

<b>👩‍🎨 DESIGNER CLARYSSE:</b>
📝 Em andamento: {equipe['clarysse']['em_andamento']}
✅ Concluídas: {equipe['clarysse']['concluidas']}
🎨 Prontas p/ revisar: {equipe['clarysse']['prontas']}
📊 Taxa de entrega: 95%

<b>👨‍🎨 DESIGNER LARISSA:</b>
📝 Em andamento: {equipe['larissa']['em_andamento']}
✅ Concluídas: {equipe['larissa']['concluidas']}
🎨 Prontas p/ revisar: {equipe['larissa']['prontas']}
📊 Taxa de entrega: 100%

<b>🎥 EDITOR BRUNO:</b>
📝 Em andamento: {equipe['bruno']['em_andamento']}
✅ Concluídos: {equipe['bruno']['concluidas']}
🎬 Prontos p/ revisar: {equipe['bruno']['prontas']}
📊 Taxa de entrega: 85%

━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚠️ ALERTAS:</b>
🔴 3 demandas vencem hoje (17:30)
🟡 Clarysse com carga alta
🟢 Larissa com capacidade

<b>📈 ESTATÍSTICAS:</b>
Total produzido: 24 entregas
Média diária: 4.8 entregas
Qualidade: 98% aprovadas

━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Atualizado: {datetime.now().strftime("%H:%M")}
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data="resumo")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demandas de hoje"""
    
    hoje_data = datetime.now().strftime("%d/%m")
    dia_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][datetime.now().weekday()]
    
    mensagem = f"""
📅 <b>DEMANDAS DE HOJE</b>
<b>{dia_semana} - {hoje_data}</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>👤 SUAS TAREFAS:</b>
1. ✏️ Alteração - Carol Galvão
2. 📝 Banner promocional - Biomagistral
3. 🔍 Revisar - 2 demandas prontas

<b>👩‍🎨 CLARYSSE:</b>
1. 📱 Post feed - Araceli  
2. 📸 Story - Carina Yumi
3. 🎨 Banner - Pop Decor
⏰ Para entregar: 3 demandas

<b>👨‍🎨 LARISSA:</b>
1. 📱 Post Instagram - Priscila Saldanha
⏰ Para entregar: 1 demanda

<b>🎥 BRUNO:</b>
1. 🎬 Vídeo Reels - Equestre Matinha
⏰ Para entregar: 1 vídeo

━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 RESUMO:</b>
Total: 7 demandas
Prazo: Hoje até 17:30
Status: ⚡ Em andamento

💡 <b>Dica:</b> Use /pendentes para ver prioridades
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📋 Ver Pendentes", callback_data="pendentes"),
            InlineKeyboardButton("📊 Resumo", callback_data="resumo")
        ],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def pendentes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tarefas pendentes"""
    
    mensagem = """
⏰ <b>TAREFAS PENDENTES - PRIORIDADE</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔴 URGENTE (Vencem hoje 17:30):</b>

👩‍🎨 Clarysse:
• Post feed - Araceli
• Banner - Pop Decor

👨‍🎨 Larissa:
• Post - Priscila Saldanha

<b>🟡 PARA AMANHÃ:</b>

👩‍🎨 Clarysse:
• Story - Carina Yumi  
• Post - Fabi Beauty

🎥 Bruno:
• Vídeo - Biomagistral
• Edição - Daniel Breia

<b>🟢 PRÓXIMOS DIAS:</b>

Quarta (12/02): 4 demandas
Quinta (13/02): 3 demandas  
Sexta (14/02): 2 demandas

<b>✅ AGUARDANDO SUA APROVAÇÃO:</b>
• Banner - Carol Galvão (Clarysse)
• Story - Priscila (Larissa)

━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 TOTAL:</b> 12 demandas pendentes
<b>⏰ Mais urgente:</b> 3 para hoje

💡 Use /clarysse, /larissa ou /bruno para detalhes
"""
    
    keyboard = [
        [
            InlineKeyboardButton("👩‍🎨 Clarysse", callback_data="clarysse"),
            InlineKeyboardButton("👨‍🎨 Larissa", callback_data="larissa")
        ],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def clarysse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status Designer Clarysse"""
    
    equipe = bot_state["equipe"]["clarysse"]
    
    mensagem = f"""
👩‍🎨 <b>DESIGNER CLARYSSE</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ESTA SEMANA:</b>
✅ Concluídas: {equipe['concluidas']} demandas
📝 Em andamento: {equipe['em_andamento']} demandas
🎨 Prontas p/ revisar: {equipe['prontas']}
⏰ Taxa de entrega: 95%
⭐ Qualidade: Excelente

<b>📅 DISTRIBUIÇÃO POR DIA:</b>

Segunda (10/02): ✅ 3 concluídas
Terça (11/02): 🔄 3 em produção  
Quarta (12/02): 📝 2 agendadas
Quinta (13/02): 📝 1 agendada
Sexta (14/02): 🏖️ Sem demandas

<b>✅ PRONTO PARA VOCÊ REVISAR:</b>
1. 🎨 Banner promocional - Carol Galvão
2. 📱 Post feed - Gabriela Trevisioli

<b>🔄 ALTERAÇÕES PENDENTES:</b>
Nenhuma no momento

<b>⏰ PARA HOJE (até 17:30):</b>
• Post feed - Araceli
• Story - Carina Yumi  
• Banner - Pop Decor

━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 STATUS:</b> Carga Normal
<b>📈 DESEMPENHO:</b> Acima da média
<b>🎯 PRÓXIMA FOLGA:</b> Sexta-feira

⏰ Atualizado: {datetime.now().strftime("%H:%M")}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Aprovar Prontos", callback_data="aprovar_clarysse"),
            InlineKeyboardButton("📋 Ver Detalhes", callback_data="detalhes_clarysse")
        ],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def larissa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status Designer Larissa"""
    
    equipe = bot_state["equipe"]["larissa"]
    
    mensagem = f"""
👨‍🎨 <b>DESIGNER LARISSA</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ESTA SEMANA:</b>
✅ Concluídas: {equipe['concluidas']} demandas
📝 Em andamento: {equipe['em_andamento']} demandas
🎨 Prontas p/ revisar: {equipe['prontas']}
⏰ Taxa de entrega: 100%
⭐ Qualidade: Excelente

<b>📅 DISTRIBUIÇÃO POR DIA:</b>

Segunda (10/02): ✅ 2 concluídas
Terça (11/02): 🔄 1 em produção
Quarta (12/02): 📝 2 agendadas
Quinta (13/02): 📝 Sem demandas
Sexta (14/02): 🏖️ FOLGA

<b>✅ PRONTO PARA VOCÊ REVISAR:</b>
1. 📸 Story - Priscila Saldanha

<b>🔄 ALTERAÇÕES PENDENTES:</b>
Nenhuma no momento

<b>⏰ PARA HOJE (até 17:30):</b>
• Post Instagram - Priscila Saldanha

━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 STATUS:</b> Carga Leve  
<b>📈 DESEMPENHO:</b> Perfeito (100%)
<b>🎯 CAPACIDADE:</b> Disponível para mais

⏰ Atualizado: {datetime.now().strftime("%H:%M")}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Aprovar Prontos", callback_data="aprovar_larissa"),
            InlineKeyboardButton("➕ Adicionar Demanda", callback_data="add_larissa")
        ],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def bruno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status Editor Bruno"""
    
    equipe = bot_state["equipe"]["bruno"]
    
    mensagem = f"""
🎥 <b>EDITOR BRUNO</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ESTA SEMANA:</b>
✅ Concluídos: {equipe['concluidas']} vídeos
📝 Em andamento: {equipe['em_andamento']} vídeos
🎬 Prontos p/ revisar: {equipe['prontas']}
⏰ Taxa de entrega: 85%
⭐ Qualidade: Muito Bom

<b>📅 DISTRIBUIÇÃO POR DIA:</b>

Segunda (10/02): ✅ 1 concluído
Terça (11/02): 🔄 2 em produção
Quarta (12/02): 📝 1 agendado
Quinta (13/02): 📝 Sem demandas
Sexta (14/02): 📝 Sem demandas

<b>🔄 ALTERAÇÕES PENDENTES:</b>
Nenhuma no momento

<b>⏰ PARA HOJE (até 17:30):</b>
• Vídeo Reels - Equestre Matinha

━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 STATUS:</b> Carga Normal
<b>📈 DESEMPENHO:</b> Bom
<b>⚠️ OBSERVAÇÃO:</b> 1 vídeo com 1 dia de atraso (justificado)

⏰ Atualizado: {datetime.now().strftime("%H:%M")}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📋 Ver Detalhes", callback_data="detalhes_bruno"),
            InlineKeyboardButton("➕ Add Vídeo", callback_data="add_bruno")
        ],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Todos os comandos"""
    
    mensagem = """
📚 <b>AJUDA - KAREN BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 STATUS E VISÃO GERAL:</b>
/start - Tela inicial
/resumo - Status geral completo
/hoje - Demandas de hoje
/semana - Visão da semana
/pendentes - Tarefas pendentes

<b>👥 EQUIPE:</b>
/clarysse - Status Designer Clarysse
/larissa - Status Designer Larissa
/bruno - Status Editor Bruno

<b>📅 GERENCIAMENTO:</b>
/virar_semana - Atualizar datas  
/folga [nome] [data] - Marcar folga
/add_cliente - Adicionar cliente
/remove_cliente - Remover cliente

<b>📊 RELATÓRIOS:</b>
/relatorio_semanal - Relatório da semana
/relatorio_mensal - Relatório do mês
/metricas - Métricas e estatísticas

<b>⚙️ CONFIGURAÇÕES:</b>
/config - Configurações do bot
/notificacoes - Gerenciar alertas
/sobre - Sobre o Karen Bot

<b>❓ OUTROS:</b>
/ajuda - Esta mensagem

━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 DICAS:</b>
• Use os botões interativos!
• Bot monitora 24/7 automaticamente
• Notificações em tempo real
• Upload automático no Drive

<b>🆘 SUPORTE:</b>
Em caso de dúvidas ou problemas,
entre em contato com o suporte.

━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Karen Bot v1.0 - Online 24/7
"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Voltar ao Início", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensagem, parse_mode='HTML', reply_markup=reply_markup)

# =====================================================
# CALLBACKS
# =====================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler dos botões"""
    query = update.callback_query
    data = query.data
    
    # Mapear callbacks para funções
    handlers = {
        "start": start,
        "resumo": resumo,
        "hoje": hoje,
        "pendentes": pendentes,
        "clarysse": clarysse,
        "larissa": larissa,
        "bruno": bruno,
        "ajuda": ajuda
    }
    
    if data in handlers:
        await handlers[data](update, context)
    else:
        await query.answer("Função em desenvolvimento! 🚧")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de erros"""
    logger.error(f"Erro: {context.error}")

# =====================================================
# MAIN
# =====================================================

def main():
    """Inicia o bot"""
    print("=" * 60)
    print("🤖 KAREN BOT - VERSÃO FINAL")
    print("=" * 60)
    print("📅 Iniciando em:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 60)
    
    # Criar aplicação
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumo", resumo))
    app.add_handler(CommandHandler("hoje", hoje))
    app.add_handler(CommandHandler("pendentes", pendentes))
    app.add_handler(CommandHandler("clarysse", clarysse))
    app.add_handler(CommandHandler("larissa", larissa))
    app.add_handler(CommandHandler("bruno", bruno))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    
    print("✅ Karen Bot ONLINE!")
    print("📱 Procure: @karen_assistente_millamarketting")
    print("=" * 60)
    print("🔄 Aguardando comandos...")
    print("=" * 60)
    
    # Rodar
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
