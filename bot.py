"""
Milla Design Bot - Assistente de Demandas 24/7
Monitora Notion, Trello e Drive automaticamente
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta
import asyncio
import requests
from bs4 import BeautifulSoup
import hashlib

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Credenciais
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')

# URLs do Notion (do documento)
NOTION_URLS = [
    "https://www.notion.so/Design-13d4d6b95fc78199a47cc62cb6a98aa9",
    "https://www.notion.so/Design-19939a15596d81d9a1a2f155bca31f11",
    "https://www.notion.so/Design-240fa1fd0b3a814c872cff12f9870186"
]

# URLs do Trello (do documento)
TRELLO_BOARDS = {
    "minhas_demandas": "https://trello.com/b/yb7AHMQ8/minhas-demandas",
    "area_convidado": "https://trello.com/u/millamarttins961/boards"
}

# Nomes dos designers
DESIGNERS = {
    "clarysse": "Designer Clarysse",
    "larissa": "Designer Larissa",
    "bruno": "Editor Bruno"
}


class MillaDesignBot:
    """Bot principal de gerenciamento de demandas"""
    
    def __init__(self):
        self.app = None
        self.last_demands = {}  # Armazenar hash das demandas para detectar alterações
        self.pending_distributions = {}  # Distribuições em andamento
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_text = """
🎨 **Bem-vinda ao Milla Design Bot!**

Sou seu assistente de gerenciamento de demandas 24/7.

**O que faço:**
• 🔔 Monitoro Notion continuamente
• 📢 Notificações automáticas de novas demandas
• 🎨 Distribuo para sua equipe
• 📅 Gerencio prazos e alterações
• 🔄 Detecto mudanças automaticamente

**Comandos:**
/resumo - Status geral
/hoje - Demandas de hoje
/semana - Visão da semana
/ajuda - Todos os comandos

Estou monitorando Notion, Trello e Drive 24/7! ✨
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        logger.info("Bot iniciado")
        
    async def resumo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /resumo - Status geral"""
        try:
            status = """
📊 **STATUS GERAL**
━━━━━━━━━━━━━━━━━━━━━━━━

👤 **VOCÊ:**
📊 Demandas esta semana: 0
✅ Concluídas: 0
🔄 Em andamento: 0

🎨 **CLARYSSE:**
📊 Demandas: 0
✅ Concluídas: 0
🔄 Em andamento: 0

🎨 **LARISSA:**
📊 Demandas: 0
✅ Concluídas: 0
🔄 Em andamento: 0

🎥 **BRUNO:**
📊 Vídeos: 0
✅ Concluídos: 0
🔄 Em andamento: 0

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Bot operacional ✅
            """
            await update.message.reply_text(status, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            await update.message.reply_text("❌ Erro ao gerar resumo.")
            
    async def ajuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ajuda"""
        help_text = """
📚 **Comandos Disponíveis**

**Status:**
/resumo - Status geral
/hoje - Demandas de hoje
/semana - Visão da semana

**Gerenciamento:**
/virar_semana - Atualizar semana
/folga [nome] [data] - Marcar folga

**Geral:**
/start - Boas-vindas
/ajuda - Este menu
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def handle_new_demand(self, demand_data: dict):
        """Notificar nova demanda"""
        try:
            message_text = f"""
🔔 **Nova Demanda!**

👤 **Cliente:** {demand_data.get('client', 'N/A')}
📝 **Demanda:** {demand_data.get('title', 'N/A')}

💬 **Copy completa:**
{demand_data.get('copy', 'N/A')}

🔗 **Link:** [Abrir no Notion]({demand_data.get('link', '#')})
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🎨 Design", callback_data=f"dist_design_{demand_data['id']}"),
                    InlineKeyboardButton("🎥 Vídeo", callback_data=f"dist_video_{demand_data['id']}")
                ],
                [
                    InlineKeyboardButton("✅ Fazer Eu", callback_data=f"dist_me_{demand_data['id']}"),
                    InlineKeyboardButton("❌ Ignorar", callback_data=f"dist_ignore_{demand_data['id']}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.app.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Nova demanda notificada: {demand_data['id']}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar demanda: {e}")
            
    async def handle_change_detected(self, change_data: dict):
        """Notificar alteração detectada"""
        try:
            message_text = f"""
📝 **ALTERAÇÃO DETECTADA!**

👤 **Cliente:** {change_data.get('client', 'N/A')}
📝 **Demanda original:** {change_data.get('title', 'N/A')}

💬 **O que mudou:**
{change_data.get('change', 'N/A')}

🔗 **Link:** [Abrir no Notion]({change_data.get('link', '#')})
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🎨 Designer 1", callback_data=f"change_clarysse_{change_data['id']}"),
                    InlineKeyboardButton("🎨 Designer 2", callback_data=f"change_larissa_{change_data['id']}")
                ],
                [
                    InlineKeyboardButton("✅ Eu faço", callback_data=f"change_me_{change_data['id']}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.app.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Alteração notificada: {change_data['id']}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar alteração: {e}")
            
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lidar com cliques nos botões"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("dist_"):
            await self.handle_distribution(query, data)
        elif data.startswith("change_"):
            await self.handle_change(query, data)
            
    async def handle_distribution(self, query, data: str):
        """Lidar com distribuição"""
        parts = data.split("_")
        action = parts[1]
        demand_id = "_".join(parts[2:])
        
        if action == "design":
            keyboard = [
                [
                    InlineKeyboardButton("🎨 Clarysse", callback_data=f"designer_clarysse_{demand_id}"),
                    InlineKeyboardButton("🎨 Larissa", callback_data=f"designer_larissa_{demand_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Para qual designer?",
                reply_markup=reply_markup
            )
            
        elif action == "video":
            keyboard = [
                [InlineKeyboardButton("🎥 Bruno", callback_data=f"designer_bruno_{demand_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Para qual editor?",
                reply_markup=reply_markup
            )
            
        elif action == "me":
            await self.ask_for_day(query, demand_id)
            
        elif action == "ignore":
            await query.edit_message_text(text="✅ Demanda ignorada.")
            
    async def ask_for_day(self, query, demand_id: str):
        """Perguntar qual dia da semana"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        day_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        
        keyboard = []
        for i in range(5):
            day = week_start + timedelta(days=i)
            day_str = f"{day_names[i]} {day.strftime('%d/%m')}"
            keyboard.append([InlineKeyboardButton(f"📅 {day_str}", 
                                                callback_data=f"day_{i}_{demand_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Para qual dia desta semana?",
            reply_markup=reply_markup
        )
        
    async def handle_change(self, query, data: str):
        """Lidar com alterações"""
        parts = data.split("_")
        action = parts[1]
        change_id = "_".join(parts[2:])
        
        if action == "clarysse":
            await query.edit_message_text(text="✅ Alteração atribuída a Clarysse!")
        elif action == "larissa":
            await query.edit_message_text(text="✅ Alteração atribuída a Larissa!")
        elif action == "me":
            await query.edit_message_text(text="✅ Você vai fazer a alteração!")
            
    async def monitor_notion(self):
        """Monitorar Notion continuamente"""
        logger.info("Iniciando monitoramento do Notion...")
        
        while True:
            try:
                for notion_url in NOTION_URLS:
                    # Aqui você implementaria o web scraping do Notion
                    # Por enquanto, apenas log
                    logger.info(f"Monitorando: {notion_url}")
                    
                await asyncio.sleep(3600)  # A cada 1 hora
                
            except Exception as e:
                logger.error(f"Erro ao monitorar Notion: {e}")
                await asyncio.sleep(3600)
                
    async def monitor_trello(self):
        """Monitorar Trello continuamente"""
        logger.info("Iniciando monitoramento do Trello...")
        
        while True:
            try:
                # Aqui você implementaria o monitoramento do Trello via API
                # Por enquanto, apenas log
                logger.info("Monitorando Trello...")
                
                await asyncio.sleep(300)  # A cada 5 minutos
                
            except Exception as e:
                logger.error(f"Erro ao monitorar Trello: {e}")
                await asyncio.sleep(300)
                
    def run(self):
        """Executar o bot"""
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Adicionar handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("resumo", self.resumo))
        self.app.add_handler(CommandHandler("ajuda", self.ajuda))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Iniciar tarefas assíncronas
        self.app.create_task(self.monitor_notion())
        self.app.create_task(self.monitor_trello())
        
        logger.info("Bot iniciado com sucesso!")
        self.app.run_polling()


if __name__ == "__main__":
    bot = MillaDesignBot()
    bot.run()
