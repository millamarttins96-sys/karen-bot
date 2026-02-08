"""
Bot de Gerenciamento de Demandas - Etapa 1
Notificações e Distribuição Básica
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta
import asyncio

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Credenciais
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')

# Importar módulos de monitoramento
try:
    from etapa1.monitors.notion_monitor import NotionMonitor
    from etapa1.monitors.trello_monitor import TrelloMonitor
    from etapa1.handlers.distribution_handler import DistributionHandler
    from etapa1.handlers.week_manager import WeekManager
except ImportError:
    from monitors.notion_monitor import NotionMonitor
    from monitors.trello_monitor import TrelloMonitor
    from handlers.distribution_handler import DistributionHandler
    from handlers.week_manager import WeekManager


class MillaDesignBot:
    """Classe principal do bot"""
    
    def __init__(self):
        self.app = None
        self.notion_monitor = NotionMonitor()
        self.trello_monitor = TrelloMonitor()
        self.distribution_handler = DistributionHandler()
        self.week_manager = WeekManager()
        self.pending_distributions = {}  # Armazenar distribuições em andamento
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_text = """
🎨 **Bem-vinda ao Milla Design Bot!**

Sou seu assistente de gerenciamento de demandas 24/7.

**Funcionalidades disponíveis:**
• 🔔 Notificações automáticas de novas demandas
• 📊 Distribuição inteligente para sua equipe
• 📅 Gerenciamento de semanas automático
• 🔄 Detecção de alterações

**Comandos rápidos:**
/resumo - Status geral
/hoje - Demandas de hoje
/semana - Visão da semana
/ajuda - Ver todos os comandos

Estou monitorando Notion, Trello e Drive continuamente! ✨
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        
    async def resumo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /resumo - Status geral"""
        try:
            status = await self.get_status()
            await update.message.reply_text(status, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            await update.message.reply_text("❌ Erro ao gerar resumo. Tente novamente.")
            
    async def hoje(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /hoje - Demandas de hoje"""
        try:
            today_demands = await self.get_today_demands()
            await update.message.reply_text(today_demands, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Erro ao buscar demandas de hoje: {e}")
            await update.message.reply_text("❌ Erro ao buscar demandas.")
            
    async def semana(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /semana - Visão da semana"""
        try:
            week_view = await self.get_week_view()
            await update.message.reply_text(week_view, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Erro ao buscar visão da semana: {e}")
            await update.message.reply_text("❌ Erro ao buscar visão da semana.")
            
    async def ajuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ajuda - Ver todos os comandos"""
        help_text = """
📚 **Comandos Disponíveis**

**Status e Informações:**
/resumo - Status geral de tudo
/pendentes - O que ainda falta fazer
/hoje - Demandas de hoje
/semana - Visão da semana

**Equipe:**
/clarysse - Status Designer Clarysse
/larissa - Status Designer Larissa
/bruno - Status Editor Bruno

**Gerenciamento:**
/add_cliente [nome] - Adicionar cliente para monitorar
/remove_cliente [nome] - Remover cliente
/virar_semana - Atualizar datas (manual)
/folga [nome] [data] - Marcar folga

**Geral:**
/start - Mensagem de boas-vindas
/ajuda - Este menu
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def handle_new_demand(self, demand_data: dict):
        """Lidar com nova demanda detectada"""
        try:
            # Criar mensagem com botões de distribuição
            message_text = self._format_demand_message(demand_data)
            
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
            
            # Enviar para o chat do usuário
            await self.app.bot.send_message(
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Nova demanda notificada: {demand_data['id']}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar nova demanda: {e}")
            
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lidar com cliques nos botões"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("dist_"):
            await self.handle_distribution_button(query, data)
            
    async def handle_distribution_button(self, query, data: str):
        """Lidar com botões de distribuição"""
        parts = data.split("_")
        action = parts[1]
        demand_id = "_".join(parts[2:])
        
        if action == "design":
            # Perguntar para qual designer
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
            # Perguntar para Bruno
            keyboard = [
                [InlineKeyboardButton("🎥 Bruno", callback_data=f"designer_bruno_{demand_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Para qual editor?",
                reply_markup=reply_markup
            )
            
        elif action == "me":
            # Perguntar qual dia da semana
            await self.ask_for_day(query, demand_id)
            
        elif action == "ignore":
            await query.edit_message_text(text="✅ Demanda ignorada.")
            
    async def ask_for_day(self, query, demand_id: str):
        """Perguntar qual dia da semana"""
        # Calcular semana atual
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        days = []
        day_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        
        for i in range(5):
            day = week_start + timedelta(days=i)
            day_str = f"{day_names[i]} {day.strftime('%d/%m')}"
            days.append(day)
            
        keyboard = [
            [InlineKeyboardButton(f"📅 {day_names[i]} {days[i].strftime('%d/%m')}", 
                                callback_data=f"day_{i}_{demand_id}")]
            for i in range(5)
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Para qual dia desta semana?",
            reply_markup=reply_markup
        )
        
    async def get_status(self) -> str:
        """Obter status geral"""
        status_text = """
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
        return status_text
        
    async def get_today_demands(self) -> str:
        """Obter demandas de hoje"""
        return "📅 **DEMANDAS DE HOJE**\n\nNenhuma demanda para hoje."
        
    async def get_week_view(self) -> str:
        """Obter visão da semana"""
        return "📅 **VISÃO DA SEMANA**\n\nNenhuma demanda esta semana."
        
    def _format_demand_message(self, demand_data: dict) -> str:
        """Formatar mensagem de demanda"""
        return f"""
🔔 **Nova Demanda!**

👤 **Cliente:** {demand_data.get('client', 'N/A')}
📝 **Demanda:** {demand_data.get('title', 'N/A')}

💬 **Copy completa:**
{demand_data.get('copy', 'N/A')}

🔗 **Link:** [Abrir]({demand_data.get('link', '#')})
        """
        
    async def start_monitoring(self):
        """Iniciar monitoramento contínuo"""
        logger.info("Iniciando monitoramento...")
        
        # Iniciar monitoramento do Notion
        asyncio.create_task(self.notion_monitor.start_monitoring(self))
        
        # Iniciar monitoramento do Trello
        asyncio.create_task(self.trello_monitor.start_monitoring(self))
        
    def run(self):
        """Executar o bot"""
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Adicionar handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("resumo", self.resumo))
        self.app.add_handler(CommandHandler("hoje", self.hoje))
        self.app.add_handler(CommandHandler("semana", self.semana))
        self.app.add_handler(CommandHandler("ajuda", self.ajuda))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Bot iniciado com sucesso!")
        self.app.run_polling()


if __name__ == "__main__":
    bot = MillaDesignBot()
    bot.run()
